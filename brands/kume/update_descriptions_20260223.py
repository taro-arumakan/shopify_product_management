from brands.kume.client import KumeClient


def main():
    sheet_name = "26SS_1次_2月23日"
    client = KumeClient()
    product_inputs = client.product_inputs_by_sheet_name(sheet_name)
    filter_func = lambda pi: pi.get("release_date") == "2026-02-23"
    
    for pi in filter(filter_func, product_inputs):

        product_id = client.product_id_by_title(pi['title'])

        new_description = client.get_description_html(pi)
        client.update_product_description(product_id, new_description)


if __name__ == "__main__":
    main()
