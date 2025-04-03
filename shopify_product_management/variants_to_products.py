from shopify_product_management import shopify_utils

shop_name = 'kumej'
access_token = 'xzx'

product_title = 'Hooded Quilted Goose Down Jumper'
product_id = shopify_utils.product_id_by_title(shop_name, access_token, product_title)
variants = shopify_utils.product_variants_by_product_id(shop_name, access_token, product_id)

color_options = set([so['value'] for v in variants for so in v['selectedOptions'] if so['name'] == 'カラー'])

include_images = True
new_status = 'DRAFT'

for color_option in color_options:
    res = shopify_utils.duplicate_product(shop_name, access_token, product_id, product_title, include_images, new_status)
    new_product = res['productDuplicate']['newProduct']
    new_product_id = new_product['id']
    color_option_id = [o['id'] for o in new_product['options'] if o['name'] == 'カラー']
    assert len(color_option_id) == 1, f"{'Multiple' if color_option_id else 'No'} option カラー for {new_product_id}"
    color_option_id = color_option_id[0]
    print(f"Duplicated product ID: {new_product_id}")
    new_variants = new_product['variants']['nodes']
    variant_ids_to_keep = [v['id'] for v in new_variants if any(so['name'] == 'カラー' and so['value'] == color_option for so in v['selectedOptions'])]
    variant_ids_to_remove = [v['id'] for v in new_variants if v['id'] not in variant_ids_to_keep]

    all_medias = shopify_utils.medias_by_product_id(shop_name, access_token, new_product_id)
    keep_medias = shopify_utils.medias_by_variant_id(shop_name, access_token, variant_ids_to_keep[0])
    media_ids_to_remove = [m['id'] for m in all_medias if m['id'] not in [km['id'] for km in keep_medias]]
    shopify_utils.remove_product_media_by_product_id(shop_name, access_token, new_product_id, media_ids_to_remove)
    shopify_utils.remove_product_variants(shop_name, access_token, new_product_id, variant_ids_to_remove)
    shopify_utils.delete_product_options(shop_name, access_token, new_product_id, [color_option_id])
