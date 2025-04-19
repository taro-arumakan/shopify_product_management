import utils


def main():
    shop_name = 'archive-epke'
    sheet_name = '2025.4/10 Release'

    client = utils.client(shop_name)
    rows = client.worksheet_rows(client.sheet_id, sheet_name)

    for row in rows[2:]:
        title = row[3]
        print(title)
        try:
            gid = client.product_by_title(title)
        except RuntimeError as e:
            print(e)
        else:
            print(gid)

if __name__ == '__main__':
    main()
