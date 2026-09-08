"""Migrate alvana lookbook Pages to Articles in a 'Lookbook' blog, so publishing a new
season is one action instead of hand-editing the nav, the homepage tile row and
/pages/archives (the source of the 2026 seasons going missing from the archives page).

Per season the migration:
  1. copies the page's section template to an article template (main-page -> main-article,
     plus prev-next-blog-posts so seasons link to each other),
  2. creates the article with that template_suffix, the archives-tile image as its cover,
     and publishedAt backdated so the blog sorts chronologically,
  3. (cutover, opt-in) unpublishes the page and adds a 301 to the article.

Step 3 is separate because a Shopify URL redirect only fires once the old path 404s, so the
page must be unpublished for it to take effect. Verify rendering before cutting over.

Run order per season: main() writes the template -> push it to the live theme -> create the
article. The article render depends on the template already being on the theme.
"""

import datetime
import json
import logging
import os
import re
import subprocess
import time

import utils

logger = logging.getLogger(__name__)

THEME_DIR = "/Users/taro/sc/alvana"
BLOG_TITLE = "Lookbook"
BLOG_HANDLE = "lookbook"
DRY_RUN = True
# theme to push article templates to; None targets the live theme
TARGET_THEME_ID = None

# page handle -> (article title, cover image, publishedAt). The cover is the image already
# used for that season on /pages/archives, so the blog listing keeps the same visual key.
# publishedAt only orders the blog; it is not the real shoot date.
SEASONS = {
    "2024-spring-summer": (
        "2024 Spring & Summer",
        "2024ss_35.jpg",
        "2024-03-01T00:00:00Z",
    ),
    "2024-autumn-winter": (
        "2024 Autumn & Winter",
        "2024aw_3.jpg",
        "2024-09-01T00:00:00Z",
    ),
    "2025-spring-summer": (
        "2025 Spring & Summer",
        "2025ss_64_jpg.webp",
        "2025-03-01T00:00:00Z",
    ),
    "in-bristol": ("Bristol", "in_bristol_25.jpg", "2025-06-01T00:00:00Z"),
    "2025-autumn-winter": (
        "2025 Autumn & Winter",
        "2025aw_23.jpg",
        "2025-09-01T00:00:00Z",
    ),
    "2026-spring-summer": (
        "2026 Spring & Summer",
        "2026ss_36.jpg",
        "2026-03-01T00:00:00Z",
    ),
    "2026-autumn-winter": (
        "2026 Autumn & Winter",
        "2026aw_21.jpg",
        "2026-09-01T00:00:00Z",
    ),
}


def template_suffix(page_template_suffix):
    """article.lookbook-2024ss.json, mirroring the page.2024ss.json naming already in the
    theme. The shared article_template_name() derives from the title instead and yields
    'lookbook-2024-spring-_-summer'."""
    return f"{BLOG_HANDLE}-{page_template_suffix}"


def target_theme(client):
    """The theme article templates are pushed to: TARGET_THEME_ID, else the live theme."""
    if TARGET_THEME_ID:
        q = "query($id: ID!) { theme(id: $id) { id name } }"
        gid = f"gid://shopify/OnlineStoreTheme/{TARGET_THEME_ID}"
        return client.run_query(q, {"id": gid})["theme"]
    q = "query { themes(first: 1, roles: MAIN) { nodes { id name } } }"
    return client.run_query(q)["themes"]["nodes"][0]


def ensure_blog(client):
    blogs = client.blogs_by_query(f"handle:{BLOG_HANDLE}")
    if blogs:
        logger.info(f"blog exists: {blogs[0]['title']} ({blogs[0]['handle']})")
        return blogs[0]
    if DRY_RUN:
        logger.info(f"DRY RUN: would create blog {BLOG_TITLE} / {BLOG_HANDLE}")
        return None
    q = """
    mutation blogCreate($blog: BlogCreateInput!) {
        blogCreate(blog: $blog) {
            blog { id title handle }
            userErrors { field message }
        }
    }
    """
    res = client.run_query(q, {"blog": {"title": BLOG_TITLE, "handle": BLOG_HANDLE}})
    if errors := res["blogCreate"]["userErrors"]:
        raise RuntimeError(f"Failed to create blog: {errors}")
    logger.info(f"created blog {res['blogCreate']['blog']}")
    return res["blogCreate"]["blog"]


# Cover images come in 2:3, 3:4 and 4:5. Nothing in the theme constrains
# .blog-post-card__image and .blog-post-list is align-items:start, so unconstrained cards
# end up different heights with their captions at different levels. 3:4 is the middle of
# the three ratios, so every cover loses at most 11%.
BLOG_CARD_RATIO_CSS = ".blog-post-card__image {aspect-ratio: 3 / 4; object-fit: cover;}"

# prev-next-blog-posts defaults to color scheme "scheme-3", which is background #f3f3f3
# with text_color #ffffff -- a white heading on light grey, i.e. unreadable. It has to be
# set explicitly to scheme-2 (#f3f3f3 background, #5c5c5c text): "" does NOT inherit, it
# means "unset" and Shopify then applies the schema default, which is scheme-3 again.
# scheme-2 matches the body (#f3f3f3) and the images-list text colour (#5c5c5c) so the
# block sits flush with the lookbook above it.
# Excerpt/category are off because these articles carry no body text and every one of them
# has the same "Lookbook" tag; the per-card "Read more" link just repeats the heading.
PREV_NEXT_SETTINGS = {
    "color_scheme": "scheme-2",
    "title": "Other Collections",
    "show_excerpt": False,
    "show_category": False,
    "show_read_more": False,
}

# main-article defaults every one of these to true, which would add a cover-image hero,
# a date/tag line, an author line, share buttons and a sticky share/prev-next toolbar --
# none of which the lookbook pages had. Turned off so the article matches the page.
# content_width mirrors the page's "page_width": "xs".
MAIN_ARTICLE_SETTINGS = {
    "color_scheme": "",
    "content_width": "xs",
    "show_image": False,
    "show_date": False,
    "show_category": False,
    "show_author": False,
    "show_share_buttons": False,
    "show_sticky_bar": False,
}


def strip_json_comments(text):
    return re.sub(r"^/\*.*?\*/\s*", "", text, flags=re.S)


def build_article_template(page_template_suffix):
    """Page template -> article template: keep every content section verbatim (the
    images-list blocks carry the whole lookbook), swap the main section for main-article
    and append prev-next-blog-posts."""
    page_path = os.path.join(THEME_DIR, f"templates/page.{page_template_suffix}.json")
    page = json.loads(strip_json_comments(open(page_path).read()))

    main_section = {"type": "main-article", "settings": dict(MAIN_ARTICLE_SETTINGS)}
    # every lookbook page disables its main-page section, so the page is a bare image
    # gallery with no title block. Carry that state over rather than assuming it, so a
    # page that does show its title produces an article that shows its title too.
    page_main = next(
        (s for s in page["sections"].values() if s["type"] == "main-page"), {}
    )
    if page_main.get("disabled"):
        main_section["disabled"] = True

    sections = {"main": main_section}
    order = ["main"]
    for sid in page["order"]:
        if page["sections"][sid]["type"] == "main-page":
            continue  # replaced by main-article
        sections[sid] = page["sections"][sid]
        order.append(sid)
    sections["prev-next-blog-posts"] = {
        "type": "prev-next-blog-posts",
        "settings": dict(PREV_NEXT_SETTINGS),
        # season covers are a mix of 2:3, 3:4 and 4:5 and nothing in the theme constrains
        # .blog-post-card__image, so side-by-side cards end up different heights
        "custom_css": [BLOG_CARD_RATIO_CSS],
    }
    order.append("prev-next-blog-posts")

    return {"sections": sections, "order": order}


def write_article_template(page_template_suffix):
    suffix = template_suffix(page_template_suffix)
    path = os.path.join(THEME_DIR, f"templates/article.{suffix}.json")
    contents = json.dumps(
        build_article_template(page_template_suffix), indent=2, ensure_ascii=False
    )
    if DRY_RUN:
        logger.info(f"DRY RUN: would write {path} ({len(contents)} bytes)")
        return path, suffix
    with open(path, "w") as f:
        f.write(contents + "\n")
    logger.info(f"wrote {path}")
    return path, suffix


def push_template(path, shop="alvanas"):
    """Additive push of the single new template; touches no existing file. Targets
    TARGET_THEME_ID when set, otherwise the live theme.

    --force matters: `theme push --only <file>` without it runs a "cleaning" step that
    deletes the file from the remote theme while still reporting success."""
    rel = os.path.relpath(path, THEME_DIR)
    target = (
        ["--theme", str(TARGET_THEME_ID)]
        if TARGET_THEME_ID
        else ["--live", "--allow-live"]  # --allow-live is required non-interactively
    )
    cmd = (
        ["shopify", "theme", "push", "--store", shop]
        + target
        + ["--only", rel, "--force"]
    )
    if DRY_RUN:
        logger.info(f"DRY RUN: would run {' '.join(cmd)} (cwd={THEME_DIR})")
        return
    subprocess.run(cmd, cwd=THEME_DIR, check=True)
    logger.info(
        f"pushed {rel} to {'theme ' + str(TARGET_THEME_ID) if TARGET_THEME_ID else 'live theme'}"
    )


def create_article(client, page_handle):
    title, cover_file, published_at = SEASONS[page_handle]
    page = client.run_query(
        "query($q: String!) { pages(first: 1, query: $q) { nodes { id title handle templateSuffix } } }",
        {"q": f"handle:{page_handle}"},
    )["pages"]["nodes"][0]
    suffix = template_suffix(page["templateSuffix"])

    if existing := [
        a for a in client.articles_by_title(title) if a["templateSuffix"] == suffix
    ]:
        logger.info(f"article already exists: {existing[0]['handle']}")
        return existing[0]

    cover_url = client.file_by_file_name(cover_file)["image"]["url"]
    theme_name = target_theme(client)["name"]
    if DRY_RUN:
        logger.info(
            f"DRY RUN: would create article '{title}' suffix={suffix} "
            f"cover={cover_file} publishedAt={published_at}"
        )
        return None

    # the template must be on the theme before the article renders
    file_name = f"article.{suffix}.json"
    for _ in range(60):
        if client.theme_file_by_theme_name_and_file_name(theme_name, file_name):
            break
        logger.info(f"awaiting {file_name} on {theme_name}")
        time.sleep(0.5)
    else:
        raise TimeoutError(f"{file_name} never appeared on theme {theme_name}")

    article = client.article_create(
        blog_title=BLOG_TITLE,
        title=title,
        template_suffix=suffix,
        media_url=cover_url,
        tags=["Lookbook"],
    )
    client.article_update_published_at_by_article_id(
        article["id"], datetime.datetime.fromisoformat(published_at)
    )
    logger.info(f"created article {article['handle']} ({article['id']})")
    return article


def cutover(client, page_handle, article_handle):
    """Unpublish the page and 301 it to the article. Separate from creation: a Shopify
    redirect only fires once the old path 404s. Run after verifying the article renders.
    """
    if DRY_RUN:
        logger.info(
            f"DRY RUN: would unpublish /pages/{page_handle} and redirect it to "
            f"/blogs/{BLOG_HANDLE}/{article_handle}"
        )
        return
    page = client.run_query(
        "query($q: String!) { pages(first: 1, query: $q) { nodes { id } } }",
        {"q": f"handle:{page_handle}"},
    )["pages"]["nodes"][0]
    res = client.run_query(
        """mutation pageUpdate($id: ID!, $page: PageUpdateInput!) {
             pageUpdate(id: $id, page: $page) { page { id handle isPublished }
             userErrors { field message } } }""",
        {"id": page["id"], "page": {"isPublished": False}},
    )
    if errors := res["pageUpdate"]["userErrors"]:
        raise RuntimeError(f"Failed to unpublish page: {errors}")
    logger.info(f"unpublished /pages/{page_handle}")
    client.create_url_redirect(
        f"/pages/{page_handle}", f"/blogs/{BLOG_HANDLE}/{article_handle}"
    )
    logger.info(
        f"redirected /pages/{page_handle} -> /blogs/{BLOG_HANDLE}/{article_handle}"
    )


def migrate(page_handle):
    client = utils.client("alvana")
    ensure_blog(client)
    page = client.run_query(
        "query($q: String!) { pages(first: 1, query: $q) { nodes { templateSuffix } } }",
        {"q": f"handle:{page_handle}"},
    )["pages"]["nodes"][0]
    path, _ = write_article_template(page["templateSuffix"])
    push_template(path)
    return create_article(client, page_handle)


def main():
    logging.basicConfig(level=logging.INFO)
    migrate("2024-spring-summer")


if __name__ == "__main__":
    main()
