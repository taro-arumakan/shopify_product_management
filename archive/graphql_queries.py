query_epokhe_products = '''
{
  products(first: 200, query: "vendor:EPOKHE", sortKey: TITLE) {
    nodes {
      id
      title
      variants(first: 15) {
        nodes {
          id
          title
          sku
          price
        }
      }
      onlineStoreUrl
      metafields(first: 50) {
        nodes {
          key
          type
          description
          value
          definition {
            name
          }
        }
      }
      handle
      seo {
        title
        description
      }
    }
  }
}
'''

query_epokhe_variants_by_product_query = '''
query productsByQuery($query_string: String!)
{
  products(first: 200, query: $query_string, sortKey: TITLE) {
    nodes {
      id
      title
      variants(first: 15) {
        nodes {
          id
          title
          sku
          price
        }
      }
    }
  }
}
'''

query_mutate_product = '''
mutation updateProductSEO($id: ID!, $title: String, $seo_title: String, $url_handle: String) {
  productUpdate(
    input: {id: $id, title: $title, seo: {title: $seo_title}, handle: $url_handle}
  ) {
    product {
      title
      seo {
        title
      }
      handle
    }
  }
}
'''

query_update_variant_title = '''
mutation UpdateVariantTitle ($id: ID!, $new_title: String!){
  productVariantUpdate(input: {id: $id, options: [$new_title]}) {
    productVariant {
      id
      title
    }
  }
}
'''

query_update_variant_sku = '''
mutation UpdateVariantTitle ($id: ID!, $sku: String!){
  productVariantUpdate(input: {id: $id, sku: $sku}) {
    productVariant {
      id
      sku
    }
  }
}
'''

query_all_products = '''
{
	products(first:100) {
		nodes{
      id
      title
      variants(first:100){
        nodes{
          id
          sku
        }
      }
    }
	}
}
'''
