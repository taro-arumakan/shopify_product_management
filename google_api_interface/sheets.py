import datetime
import gspread

class GoogleSheetsApiInterface:
    def to_products_list(self, sheet_id, sheet_title, start_row, product_attr_column_map, variant_attr_column_map=None, handle_suffix=None, row_filter_func=None):
        if not variant_attr_column_map:
            # TODO this is wrong - for color options as products brand such as KUME, they still have size variants.
            res = self.variants_as_products_list(sheet_id, sheet_title, start_row, product_attr_column_map)
        else:
            res = self.products_with_variants_list(sheet_id, sheet_title, start_row, product_attr_column_map, variant_attr_column_map, handle_suffix, row_filter_func)
        return res

    def products_with_variants_list(self, sheet_id, sheet_title, start_row, product_attr_column_map, variant_attr_column_map, handle_suffix=None, row_filter_func=None):
        rows = self.worksheet_rows(sheet_id, sheet_title)
        current_title = ''
        res = []
        for row in rows[start_row:]:
            if row_filter_func and not row_filter_func(row):
                continue
            title = row[product_attr_column_map['title']].strip()
            if title != current_title:
                if current_title:
                    res.append(product_dict)            # done processing all variants of a product
                current_title, product_dict = title, {}
                product_dict['title'] = title
                if handle_suffix:
                    product_dict['handle'] = '-'.join(title.lower().split(' ') + [handle_suffix])
                for k, ci in product_attr_column_map.items():
                    product_dict[k] = self.get_cell_value(row, ci, k)
            for k, ci in variant_attr_column_map.items():
                product_dict.setdefault(k, []).append(self.get_cell_value(row, ci, k))
        res.append(product_dict)                        # done processing the last product
        return res

    def variants_as_products_list(self, sheet_id, sheet_title, start_row, product_attr_column_map, new_only=False):
        rows = self.worksheet_rows(sheet_id, sheet_title)
        res = []
        value_by_attr_by_product = {}
        for row in rows[start_row:]:
            title = row[product_attr_column_map['title']]
            if new_only and row[product_attr_column_map['status']].strip() != 'NEW':
                self.logger.info(f'skipping row {title}')
                continue
            product_dict = dict(title=title)
            for k, ci in product_attr_column_map.items():
                product_dict[k] = self.get_cell_value(row, ci, k)
                if not product_dict[k]:
                    if k not in ['status']:
                        product_dict[k] = value_by_attr_by_product[k][title]    # fallback to previously processed value for that title
                else:
                    value_by_attr_by_product.setdefault(k, {}).setdefault(title, product_dict[k])
            product_dict['handle'] = '-'.join(title.lower().split(' ') + product_dict['color'].lower().split(' '))
            res.append(product_dict)                        # done processing the last product
        return res

    def get_cell_value(self, row, column_index, column_name):
        v = row[column_index]
        if column_name in ['release_date'] and isinstance(v, int):
            assert isinstance(v, int), f'expected int for {column_name}, got {type(v)}: {v}'
            v = str(datetime.date(1900, 1, 1) + datetime.timedelta(days=v))
        elif column_name in ['price', 'stock']:
            assert isinstance(v, (int, float)), f'expected int for {column_name}, got {type(v)}: {v}'
            v = int(v)
        else:
            assert isinstance(v, str), f'expected str for {column_name}, got {type(v)}: {v}'
            v = v.strip()
        return v


    def get_sheet_index_by_title(self, sheet_id, sheet_title):
        worksheet = self.gspread_client.open_by_key(sheet_id)
        for meta in worksheet.fetch_sheet_metadata()['sheets']:
            if meta['properties']['title'] == sheet_title:
                return meta['properties']['index']
        raise RuntimeError(f'Did not find a sheet named {sheet_title}')

    def get_link(self, spreadsheet_id, sheet_title, row, row_num, column_num):
        link = row[column_num]
        if all([link, link != 'no image', not link.startswith('http')]):
            link = self.get_richtext_link(spreadsheet_id, sheet_title, row_num, column_num)
        return link

    def get_richtext_link(self, spreadsheet_id, sheet_title, row, column):
        # Use the Google Sheets API directly for rich text data
        from googleapiclient.discovery import build
        import string
        range_notation = f'{sheet_title}!{string.ascii_uppercase[column]}{row}'
        response = self.sheets_service.spreadsheets().get(
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
        print(f"The hyperlink is: {hyperlink}")
        return hyperlink

    def drive_link_to_id(self, link):
        return (link.rsplit('/', 1)[-1].replace('open?id=', '')
                                    .replace('?usp=drive_link', '')
                                    .replace('?usp=sharing', '')
                                    .replace('&usp=drive_fs', '')
                                    .replace('?dmr=1&ec=wgc-drive-globalnav-goto', ''))

    def worksheet_rows(self, sheet_id, sheet_title):
        sheet_index = self.get_sheet_index_by_title(sheet_id, sheet_title)
        worksheet = self.gspread_client.open_by_key(sheet_id).get_worksheet(sheet_index)
        return worksheet.get_all_values(value_render_option=gspread.utils.ValueRenderOption.unformatted)
