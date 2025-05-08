"""
largely moved to product_create.py of each brand and helpder classes.
"""

import logging
import os

import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_product_images_to_shopify(
    sgc: utils.Client,
    image_prefix,
    product_title,
    drive_ids,
    skuss,
    images_local_dir,
):
    """
    Processes and uploads images for a product to Shopify, associating them with
    specific SKUs based on their positions within provided Google Drive folders.

    :param image_prefix: A prefix to be added to each image file name during processing.
    :param product_title: The title of the product in Shopify. Used to retrieve the product ID.
    :param drive_ids: A list of Google Drive folder IDs, each containing images for different color variants of the product.
    :param skuss: A nested list of SKUs. Each inner list corresponds to a Google Drive folder and contains SKUs for different sizes of the same color variant.

    Example:
    image_prefix = '20240901_sample_upload_'
    product_title = 'Twisted Neck Superfine Merino Wool Cardigan'
    drive_ids = [
        '1qEME0URUWETd_fepr3KJFSz2EhXCxjoJ',
        '1ACt4g7tqigsmXYemUCc9KnDynW20E5Iz',
        '15VwlvmnC7EBmOZaslyMq40KyHXcWt63g'
    ]
    skuss = [
        ['KM-24FW-SW01-IV-S', 'KM-24FW-SW01-IV-M'],
        ['KM-24FW-SW01-MT-S', 'KM-24FW-SW01-MT-M'],
        ['KM-24FW-SW01-DBR-S', 'KM-24FW-SW01-DBR-M']
    ]
    """
    if sgc.shop_name in ["rohseoul"]:
        product_handle = "-".join(
            list(
                map(
                    str.lower,
                    product_title.replace(")", "").replace("(", "").split(" "),
                )
            )
            + ["25ss"]
        )
        logger.info(f"product_handle: {product_handle}")
        product_id = sgc.product_id_by_handle(product_handle)
    elif sgc.shop_name in ["archive-epke"]:
        product_handle = "-".join(
            list(
                map(
                    str.lower,
                    product_title.replace(")", "").replace("(", "").split(" "),
                )
            )
        )
        if product_handle == "took-bag":
            product_handle = "took-bag-1"
        logger.info(f"product_handle: {product_handle}")
        product_id = sgc.product_id_by_handle(product_handle)
    else:
        product_id = sgc.product_id_by_title(product_title)

    local_paths = []
    variant_image_positions = []

    for drive_id, skus in zip(drive_ids, skuss):
        variant_image_positions.append(len(local_paths))
        local_paths += sgc.drive_images_to_local(
            drive_id,
            images_local_dir,
            download_filename_prefix=f"{image_prefix}_{skus[0]}_",
        )

    sgc.upload_and_assign_images_to_product(product_id, local_paths)

    for skus, image_position in zip(skuss, variant_image_positions):
        sgc.assign_image_to_skus_by_position(product_id, image_position, skus)


def products_info_from_sheet(client: utils.Client, sheet_name):
    rows = client.worksheet_rows(client.sheet_id, sheet_name)
    # start_row 1 base, columns are 0 base
    if client.shop_name == "kumej":
        title_column_index = 2
        color_column_index = 15
        sku_column_index = 18
        link_column_index = 16
        start_row = 103
    elif client.shop_name == "gbhjapan":
        title_column_index = 5
        color_column_index = 6
        sku_column_index = 8
        link_column_index = 14
        start_row = 3
    elif client.shop_name == "alvanas":
        title_column_index = 1
        color_column_index = 9
        sku_column_index = 12
        link_column_index = 10
        start_row = 2
    elif client.shop_name == "rawrowr":
        title_column_index = 1
        color_column_index = 12
        sku_column_index = 16
        link_column_index = 14
        start_row = 3
    elif client.shop_name == "rohseoul":
        state_column_index = 0
        title_column_index = 4
        color_column_index = 9
        sku_column_index = 5
        link_column_index = 15
        start_row = 3
    elif client.shop_name == "archive-epke":
        title_column_index = 3
        color_column_index = 8
        sku_column_index = 4
        link_column_index = 14
        start_row = 3
    else:
        raise RuntimeError(f"unknown shop {client.shop_name}")

    products = []
    current_product_title = ""

    for row_num, row in enumerate(rows[start_row - 1 :]):  # Skip headers
        if client.shop_name == "rohseoul":
            state = row[state_column_index].strip()
            if state != "NEW":
                logger.info(f"skipping row {row_num}")
                continue
        elif client.shop_name == "gbhjapan":
            release = row[1]
            if not release.startswith("3/17"):
                logger.info(f"skipping row {row_num}, release is {release}")
                continue
        sku = row[sku_column_index].strip()
        if not sku:
            logger.warning(f"terminating at {row_num}, no sku")
            break
        product_title = row[title_column_index].strip()
        if not product_title:
            product_title = current_product_title
        if product_title != current_product_title:
            products.append(dict(product_title=product_title, skuss=[], links=[]))
            current_product_title = product_title
            current_color = ""
        color = row[color_column_index].strip()
        if not color:
            color = current_color
        if color != current_color:
            current_color = color
            products[-1]["skuss"].append([sku])
        else:
            products[-1]["skuss"][-1].append(sku)
        logger.info(f"retrieving link for {product_title}")
        link = client.get_link(
            client.sheet_id,
            sheet_name,
            row,
            start_row + row_num,
            link_column_index,
        )
        if link and link != "no image":
            if not link.startswith("http"):
                logger.exception(f"\n!!! malformed URL: {link} !!!\n")
            products[-1]["links"].append(link)
    return products


def main():
    client = utils.client("rawrowr")

    UPLOAD_IMAGE_PREFIX = "upload_20250409"
    IMAGES_LOCAL_DIR = (
        f"/Users/taro/Downloads/{client.shop_name}_{UPLOAD_IMAGE_PREFIX}/"
    )
    SHEET_TITLE = "20250211_v3"

    GOOGLE_CREDENTIAL_PATH = os.getenv("GOOGLE_CREDENTIAL_PATH")

    product_details = products_info_from_sheet(
        client,
        sheet_name=SHEET_TITLE,
    )

    reprocess_titles = []
    reprocess_skus = []
    reprocess_from_sku = ""

    if reprocess_from_sku:
        import itertools

        all_skus = list(
            itertools.chain(
                sku for pr in product_details for skus in pr["skuss"] for sku in skus
            )
        )
        logger.info(all_skus)
    for pr in product_details:
        if (
            all((not (reprocess_skus), not (reprocess_titles)))
            or any(sku in skus for sku in reprocess_skus for skus in pr["skuss"])
            or pr["product_title"] in reprocess_titles
        ) and (
            not reprocess_from_sku
            or reprocess_from_sku
            and any(
                all_skus.index(sku) >= all_skus.index(reprocess_from_sku)
                for skus in pr["skuss"]
                for sku in skus
            )
        ):
            drive_ids = list(
                dict.fromkeys(client.drive_link_to_id(pp) for pp in pr["links"]).keys()
            )
            logger.info(
                f"""
                  processing {pr['product_title']}
                  SKUs: {pr['skuss']}
                  Folders: {drive_ids}
                  """
            )
            process_product_images_to_shopify(
                client,
                GOOGLE_CREDENTIAL_PATH,
                UPLOAD_IMAGE_PREFIX,
                pr["product_title"],
                drive_ids,
                pr["skuss"],
                IMAGES_LOCAL_DIR,
            )


if __name__ == "__main__":
    main()
