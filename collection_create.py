import utils


def main():
    c = utils.client("kumej")
    titles = [
        "Basic Sliket Sweater",
        "Fringe Long Sleeve Cardigan",
        "Fringe Waist H-Line Skirt",
        "Off-the-Shoulder Shirt Blouse",
        "Organza Layered Midi Skirt",
        "Pleated Ruffle Sleeveless Long Dress",
        "Organza Back Mini Dress",
        "Side Frayed Wide Denim Pants",
        "Linen Boat-neck Vest",
        "Organza V-neck Trench Coat",
        "Back String Cotton Nylon Summer Jacket",
        "Twisted Back Detail T-shirt",
        "H-line Knitted Skirt ",
        "ESSENTIAL Basic Tank Top ",
        "ESSENTIAL Semi-Cropped Cotton T-shirt",
        "Pintucked Layering Dress",
        "Cropped Organza Collar Blouson Jacket",
        "Fitted Button Knitted Vest",
        "Back Buckle Detail Semi Bootcut Denim Pants",
        "Semi Wide Work Denim Pants",
        "Striped knitted Halter Top",
        "Cropped Linen Ribbon Tie Top",
        "One Button Square-neck Jacket",
        "Fringe Detail Oversized Shirt",
    ]
    product_ids = [
        c.product_id_by_title(title.replace("ESSENTIAL ", "")) for title in titles
    ]
    print(product_ids)
    c.collection_create_by_product_ids("HANKYU UMEDA COLLECTION", product_ids)


if __name__ == "__main__":
    main()
