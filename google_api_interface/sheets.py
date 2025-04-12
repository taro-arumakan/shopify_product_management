class GoogleSheetsApiInterface:
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
        return worksheet.get_all_values()
