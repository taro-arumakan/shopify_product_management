import os
from brands.rohseoul.client import RohseoulClient
from brands.rohseoul.article_templates import article_template_campaign

theme_dir = "/Users/taro/sc/rohseoul/"
theme_name = "trove bag"

article_title = "Campaign - 25 Holiday"
campaign_title = "CAMPAIGN - HOLIDAY 25"
campaign_subtitle = "Silent Layer: Where Warmth Meets Still Air"
campaign_description = r"""世界を白く染めた雪は、音さえも静かに包み込みます。
そんな冬の静寂に寄り添うように、ROH SEOULはあたたかな素材と洗練されたデザインを選びました。
雪に残る足跡のように、そっと記憶に残るディテール。
冬という季節の感情を、ひとつひとつのフォルムに落とし込んだコレクションです。""".replace(
    "\n", "<br/>"
)

thumbnail_image_file_name = "25_Holiday_CP_cover.jpg"
campaign_images_dir = "/Users/taro/Downloads/CAMPAIGN - HOLIDAY 25"


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
    client.article_from_image_file_names_and_product_titles(
        theme_dir=theme_dir,
        theme_name=theme_name,
        template_json=template_json,
        blog_title="Lookbook",
        article_title=article_title,
        thumbnail_image_file_name=thumbnail_image_file_name,
        article_image_file_names=file_names,
        publish_article=True,
    )


if __name__ == "__main__":
    main()
