import json
import logging
import requests
import time

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

def update_product_description(shop_name, access_token, product_id, desc):
    query = """
    mutation updateProductDescription($productSet: ProductSetInput!) {
        productSet(synchronous:true, input: $productSet) {
          product {
            id
            descriptionHtml
          }
          userErrors {
            field
            code
            message
          }
        }
    }
    """
    if product_id.isnumeric():
        product_id = f'gid://shopify/Product/{product_id}'
    variables = {
      "productSet": {
        "id": product_id,
        "descriptionHtml": desc
      }
    }
    response = run_query(shop_name, access_token, query, variables)
    res = response.json()['data']
    if res['productSet']['userErrors']:
        raise RuntimeError(f"Failed to update the description: {res['productSet']['userErrors']}")
    return res

def sanitize_image_name(image_name):
    return image_name.replace(' ', '_').replace('[', '').replace(']', '_').replace('(', '').replace(')', '')

def image_htmlfragment_in_description(image_name, sequence):
    animation_classes = ['reveal_tran_bt', 'reveal_tran_rl', 'reveal_tran_lr', 'reveal_tran_tb']
    animation_class = animation_classes[sequence % 4]
    return f'<p class="{animation_class}"><img src="https://cdn.shopify.com/s/files/1/0745/9435/3408/files/{sanitize_image_name(image_name)}" alt=""></p>'


def upload_and_assign_description_images_to_shopify(shop_name, access_token, product_id, local_paths, dummy_product_id):
    local_paths = [local_path for local_path in local_paths if not local_path.endswith('.psd')]
    mime_types = [f'image/{local_path.rsplit('.', 1)[-1].lower()}' for local_path in local_paths]
    staged_targets = generate_staged_upload_targets(shop_name, access_token, local_paths, mime_types)
    logger.info(f'generated staged upload targets: {len(staged_targets)}')
    upload_images_to_shopify(staged_targets, local_paths, mime_types)
    description = '\n'.join(image_htmlfragment_in_description(local_path.rsplit('/', 1)[-1], i) for i, local_path in enumerate(local_paths))
    assign_images_to_product(shop_name, access_token,
                             [target['resourceUrl'] for target in staged_targets],
                             alts=[local_path.rsplit('/', 1)[-1] for local_path in local_paths],
                             product_id=dummy_product_id)
    return update_product_description(shop_name, access_token, product_id, description)


def update_product_description_and_size_table_html_metafields(shop_name, access_token, product_id, desc, html_text):
    query = """
    mutation updateProductMetafield($productSet: ProductSetInput!) {
        productSet(synchronous:true, input: $productSet) {
          product {
            id
            metafields (first:10) {
              nodes {
                id
                namespace
                key
                value
              }
            }
          }
          userErrors {
            field
            code
            message
          }
        }
    }
    """

    if product_id.isnumeric():
        product_id = f'gid://shopify/Product/{product_id}'
    variables = {
      "productSet": {
        "id": product_id,
        "metafields": [
          {
            "id": "gid://shopify/Metafield/37315032023281",     # product_description
            "namespace": "custom",
            "key": "product_description",
            "type": "rich_text_field",
            "value": json.dumps(desc)
          },
          {
            "id": "gid://shopify/Metafield/30082966716672",     # size_table_html
            "namespace": "custom",
            "key": "size_table_html",
            "type": "multi_line_text_field",
            "value": html_text
          }
        ]
      }
    }

    response = run_query(shop_name, access_token, query, variables)
    res = response.json()['data']
    if res['productSet']['userErrors']:
        raise RuntimeError(f"Failed to update the metafield: {res['productSet']['userErrors']}")
    return res


# TODO: metafield id by namespace and key
def update_product_description_metafield(shop_name, access_token, product_id, desc):
    query = """
    mutation updateProductMetafield($productSet: ProductSetInput!) {
        productSet(synchronous:true, input: $productSet) {
          product {
            id
            metafields (first:10) {
              nodes {
                id
                namespace
                key
                value
              }
            }
          }
          userErrors {
            field
            code
            message
          }
        }
    }
    """

    if product_id.isnumeric():
        product_id = f'gid://shopify/Product/{product_id}'
    variables = {
      "productSet": {
        "id": product_id,
        "metafields": [
          {
            "id": "gid://shopify/Metafield/37315032023281",
            "namespace": "custom",
            "key": "product_description",
            "type": "rich_text_field",
            "value": json.dumps(desc)
          }
        ]
      }
    }

    response = run_query(shop_name, access_token, query, variables)
    res = response.json()['data']
    if res['productSet']['userErrors']:
        raise RuntimeError(f"Failed to update the metafield: {res['productSet']['userErrors']}")
    return res


# TODO: metafield id by namespace and key
def update_size_table_html_metafield(shop_name, access_token, product_id, html_text):
    query = """
    mutation updateProductMetafield($productSet: ProductSetInput!) {
        productSet(synchronous:true, input: $productSet) {
          product {
            id
            metafields (first:10) {
              nodes {
                id
                namespace
                key
                value
              }
            }
          }
          userErrors {
            field
            code
            message
          }
        }
    }
    """

    if product_id.isnumeric():
        product_id = f'gid://shopify/Product/{product_id}'
    variables = {
      "productSet": {
        "id": product_id,
        "metafields": [
          {
            "id": "gid://shopify/Metafield/30082966716672",
            "namespace": "custom",
            "key": "size_table_html",
            "type": "multi_line_text_field",
            "value": html_text
          }
        ]
      }
    }

    response = run_query(shop_name, access_token, query, variables)
    res = response.json()['data']
    if res['productSet']['userErrors']:
        raise RuntimeError(f"Failed to update the metafield: {res['productSet']['userErrors']}")
    return res


def product_description_by_product_id(shop_name, access_token, product_id):
    if isinstance(product_id, int) or product_id.isnumeric():
        product_id = f'gid://shopify/Product/{product_id}'
    query = '''
      query {
        product(id: "%s") {
          id
          descriptionHtml
        }
      }
    ''' % product_id
    response = run_query(shop_name, access_token, query)
    if response.json().get('errors'):
        raise RuntimeError(f"Failed to get the description: {response.json()['errors']}")
    return response.json()['data']['product']['descriptionHtml']


def set_product_description_metafield(shop_name, access_token, product_id, description_rich_text):
    query = '''
    mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
    metafieldsSet(metafields: $metafields) {
        metafields {
        key
        namespace
        value
        }
        userErrors {
        field
        message
        code
        }
    }
    }
    '''

    import json
    description_rich_text = json.dumps(description_rich_text)

    variables = {
        "metafields": [
            {
                "key": "product_description",
                "namespace": "custom",
                "ownerId": f"gid://shopify/Product/{product_id}",
                "value": description_rich_text
            }
        ]
    }
    return run_query(shop_name, access_token, query, variables)


def product_id_by_title(shop_name, access_token, title):
    query = """
    query productsByQuery($query_string: String!) {
      products(first: 10, query: $query_string, sortKey: TITLE) {
        nodes {
          id
          title
        }
      }
    }
    """
    variables = {
        "query_string": f"title:'{title}'"
    }
    response = run_query(shop_name, access_token, query, variables)
    json_data = response.json()

    products = json_data['data']['products']['nodes']
    if len(products) != 1:
        raise Exception(f"Multiple products found for {title}: {products}")
    return products[0]['id']


def product_id_by_handle(shop_name, access_token, handle):
    query = """
    query productsByQuery($query_string: String!) {
      products(first: 10, query: $query_string, sortKey: TITLE) {
        nodes {
          id
          handle
        }
      }
    }
    """
    variables = {
        "query_string": f"handle:'{handle}'"
    }
    response = run_query(shop_name, access_token, query, variables)
    json_data = response.json()

    products = json_data['data']['products']['nodes']
    if len(products) != 1:
        raise Exception(f"Multiple products found for {handle}: {products}")
    return products[0]['id']


def medias_by_product_id(shop_name, access_token, product_id):
    query = """
    query ProductMediaStatusByID($productId: ID!) {
      product(id: $productId) {
        media(first: 100) {
          nodes {
            id
            alt
            ... on MediaImage {
            	image{
                url
              }
            }
            mediaContentType
            status
            mediaErrors {
              code
              details
              message
            }
            mediaWarnings {
              code
              message
            }
          }
        }
      }
    }
    """
    variables = {"productId": product_id}
    response = run_query(shop_name, access_token, query, variables)
    json_data = response.json()
    return json_data['data']['product']['media']['nodes']


def product_variants_by_product_id(shop_name, access_token, product_id):
    if product_id.startswith('gid://'):
        assert '/Product/' in product_id, f'non-product gid was provided: {product_id}'
        product_id = product_id.rsplit('/', 1)[-1]
    query = """
      {
        productVariants(first:10, query: "product_id:%s") {
          nodes {
            id
            displayName
            sku
            media (first:50){
              nodes{
                id
                ... on MediaImage {
                  image{
                    url
                  }
                }
              }
            }
          }
        }
      }
    """ % product_id
    res = run_query(shop_name, access_token, query)
    return res.json()['data']['productVariants']['nodes']


def product_id_by_variant_id(shop_name, access_token, variant_id):
    if variant_id.isnumeric():
        variant_id = f'gid://shopify/ProductVariant/{variant_id}'
    query = """
      {
        productVariant(id:"%s") {
          displayName,
          product{
            title
            id
          }
        }
      }
    """ % variant_id
    res = run_query(shop_name, access_token, query)
    return res.json()['data']['productVariant']['product']['id']


def remove_product_media_by_product_id(shop_name, access_token, product_id, media_ids=None):
    if not media_ids:
      media_nodes = medias_by_product_id(shop_name, access_token, product_id)
      media_ids = [node['id'] for node in media_nodes]

    if not media_ids:
        logger.debug(f"Nothing to delete for {product_id}")
        return True

    logger.info(f"Going to delete {media_ids} from {product_id}")

    query = """
    mutation deleteProductMedia($productId: ID!, $mediaIds: [ID!]!) {
      productDeleteMedia(productId: $productId, mediaIds: $mediaIds) {
        deletedMediaIds
        product {
          id
        }
        mediaUserErrors {
          code
          field
          message
        }
      }
    }
    """

    variables = {
        "productId": product_id,
        "mediaIds": media_ids
    }
    response = run_query(shop_name, access_token, query, variables)
    logger.info(f'Initial media status for deletion:\n{response.json()}')
    status = wait_for_media_processing_completion(shop_name, access_token, product_id)
    if not status:
        raise Exception("Error during media processing")


def assign_images_to_product(shop_name, access_token, resource_urls, alts, product_id):
    mutation_query = """
    mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
      productCreateMedia(media: $media, productId: $productId) {
        media {
          alt
          mediaContentType
          status
        }
        userErrors {
          field
          message
        }
        product {
          id
          title
        }
      }
    }
    """

    medias = [{
        "originalSource": url,
        "alt": alt,
        "mediaContentType": "IMAGE"
    } for url, alt in zip(resource_urls, alts)]

    variables = {
        "media": medias,
        "productId": product_id
    }

    response = run_query(shop_name, access_token, mutation_query, variables)
    json_data = response.json()

    logger.debug("Initial media status:")
    logger.debug(json_data)

    if json_data.get('errors') or json_data['data']['productCreateMedia']['userErrors']:
        raise Exception(f"Error during media creation: {json_data['data']['productCreateMedia']['userErrors']}")

    status = wait_for_media_processing_completion(shop_name, access_token, product_id)
    if not status:
        raise Exception("Error during media processing")


def wait_for_media_processing_completion(shop_name, access_token, product_id, timeout_minutes=10):
    poll_interval = 5  # Poll every 5 seconds
    max_attempts = int((timeout_minutes * 60) / poll_interval)
    attempts = 0

    while attempts < max_attempts:
        media_nodes = medias_by_product_id(shop_name, access_token, product_id)
        processing_items = [
            node for node in media_nodes if node['status'] == "PROCESSING"]
        failed_items = [
            node for node in media_nodes if node['status'] == "FAILED"]

        if failed_items:
            logger.info("Some media failed to process:")
            for item in failed_items:
                logger.info(f"Status: {item['status']}, Errors: {item['mediaErrors']}")
            return False

        if not processing_items:
            logger.info("All media have completed processing.")
            return True

        logger.info("Media still processing. Waiting...")
        time.sleep(poll_interval)
        attempts += 1

    logger.info("Timeout reached while waiting for media processing completion.")
    return False


def check_rohseoul_media(sku, medias):
    if medias:
      filename = medias[0]['image']['url'].rsplit('/', 1)[-1]
      return f'{sku}_0' in filename or filename.startswith('b1_') or '_0_' in filename
    logger.info(f'no media for {sku}')
    return True


def medias_by_variant_id(shop_name, access_token, variant_id):
    product_id = product_id_by_variant_id(shop_name, access_token, variant_id)
    all_medias = medias_by_product_id(shop_name, access_token, product_id)
    all_media_ids = [m['id'] for m in all_medias]
    all_variants = product_variants_by_product_id(shop_name, access_token, product_id)
    assert all(check_rohseoul_media(variant['sku'], variant['media']['nodes']) for variant in all_variants), f'suspicious media found in variants of {product_id}: {all_variants}'
    target_variant = [v for v in all_variants if v['id'] == variant_id]
    assert len(target_variant) == 1, f"{'No' if not target_variant else 'Multiple'} target variants: target_variants"
    target_variant = target_variant[0]
    if not target_variant['media']['nodes']:
        variant = variant_by_variant_id(shop_name, access_token, variant_id)
        return [media for media in all_medias if variant['sku'] in media['image']['url']]
    target_media_start_position = all_media_ids.index(target_variant['media']['nodes'][0]['id'])
    all_media_start_positions = sorted([all_media_ids.index(variant['media']['nodes'][0]['id']) for variant in all_variants] + [len(all_medias)])
    target_media_end_position = all_media_start_positions[all_media_start_positions.index(target_media_start_position) + 1]
    return all_medias[target_media_start_position:target_media_end_position]


def medias_by_sku(shop_name, access_token, sku):
    variant_id = variant_id_by_sku(shop_name, access_token, sku)
    return medias_by_variant_id(shop_name, access_token, variant_id)


def variant_by_sku(shop_name, access_token, sku):
    query = """
    {
      productVariants(first: 10, query: "sku:'%s'") {
        nodes {
          id
          title
          product {
            id
          }
        }
      }
    }
    """ % sku
    response = run_query(shop_name, access_token, query)
    json_data = response.json()
    return json_data['data']['productVariants']


def product_id_by_sku(shop_name, access_token, sku):
    json_data = variant_by_sku(shop_name, access_token, sku)
    if len(json_data['nodes']) != 1:
        raise Exception(f"{'Multiple' if json_data['nodes'] else 'No'} variants found for {sku}: {json_data['nodes']}")
    return json_data['nodes'][0]['product']['id']


def variant_by_variant_id(shop_name, access_token, variant_id):
    query = """
    {
      productVariant(id: "%s") {
        id
        title
        sku
        media(first: 5) {
          nodes {
            id
          }
        }
      }
    }
    """ % variant_id

    response = run_query(shop_name, access_token, query, {})
    json_response = response.json()

    return json_response['data']['productVariant']


def variant_id_by_sku(shop_name, access_token, sku):
    json_data = variant_by_sku(shop_name, access_token, sku)
    if len(json_data['nodes']) != 1:
        raise Exception(f"{'Multiple' if json_data['nodes'] else 'No'} variants found for {sku}: {json_data['nodes']}")
    return json_data['nodes'][0]['id']


def generate_staged_upload_targets(shop_name, access_token, file_names, mime_types):
    query = """
    mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
      stagedUploadsCreate(input: $input) {
        stagedTargets {
          url
          resourceUrl
          parameters {
            name
            value
          }
        }
        userErrors {
          field
          message
        }
      }
    }
    """

    variables = {
        "input": [{
            "resource": "IMAGE",
            "filename": file_name,
            "mimeType": mime_type,
            "httpMethod": "POST",
        } for file_name, mime_type in zip(file_names, mime_types)]
    }

    response = run_query(shop_name, access_token, query, variables)
    return response.json()['data']['stagedUploadsCreate']['stagedTargets']


def upload_images_to_shopify(staged_targets, local_paths, mime_types):
    for target, local_path, mime_type in zip(staged_targets, local_paths, mime_types):
        if mime_type in ['image/psd']:
            continue
        file_name = local_path.rsplit('/', 1)[-1]
        logger.info(f"  processing {file_name}")
        payload = {
            'Content-Type': mime_type,
            'success_action_status': '201',
            'acl': 'private',
        }
        payload.update({param['name']: param['value']
                       for param in target['parameters']})
        with open(local_path, 'rb') as f:
            logger.debug(f"  starting upload of {local_path}")
            response = requests.post(target['url'],
                                     files={'file': (file_name, f)},
                                     data=payload)
        logger.debug(f"upload response: {response.status_code}")
        if response.status_code != 201:
            logger.error(f'!!! upload failed !!!\n\n{local_path}:\n{target}\n\n{response.text}\n\n')
            response.raise_for_status()


def detach_variant_media(shop_name, access_token, product_id, variant_id, media_id):
    query = """
    mutation productVariantDetachMedia($productId: ID!, $variantMedia: [ProductVariantDetachMediaInput!]!) {
      productVariantDetachMedia(productId: $productId, variantMedia: $variantMedia) {
        product {
          id
        }
        productVariants {
          id
          media(first: 5) {
            nodes {
              id
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    variables = {
        "productId": product_id,
        "variantMedia": [{
            "variantId": variant_id,
            "mediaIds": [media_id]
        }]
    }
    return run_query(shop_name, access_token, query, variables)


def product_media_by_file_name(shop_name, access_token, product_id, name):
    medias = medias_by_product_id(shop_name, access_token, product_id)
    for media in medias:
        if name.rsplit('.', 1)[0] in media['image']['url']:
            return media


def assign_image_to_skus(shop_name, access_token, product_id, media_id, variant_ids):
    variants = [variant_by_variant_id(shop_name, access_token, variant_id)
                for variant_id in variant_ids]
    for variant in variants:
        if len(variant['media']['nodes']) > 0:
            detach_variant_media(shop_name, access_token,
                                 product_id,
                                 variant['id'],
                                 variant['media']['nodes'][0]['id'])
    query = """
    mutation productVariantAppendMedia($productId: ID!, $variantMedia: [ProductVariantAppendMediaInput!]!) {
      productVariantAppendMedia(productId: $productId, variantMedia: $variantMedia) {
        product {
          id
        }
        productVariants {
          id
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    variables = {
        "productId": product_id,
        "variantMedia": [{"variantId": vid, "mediaIds": [media_id]} for vid in variant_ids]
    }

    return run_query(shop_name, access_token, query, variables)


def location_id_by_name(shop_name, access_token, name):
    query = '''
    {
      locations(first:10, query:"name:%s") {
        nodes {
          id
        }
      }
    }
    ''' % name
    res = run_query(shop_name, access_token, query)
    res = res.json()['data']['locations']['nodes']
    assert len(res) == 1, f'{"Multiple" if res else "No"} locations found for {name}: {res}'
    return res[0]['id']


def inventory_item_id_by_sku(shop_name, access_token, sku):
    query = '''
    {
      inventoryItems(query:"sku:%s", first:5) {
        nodes{
          id
        }
      }
    }''' % sku
    res = run_query(shop_name, access_token, query)
    res = res.json()['data']['inventoryItems']['nodes']
    assert len(res) == 1, f'{"Multiple" if res else "No"} inventoryItems found for {sku}: {res}'
    return res[0]['id']


def set_inventory_quantity_by_sku_and_location_id(shop_name, access_token, sku, location_id, quantity):
    inventory_item_id = inventory_item_id_by_sku(shop_name, access_token, sku)
    query = '''
    mutation inventorySetQuantities($locationId: ID!, $inventoryItemId: ID!, $quantity: Int!) {
    inventorySetQuantities(
        input: {name: "available", ignoreCompareQuantity: true, reason: "correction",
                quantities: [{inventoryItemId: $inventoryItemId,
                              locationId: $locationId,
                              quantity: $quantity}]}
    ) {
        inventoryAdjustmentGroup {
        id
        changes {
            name
            delta
            quantityAfterChange
        }
        reason
        }
        userErrors {
        message
        code
        field
        }
      }
    }
    '''
    variables = {
        "inventoryItemId": inventory_item_id,
        "locationId": location_id,
        "quantity": quantity
    }
    res = run_query(shop_name, access_token, query, variables)
    json_data = res.json()
    if json_data.get('errors') or json_data['data']['inventorySetQuantities']['userErrors']:
        raise Exception(f"Error updating inventory quantity: {json_data.get('errors') or json_data['data']['inventorySetQuantities']['userErrors']}")
    updates = json_data['data']['inventorySetQuantities']['inventoryAdjustmentGroup']
    if not updates:
        logger.info(f'no updates found after updating inventory of {sku} to {quantity}')
    return updates


def run_query(shop_name, access_token, query, variables=None, method='post', resource='graphql'):
    url = f'https://{shop_name}.myshopify.com/admin/api/2024-07/{resource}.json'
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    data = {
        "query": query,
        "variables": variables
    }
    return requests.post(url, headers=headers, json=data)
