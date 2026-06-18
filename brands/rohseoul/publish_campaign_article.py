"""
Expects all relevant image files uploaded already.
Download the images dir from Google Drive.
Rename files as required (in the format 26_report_CP_1.jpg).
Upload the files, then run the script.
"""

import os
from brands.rohseoul.client import RohseoulClient
from brands.rohseoul.article_templates import article_template_campaign

theme_dir = "/Users/taro/sc/rohseoul/"
theme_name = "prod"

article_title = "Campaign - 26 Resort"
campaign_title = "CAMPAIGN - RESORT 26"
campaign_subtitle = "Slow Current : Adrift in Quiet Sunlight"
campaign_description = r"""ROH SEOULのRESORTコレクション26は、流れるような時間の感覚から生まれました。
風を受けながらヨットで海原を進む、そんなひとときを思わせるコレクション。波の揺れに身をゆだね、特別な予定も、急ぐ理由も必要ない——ただそこにある時間が、深い休息になっていく。
眩しい陽射しの下で目を閉じ、ゆっくりと流れる水平線を眺めるように。RESORT 26は、動きの中にも宿る、静かなくつろぎを纏ったコレクションです。""".replace(
    "\n", "<br/>"
)

thumbnail_image_file_name = "CAMPAIGN - RESORT 26_COVER IMAGE.jpg"
campaign_images_dir = "/Users/taro/Downloads/CAMPAIGN - RESORT 26"


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
    client.article_from_image_file_names_and_product_titles(
        theme_dir=theme_dir,
        theme_name=theme_name,
        template_json=template_json,
        blog_title="Lookbook",
        article_title=article_title,
        thumbnail_image_file_name=client.shopify_sanitized_filename(
            thumbnail_image_file_name
        ),
        article_image_file_names=file_names,
        publish_article=True,
    )


if __name__ == "__main__":
    main()
