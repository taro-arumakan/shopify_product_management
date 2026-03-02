from brands.lememe.client import LememeClient

skus = [
    "BFQJKZW004IV",
    "BFQJKZW004IV",
    "BFQJKZW004GE",
    "BFQJKZW004GE",
    "BFQJKXFPABR",
    "BFQJKXFPAKH",
    "BFQJPAS044IV",
    "BFQJPAS044IV",
    "BFQJPAS044BL",
    "BFQJPAS044BL",
    "BFQJKAS035BT",
    "BFQBLAS317CM",
    "BFQBLAS317NA",
    "BFQBLAS316WH",
    "BFQBLAS316BL",
    "BFQBLZF311MI",
    "BFQBLZF311CM",
    "BFQTSAS212IV",
    "BFQTSAS212NA",
    "BFQKNZF117BE",
    "BFQKNZF117NA",
    "BFQPTAS511BL",
    "BFQPTAS511BL",
    "BFQPTAS513BL",
    "BFQPTAS513BL",
    "BFQPTAS513WH",
    "BFQPTAS513WH",
    "BFQPTAS514CM",
    "BFQPTAS514NA",
    "BFQSKAS715BL",
    "BFQSKAS715WH"
]


def main():
    client = LememeClient()
    product_ids = {client.product_id_by_sku(sku) for sku in skus}
    client.collection_create_by_product_ids("26 Ready to Wear", product_ids)


if __name__ == "__main__":
    main()
