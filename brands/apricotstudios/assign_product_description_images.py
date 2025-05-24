import utils

DUMMY_PRODUCT = "gid://shopify/Product/9081967476992"


def main():
    client = utils.client("apricot-studios")
    anims = ["TOGOM", "TITI", "BAMRONG"]
    paths = [
        "/Users/taro/Downloads/02. Detail/newborn_life_set_product_details_1.jpg",
        "/Users/taro/Downloads/02. Detail/newborn_life_set_product_details_2.jpg",
        "/Users/taro/Downloads/02. Detail/newborn_life_set_product_details_3.jpg",
        "/Users/taro/Downloads/02. Detail/newborn_life_set_product_details_4.jpg",
    ]
    for anim in anims:
        product_title = f"Newborn Comfort Kit - {anim}"
        print(product_title)
        product_id = client.product_id_by_title(product_title)
        print(product_id)
        client.upload_and_assign_description_images_to_shopify(
            product_id,
            paths,
            DUMMY_PRODUCT,
            "https://cdn.shopify.com/s/files/1/0745/9435/3408",
        )


if __name__ == "__main__":
    main()
