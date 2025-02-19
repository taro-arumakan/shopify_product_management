import json
import os
import requests
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv(override=True)
SHOPNAME = 'archive-epke'
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
print(ACCESS_TOKEN)
GOOGLE_CREDENTIAL_PATH = os.getenv('GOOGLE_CREDENTIAL_PATH')

GSPREAD_ID = '1MYGLW9pekrhra8bXqIA2H2t3g3kETUWIDcFnjdW4j84'
SHEET_TITLE = '現 JP EC 価格改定 '


google_credentials = None

def authenticate_google_api():
    # Authenticate to Google API using Service Account
    global google_credentials
    if not google_credentials:
        google_credentials = Credentials.from_service_account_file(
            GOOGLE_CREDENTIAL_PATH,
            scopes=['https://www.googleapis.com/auth/drive',
                    'https://www.googleapis.com/auth/spreadsheets']
        )
    return google_credentials


def gspread_access():
    creds = authenticate_google_api()
    return gspread.authorize(creds)


def get_sheet_index_by_title(sheet_id, sheet_title):
    worksheet = gspread_access().open_by_key(sheet_id)
    for meta in worksheet.fetch_sheet_metadata()['sheets']:
        if meta['properties']['title'] == sheet_title:
            return meta['properties']['index']
    raise RuntimeError(f'Did not find a sheet named {sheet_title}')

def get_link(spreadsheet_id, row, row_num, column_num):
    link = row[column_num]
    if all([link, link != 'no image', not link.startswith('http')]):
        link = get_richtext_link(spreadsheet_id, row_num, column_num)
    return link

def get_richtext_link(spreadsheet_id, row, column):
    # Use the Google Sheets API directly for rich text data
    from googleapiclient.discovery import build
    service = build("sheets", "v4", credentials=authenticate_google_api())
    import string
    range_notation = f'{SHEET_TITLE}!{string.ascii_uppercase[column]}{row}'
    response = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        ranges=range_notation,
        fields="sheets(data(rowData(values)))"
    ).execute()
    hyperlink = (
        response.get("sheets", [])[0]
        .get("data", [])[0]
        .get("rowData", [])[0]
        .get("values", [])[0]
        .get("hyperlink")
    )
    # print(f"The hyperlink is: {hyperlink}")
    return hyperlink


def variant_ids_by_product_id(product_id):
    query = """
    {
      productVariants(first: 10, query: "product_id:'%s'") {
        nodes {
          id
          title
          product {
            id
          }
        }
      }
    }
    """ % product_id


sheet_index = get_sheet_index_by_title(GSPREAD_ID, SHEET_TITLE)
worksheet = gspread_access().open_by_key(GSPREAD_ID).get_worksheet(sheet_index)
rows = worksheet.get_all_values()

price_by_product_id = {}
price_by_title = {}
for i, row in enumerate(rows[4:]):
    link = get_richtext_link(GSPREAD_ID, i + 5, 0)    # row is 1 base, column is 0 base
    price = int(row[-7].replace('¥', '').replace(',', ''))
    print(row[0], link, price)
    if price:
        price_by_product_id[link.rsplit('/', 1)[-1]] = price
        price_by_title[row[0].lower()] = price


import pandas as pd
df = pd.read_csv('/Users/taro/Downloads/products_export_archive-epke.csv')
df = df[df['Variant SKU'].notnull()]
df = df[['Handle', 'Title',
         'Option1 Name', 'Option1 Value',
          'Option2 Name', 'Option2 Value',
          'Option3 Name', 'Option3 Value',
          'Variant SKU',
          'Variant Price',
          'Variant Compare At Price']]

df = df[df['Title'].str.lower().isin(price_by_title)]
df['Variant Price'] = df['Title'].apply(lambda x: price_by_title[x.lower()])
df['Variant Compare At Price'] = df['Title'].apply(lambda x: price_by_title[x.lower()])
