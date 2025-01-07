import os
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv(override=True)
SHOPNAME = 'gbhjapan'
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
print(ACCESS_TOKEN)

def run_query(query, variables=None, method='post', resource='graphql'):
    url = f'https://{SHOPNAME}.myshopify.com/admin/api/2024-07/{resource}.json'
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    data = {
        "query": query,
        "variables": variables
    }
    return requests.post(url, headers=headers, json=data)

def variant_by_sku(sku):
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
    response = run_query(query, {})
    json_data = response.json()
    return json_data['data']['productVariants']

def product_id_and_variant_id_for_sku(sku):
    json_data = variant_by_sku(sku)
    if len(json_data['nodes']) != 1:
        raise Exception(f"{'Multiple' if json_data['nodes'] else 'No'} variants found for {sku}: {json_data['nodes']}")
    return json_data['nodes'][0]['product']['id'], json_data['nodes'][0]['id']


def update_variant_sku(sku_before, sku_after):

  product_id, variant_id = product_id_and_variant_id_for_sku(sku_before)

  query_update_variant_sku = '''
  mutation UpdateVariantSKU ($id: ID!, $sku: String!){
    productVariantUpdate(
      input: {
        id: $id,
        inventoryItem: {
          sku: $sku
        }
      }
    ){
      productVariant {
        id
        sku
      }
    }
  }
  '''
  variables = dict(id=variant_id,
                   sku=sku_after)

  res = run_query(query_update_variant_sku, variables)
  if 'errors' in res.json():
      raise Exception(f'Bad response: {res.json()}')


if __name__ == '__main__':
    df = pd.read_csv('/Users/taro/Downloads/gbh_sku_update_20241211_final.csv')
    for _, row in df.iterrows():
        b, a = row['sku_before'], row['sku_after']
        print('processing', b, a)
        update_variant_sku(b, a)
