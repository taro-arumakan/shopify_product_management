import os
from brands.rohseoul.client import RohseoulClient
from brands.rohseoul.article_templates import article_template_campaign

theme_dir = "/Users/taro/sc/rohseoul/"
theme_name = "prod"

article_title = "Campaign - 26 Summer"
campaign_title = "CAMPAIGN - SUMMER 26"
campaign_subtitle = "Soft Pause: Where Summer Gently Settles"
campaign_description = r"""ROH SEOULのSUMMER 26コレクションは、“とどまる時間”から始まります。やわらかな陽光が均一に差し込む空間、開かれた窓からゆっくりと行き交う空気。時間は特定の方向を持たず、静かに流れていきます。過度な動きのないひとときの中で、休息は自然と深まり、感覚は穏やかに整えられていく。SUMMER 26はその静かな余白に寄り添い、次へと続く旅のための新たな余白をそっと残します。""".replace(
    "\n", "<br/>"
)

thumbnail_image_file_name = "26_SUMMER_CP_cover.jpg"
campaign_images_dir = "/Users/taro/Downloads/CAMPAIGN - Summer 26"


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
