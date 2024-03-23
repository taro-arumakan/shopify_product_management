query_epokhe_products = '''{
  products(first: 200, query: "vendor:EPOKHE", sortKey: TITLE) {
    nodes {
      id
      title
      variants(first: 15) {
        nodes {
          id
          title
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
}'''

query_mutate_product = '''
mutation updateProductSEOTitle($seo_title: String!, $id: ID!, $url_handle: String) {
  productUpdate(
    input: {seo: {title: $seo_title}, id: $id, handle: $url_handle}
  ) {
    product {
      seo {
        title
      }
      handle
    }
  }
}'''

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
