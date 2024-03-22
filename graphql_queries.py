query_epokhe_products = '''{
  products(first: 100, query: "vendor:EPOKHE") {
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
