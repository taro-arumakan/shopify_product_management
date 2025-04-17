import datetime
import gspread

class GoogleSheetsApiInterface:
    def to_products_list(self, sheet_id, sheet_title, start_row, product_attr_column_map,
                                                                 option1_attr_column_map=None,
                                                                 option2_attr_column_map=None,
                                                                 handle_suffix=None,
                                                                 row_filter_func=None):
        def update_list(target_list, column_map, row):
            for i, (k, ci) in enumerate((column_map or {}).items()):
                if value := self.get_cell_value(row, ci, k):
                    if i == 0:
                        if not target_list or target_list[-1].get(k) != value:
                            target_list.append({k: value})
                    elif value:
                        target_list[-1][k] = value
        rows = self.worksheet_rows(sheet_id, sheet_title)
        res = []
        for row in rows[start_row:]:
            if row_filter_func and not row_filter_func(row):
                continue
            update_list(res, product_attr_column_map, row)
            if handle_suffix and 'handle' not in res[-1]:
                res[-1]['handle'] = '-'.join(res[-1]['title'].lower().split(' ') + [handle_suffix])
            update_list(res[-1].setdefault('options', []), option1_attr_column_map, row)
            update_list(res[-1]['options'][-1].setdefault('options', []), option2_attr_column_map, row)
        return res

    def get_cell_value(self, row, column_index, column_name):
        v = row[column_index]
        if column_name in ['release_date'] and isinstance(v, int):
            assert isinstance(v, int), f'expected int for {column_name}, got {type(v)}: {v}'
            v = str(datetime.date(1899, 12, 30) + datetime.timedelta(days=v))
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
