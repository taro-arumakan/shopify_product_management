from rohseoul.product_create import get_description_html, product_info_lists_from_sheet
import shopify_graphql_client
import google_api_interface

def main():
    sgc = shopify_graphql_client.get('rohseoul')
    gai = google_api_interface.get('rohseoul')
    product_info_list = product_info_lists_from_sheet(gai, gai.sheet_id, '25SS 2차오픈(4월)(Summer 25)', '25ss-2nd')

    for product_info in product_info_list:
        if product_info['title'] in ['Pulpy crossbody bag Nylon', 'Pulpy crossbody bag Wrinkled']:
            description_html = get_description_html(sgc, product_info['description'],
                                                         product_info['material'],
                                                         product_info['size_text'],
                                                         product_info['made_in'])
            product_id = sgc.product_id_by_handle(product_info['handle'])
            print(description_html)
            print(product_info['handle'])
            print(product_id)
            sgc.update_product_description(product_id, description_html)

if __name__ == '__main__':
    main()
