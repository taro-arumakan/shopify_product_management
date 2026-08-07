"""
Expects all relevant image files uploaded already.
Download the images dir from Google Drive.
Rename files as required (in the format 26_report_CP_1.jpg).
Upload the files, then run the script.
"""

import os
from brands.rohseoul.client import RohseoulClient
from brands.rohseoul.article_templates import article_template_campaign

season = "Pre-Fall 26"
article_title = "Campaign - 26 Pre-Fall"
campaign_title = f"CAMPAIGN - {season.upper()}"
campaign_subtitle = "Measured Light : Where Form Emerges"
campaign_description = r"""ROH SEOULのPRE-FALL 26コレクションは、光がかたちを映し出す、その一瞬から始まります。
余白に静かに差し込む光は、線と面を鮮やかに浮かび上がらせ、視界には研ぎ澄まされたフォルムだけが穏やかに映し出されます。そうして感覚は、よりシンプルに、より明晰に研ぎ澄まされていきます。
PRE-FALL 26では、抑制された構造の上に光が宿ることで初めて現れる、フォルムの繊細なニュアンスを表現しました。""".replace(
    "\n", "<br/>"
)

thumbnail_image_file_name = f"CAMPAIGN - {season.upper()}_COVER IMAGE.jpg"
campaign_images_dir = f"/Users/taro/Downloads/CAMPAIGN - {season.upper()}"

blog_title = "Lookbook"


def main():
    client = RohseoulClient()

    template_json = article_template_campaign()
    template_json = template_json.replace("${CAMPAIGN_TITLE}", campaign_title)
    template_json = template_json.replace("${CAMPAIGN_SUBTITLE}", campaign_subtitle)
    template_json = template_json.replace(
        "${CAMPAIGN_DESCRIPTION}", campaign_description
    )

    file_names = sorted(
        (p for p in os.listdir(campaign_images_dir) if p.endswith(".jpg")),
        key=client.natural_compare,
    )
    file_names = [client.shopify_sanitized_filename(fn) for fn in file_names]
    json_contents = client.json_from_image_file_names_and_product_titles(
        image_file_names=file_names, template_json=template_json
    )

    theme = client.current_theme()
    theme_name = theme["name"]
    template_path = f"templates/article.{client.article_template_name(blog_title, article_title)}.json"

    print(f"upsert at {template_path} to {theme_name}")
    client.upsert_theme_file(
        theme["id"],
        template_path,
        json_contents,
    )

    print(f"adding article {article_title} to {theme_name}")
    client.add_article(
        blog_title,
        article_title,
        thumbnail_image_name=client.shopify_sanitized_filename(
            thumbnail_image_file_name
        ),
        theme_name=theme_name,
    )


if __name__ == "__main__":
    main()
