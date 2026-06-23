import utils


def main():
    skus = [
        "KM-26SS-JK01-IV-S",
        "KM-26SS-JK01-IV-M",
        "KM-26SS-BL02-IV-S",
        "KM-26SS-BL02-IV-M",
        "KM-26SS-BL02-IV-L",
        "KM-26SS-BL02-BK-S",
        "KM-26SS-BL02-BK-M",
        "KM-26SS-BL02-BK-L",
        "KM-26SS-PT03-LBE-S",
        "KM-26SS-PT03-LBE-M",
        "KM-26SS-PT03-LBE-L",
        "KM-26SS-PT03-BK-S",
        "KM-26SS-PT03-BK-M",
        "KM-26SS-PT03-BK-L",
        "KM-26SS-SK03IVS",
        "KM-26SS-SK03IVM",
        "KM-26SS-SK03IVL",
        "KM-26SS-OP01-IV-S",
        "KM-26SS-OP01-IV-M",
        "KM-26SS-OP01-IV-L",
        "KM-26SS-OP01-NV-S",
        "KM-26SS-OP01-NV-M",
        "KM-26SS-OP01-NV-L",
        "KM-26SS-BL03-WH-S",
        "KM-26SS-BL03-WH-M",
        "KM-26SS-BL03-WH-L",
        "KM-26SS-BL03-LBL-S",
        "KM-26SS-BL03-LBL-M",
        "KM-26SS-BL03-LBL-L",
        "KM-26SS-PT02-BK-S",
        "KM-26SS-PT02-BK-M",
        "KM-26SS-PT02-BK-L",
    ]

    client = utils.client("kume")
    variants = client.variants_by_skus(skus)
    product_ids = set([v["product"]["id"] for v in variants])

    client.collection_create_by_product_ids(
        collection_title="Aki's Picks", product_ids=product_ids
    )


if __name__ == "__main__":
    main()
