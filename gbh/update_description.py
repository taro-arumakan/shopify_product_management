from gbh.product_create_home import product_info_list_from_sheet_scent_and_size_options, product_info_list_from_sheet_color_options
import utils

def main():
    client = utils.client('gbhjapan')
    # product_info_list = product_info_list_from_sheet_scent_and_size_options(client, client.sheet_id, 'HOME&COSME_25.05.09', titles=['HAND BALM'])

    # for product_info in product_info_list:
    #     description_html = client.get_description_html(description=product_info['description'],
    #                                                     product_care=product_info['product_care'],
    #                                                     material=product_info['material'],
    #                                                     size_text=product_info['size_text'],
    #                                                     made_in=product_info['made_in'],
    #                                                     get_size_table_html_func=lambda x: x)
    #     product_id = client.product_id_by_title(product_info['title'])
    #     print(description_html)
    #     print(product_id)
    #     client.update_product_description(product_id, description_html)

    product_info_list = product_info_list_from_sheet_color_options(client, client.sheet_id, 'HOME&COSME_25.05.09', titles=['WOOD PLATE'])

    for product_info in product_info_list:
        description_html = client.get_description_html(description=product_info['description'],
                                                       product_care=product_info['product_care'],
                                                       material=product_info['material'],
                                                       size_text=product_info['size_text'],
                                                       made_in=product_info['made_in'],
                                                       get_size_table_html_func=lambda x: x)
        product_id = client.product_id_by_title(product_info['title'])
        print(description_html)
        print(product_id)
        client.update_product_description(product_id, description_html)

if __name__ == '__main__':
    main()
