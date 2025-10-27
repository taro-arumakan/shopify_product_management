import copy
import json
import logging
import os
import string
import time
from helpers.shopify_graphql_client.images_list_template import images_list_template

logger = logging.getLogger(__name__)

additional_punctuation_chars = "‘’“” "
punctuation_chrs = (
    "".join([s for s in string.punctuation if s not in ["-"]])
    + additional_punctuation_chars
)
punctuation_translator = str.maketrans({s: "_" for s in punctuation_chrs})


class Article:
    def shopify_compatible_name(self, name):
        name = self.punctuations_to_underscore(name)
        if name.startswith("_"):
            name = name[1:]
        return name

    def punctuations_to_underscore(self, s):
        parts = s.lower().split(" ")
        parts = [part.translate(punctuation_translator) for part in parts]
        return "-".join(parts)

    def blogs_by_query(self, query_string):
        query = """
        query blogsByQuery($query_string: String!) {
            blogs(first: 50, query: $query_string) {
                nodes {
                    id
                    handle
                    title
                    updatedAt
                    commentPolicy
                feed {
                    path
                    location
                }
                    createdAt
                    templateSuffix
                    tags
                }
            }
        }
        """
        variables = {"query_string": query_string}
        res = self.run_query(query, variables)
        return res["blogs"]["nodes"]

    def blog_id_by_blog_title(self, blog_title):
        blogs = self.blogs_by_query(f"title:'{blog_title.replace("'", "\\'")}'")
        if len(blogs) != 1:
            raise RuntimeError(
                f"{'Multiple' if blogs else 'No'} products found for {blog_title}: {blogs}"
            )
        return blogs[0]["id"]

    def articles_by_title(self, title):
        query = """
        query articlesByQuery($query_string: String!) {
            articles(first: 50, query: $query_string) {
                nodes {
                    id
                    handle
                    title
                    image {
                        altText
                        id
                        url
                    }
                    templateSuffix
                }
            }
        }
        """
        variables = {"query_string": f"title:'{title.replace("'", "\\'")}'"}
        res = self.run_query(query, variables)
        return res["articles"]["nodes"]

    def article_create(self, blog_title, title, template_suffix, media_url):
        blog_id = self.blog_id_by_blog_title(blog_title)
        query = """
        mutation CreateArticle($article: ArticleCreateInput!) {
            articleCreate(article: $article) {
                article {
                    id
                    title
                    author {
                        name
                    }
                    handle
                    body
                    summary
                    tags
                    image {
                        altText
                        url
                        id
                    }
                }
                userErrors {
                    code
                    field
                    message
                }
            }
        }
        """
        variables = {
            "article": {
                "blogId": blog_id,
                "title": title,
                "templateSuffix": template_suffix,
                "isPublished": True,
                "author": {"name": "Taro Nakamura"},
                "image": {"url": media_url, "altText": f"{title} cover image"},
            }
        }
        res = self.run_query(query, variables)
        if errors := res["articleCreate"]["userErrors"]:
            raise RuntimeError(f"Failed to create an article: {errors}")
        return res["articleCreate"]["article"]

    def theme_file_by_theme_name_and_file_name(self, theme_name, file_name):
        query = """
            query {
                themes(names:"%s" first:1) {
                    nodes {
                        files(filenames:"*%s*" first:50) {
                            nodes {
                                filename
                            }
                        }
                    }
                }
            }
            """ % (
            theme_name,
            file_name,
        )
        res = self.run_query(query)
        return res["themes"]["nodes"][0]["files"]["nodes"]

    def article_from_image_file_names(
        self,
        theme_dir,
        blog_title,
        article_title,
        thumbnail_image_file_name,
        article_image_file_names,
        theme_name,
        publish_article=True,
    ):
        # for file_name in image_file_names:
        #     self.file_by_file_name(file_name)
        theme_file_path = self.write_json_from_image_file_names(
            theme_dir, blog_title, article_title, article_image_file_names
        )
        if publish_article:
            theme_file_name = theme_file_path.rsplit("templates/", 1)[-1]
            while not self.theme_file_by_theme_name_and_file_name(
                theme_name, theme_file_name
            ):
                logger.info(f"awaiting upload of {theme_file_name}")
                time.sleep(1.5)  # wait for the new json file upload

            self.add_article(
                blog_title,
                article_title,
                thumbnail_image_name=thumbnail_image_file_name,
            )

    def write_json_from_image_file_names(
        self, theme_dir, blog_title, article_title, image_file_names
    ):
        sections = self.to_images_list_sections_dict(image_file_names)
        theme_file_path = os.path.join(
            theme_dir,
            self.article_template_path(theme_dir, blog_title, article_title),
        )
        self.write_to_json(
            theme_file_path=theme_file_path,
            sections_dict=sections,
        )
        return theme_file_path

    def to_images_list_sections_dict(self, file_names):
        base_attrs = {
            "type": "image",
            "settings": {
                "image_link": "",
                "margin_top": 10,
                "margin_bottom": 10,
                "max_width": 600,
                "mobile_max_width": 400,
            },
        }
        sections = {}
        section_count = 0
        for i, filename in enumerate(file_names):
            if i % 10 == 0:
                if section_count:
                    sections.update(section)
                section_count += 1
                section = {
                    f"images_list_{section_count}": {
                        "type": "images-list",
                        "blocks": {},
                        "block_order": [],
                        "name": "t:sections.images_list.presets.images_list.name",
                        "settings": {
                            "color_scheme": "",
                            "image_position": "center",
                            "overlay_color": "#000000",
                            "overlay_opacity": 0,
                        },
                    }
                }

            block_name = f"image_{str(i).zfill(3)}"
            block = {block_name: copy.deepcopy(base_attrs)}
            block[block_name]["settings"]["image"] = f"shopify://shop_images/{filename}"
            section[f"images_list_{section_count}"]["blocks"].update(block)
            section[f"images_list_{section_count}"]["block_order"].append(block_name)
        sections.update(section)
        return sections

    def write_to_json(self, theme_file_path, sections_dict):
        output_dict = json.loads(images_list_template())
        output_dict["sections"].update(sections_dict)
        output_dict["order"] += sections_dict.keys()
        with open(theme_file_path, "w") as of:
            of.write(json.dumps(output_dict, indent=2))

    def add_article(self, blog_title, article_title, thumbnail_image_name):
        template_name = self.article_template_name(blog_title, article_title)
        media = self.file_by_file_name(thumbnail_image_name)
        media_url = media["image"]["url"]
        self.article_create(
            blog_title=blog_title,
            title=article_title,
            template_suffix=template_name,
            media_url=media_url,
        )

    def article_template_path(self, theme_dir, blog_title, article_title):
        return os.path.join(
            theme_dir,
            f"templates/article.{self.article_template_name(blog_title, article_title)}.json",
        )

    def article_template_name(self, blog_title, article_title):
        return f"{blog_title.lower()}-{self.punctuations_to_underscore(article_title)}"
