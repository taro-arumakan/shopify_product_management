import logging
import utils

logging.basicConfig(level=logging.INFO)


def main():
    client = utils.client("gbhjapan")
    rows = client.worksheet_rows(client.sheet_id, "APPAREL 24SS_削除希望")

    for row in rows[4:]:
        try:
            product_id = client.product_id_by_sku(row[8])
            client.update_product_status(product_id, "ARCHIVED")
            print(f"Archived {row[8]} - {row[5]}")
        except (
            utils.NoVariantsFoundException,
            utils.MultipleVariantsFoundException,
        ) as ex:
            print(f"Error finding {row[8]} - {row[5]}, {ex}")


if __name__ == "__main__":
    main()
