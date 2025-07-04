import datetime
import logging
import gspread

logger = logging.getLogger(__name__)


class GoogleSheetsApiInterface:

    def to_products_list(
        self,
        sheet_id,
        sheet_title,
        start_row,
        product_attr_column_map,
        option1_attr_column_map=None,
        option2_attr_column_map=None,
        handle_suffix=None,
        row_filter_func=None,
    ):
        def update_list(target_list, column_map, row, row_num):
            for i, (k, ci) in enumerate((column_map or {}).items()):
                if value := self.get_cell_value(
                    row, ci, k, row_num, sheet_id, sheet_title
                ):
                    if i == 0:
                        if not target_list or target_list[-1].get(k) != value:
                            target_list.append({k: value})
                    elif value:
                        target_list[-1][k] = value

        rows = self.worksheet_rows(sheet_id, sheet_title)
        res = []
        for index, row in enumerate(rows[start_row:]):
            if row_filter_func and not row_filter_func(row):
                continue
            sheet_row_num = index + start_row + 1
            update_list(res, product_attr_column_map, row, sheet_row_num)
            if handle_suffix is not None and "handle" not in res[-1]:
                parts = res[-1]["title"].lower().split(" ")
                if handle_suffix:  # allow passing of empty string
                    parts.append(handle_suffix)
                res[-1]["handle"] = "-".join(parts)
            if option1_attr_column_map:
                update_list(
                    res[-1].setdefault("options", []),
                    option1_attr_column_map,
                    row,
                    sheet_row_num,
                )
            if option2_attr_column_map:
                update_list(
                    res[-1]["options"][-1].setdefault("options", []),
                    option2_attr_column_map,
                    row,
                    sheet_row_num,
                )
        return res

    def get_cell_value(
        self, row, column_index, column_name, row_num, sheet_id, sheet_title
    ):
        v = row[column_index]
        if v or v == 0:
            if column_name in ["release_date"] and isinstance(v, int):
                v = str(datetime.date(1899, 12, 30) + datetime.timedelta(days=v))
            elif column_name in ["price", "stock", "compare_at_price"]:
                if isinstance(v, str):
                    v = (
                        v.replace("¥", "")
                        .replace(",", "")
                        .replace(" ", "")
                        .replace("￥", "")
                    )
                assert (
                    isinstance(v, (int, float)) or v.isnumeric()
                ), f"expected int for {column_name}, got {type(v)}: {v}"
                v = int(v)
            elif column_name in ["サイズ", "sku", "product_number"]:
                v = str(v).strip()
            elif column_name == "drive_link":
                if all([v, v != "no image", not v.startswith("http")]):
                    v = self.get_richtext_link(
                        sheet_id, sheet_title, row_num, column_index
                    )
            elif column_name in ["weight"]:
                assert isinstance(
                    v, (int, float)
                ), f"expected int or float for {column_name}, got {type(v)}: {v}"
            else:
                assert isinstance(
                    v, str
                ), f"expected str for {column_name}, got {type(v)}: {v}"
                v = v.strip()
        return v

    def get_sheet_index_by_title(self, sheet_id, sheet_title):
        worksheet = self.gspread_client.open_by_key(sheet_id)
        for meta in worksheet.fetch_sheet_metadata()["sheets"]:
            if meta["properties"]["title"] == sheet_title:
                return meta["properties"]["index"]
        raise RuntimeError(f"Did not find a sheet named {sheet_title}")

    def get_link(self, spreadsheet_id, sheet_title, row, row_num, column_num):
        link = row[column_num]
        if all([link, link != "no image", not link.startswith("http")]):
            link = self.get_richtext_link(
                spreadsheet_id, sheet_title, row_num, column_num
            )
        return link

    def get_richtext_link(self, spreadsheet_id, sheet_title, row, column):
        # Use the Google Sheets API directly for rich text data
        import string

        range_notation = f"{sheet_title}!{string.ascii_uppercase[column]}{row}"
        response = (
            self.sheets_service.spreadsheets()
            .get(
                spreadsheetId=spreadsheet_id,
                ranges=range_notation,
                fields="sheets(data(rowData(values)))",
            )
            .execute()
        )
        hyperlink = (
            response.get("sheets", [])[0]
            .get("data", [])[0]
            .get("rowData", [])[0]
            .get("values", [])[0]
            .get("hyperlink")
        )
        print(f"The hyperlink is: {hyperlink}")
        return hyperlink

    def drive_link_to_id(self, link):
        return (
            link.rsplit("/", 1)[-1]
            .replace("open?id=", "")
            .replace("?usp=drive_link", "")
            .replace("?usp=sharing", "")
            .replace("&usp=drive_fs", "")
            .replace("?dmr=1&ec=wgc-drive-globalnav-goto", "")
        )

    def worksheet_rows(self, sheet_id, sheet_title):
        sheet_index = self.get_sheet_index_by_title(sheet_id, sheet_title)
        worksheet = self.gspread_client.open_by_key(sheet_id).get_worksheet(sheet_index)
        return worksheet.get_all_values(
            value_render_option=gspread.utils.ValueRenderOption.unformatted
        )

    def get_variants_level_info(self, product_info, key="sku"):
        if key in product_info:
            variants_info = [product_info]
        elif (o1 := product_info["options"]) and key in o1[0]:
            variants_info = product_info["options"]
        elif (o2 := product_info["options"][0]["options"]) and key in o2[0]:
            variants_info = [
                options2
                for options1 in product_info["options"]
                for options2 in options1["options"]
            ]
        else:
            raise ValueError(f"No variant {key} found in product info: {product_info}")
        return variants_info

    def get_sku_stocks_map(self, product_info):
        variants_info = self.get_variants_level_info(product_info)
        return {variant["sku"]: variant["stock"] for variant in variants_info}

    def update_stocks(self, product_info_list, location_name):
        logger.info("updating inventory")
        location_id = self.location_id_by_name(location_name)
        sku_stock_map = {}
        [
            sku_stock_map.update(self.get_sku_stocks_map(product_info))
            for product_info in product_info_list
        ]
        return [
            self.set_inventory_quantity_by_sku_and_location_id(sku, location_id, stock)
            for sku, stock in sku_stock_map.items()
        ]

    def populate_option(self, product_info):
        option1_key, option2_key = None, None
        if option1 := product_info.get("options"):
            option1_key = list(option1[0].keys())[0]
            if option2 := option1[0].get("options"):
                option2_key = list(option2[0].keys())[0]
        if option2_key:
            return [
                [
                    {
                        option1_key: option1[option1_key],
                        option2_key: option2[option2_key],
                    },
                    option2.get("price")
                    or option1.get("price")
                    or product_info["price"],
                    option2["sku"],
                ]
                for option1 in product_info["options"]
                for option2 in option1["options"]
            ]
        if option1_key:
            return [
                [
                    {option1_key: option1[option1_key]},
                    option1.get("price") or product_info["price"],
                    option1["sku"],
                ]
                for option1 in product_info["options"]
            ]
        return []

    def get_child_variant_skus(self, variant_info):
        if "sku" in variant_info:
            return [variant_info["sku"]]
        if (o1 := variant_info["options"]) and "sku" in o1[0]:
            return [option1["sku"] for option1 in variant_info["options"]]
        if (o2 := variant_info["options"][0]["options"]) and "sku" in o2[0]:
            return [
                option2["sku"]
                for option1 in variant_info["options"]
                for option2 in option1["options"]
            ]
        raise ValueError(f"No sku found in variant info: {variant_info}")

    def populate_drive_ids_and_skuss(self, product_info):
        skuss = []
        drive_ids = []
        image_level_variant = self.get_variants_level_info(
            product_info, key="drive_link"
        )
        for variant in image_level_variant:
            assert variant[
                "drive_link"
            ], f"no drive link for {product_info['title'], {variant}}"
            drive_ids.append(self.drive_link_to_id(variant["drive_link"]))
            skuss.append(self.get_child_variant_skus(variant))
        return drive_ids, skuss
