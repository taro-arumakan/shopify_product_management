import os
from brands.rohseoul.client import RohseoulClient
from brands.rohseoul.article_templates import article_template_campaign

theme_dir = "/Users/taro/sc/rohseoul/"
theme_name = "trove bag"

article_title = "Campaign - 25 Winter"
campaign_title = "CAMPAIGN - WINTER 25"
campaign_subtitle = "Silent Layer: Where Warmth Meets Still Air"
campaign_description = r"""ROH SEOULの2025年冬コレクションは、凛とした空気にほんのりと溶け込む“静かなぬくもり”から生まれました。
たとえば、木造の別荘で過ごす冬のひととき。

窓の外では森の木々が静かに季節を重ね、その幹には時間の流れが年輪として刻まれていきます。
ROH SEOULは、そんな穏やかな静寂の中にある微かな動きや気配に目を向け、冬という季節の温度や空気感を、かたちあるものとして表現します。

光が最も低く差し込む時間帯——その一瞬の中に潜む“静けさ”と“あたたかさ”を、丁寧にすくい取ったコレクションです。""".replace(
    "\n", "<br/>"
)

thumbnail_image_file_name = "25_Winter_CP_cover.jpg"
campaign_images_dir = (
    "/Users/taro/Downloads/drive-download-20251113T060403Z-1-001/CAMPAIGN - WINTER 25"
)


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
