import datetime
import logging
import string
import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_IMAGE_PREFIX = f"uplaod{datetime.date.today():%Y%m%d}_gbh"
IMAGES_LOCAL_DIR = f"/Users/taro/Downloads/{datetime.date.today():%Y%m%d}/"

skus = ["APA3JK040BKFF", "APA3CD020BKFF", "APA3CD020RDFF", "APA3CD020MGFF"]


def main():
    client = utils.client("gbhjapan")
    rows = client.worksheet_rows(client.sheet_id, "APPAREL 25FW (FALL 1次)")
    sku_column_index = string.ascii_lowercase.index("i")
    drive_link_column_index = string.ascii_lowercase.index("o")
    for row in rows:
        sku = row[sku_column_index]
        if sku in skus:
            drive_id = client.drive_link_to_id(row[drive_link_column_index])
            if drive_id:
                logger.info(f"going to process: {sku} - {drive_id}")
                client.replace_images_by_sku(
                    sku,
                    drive_id,
                    IMAGES_LOCAL_DIR,
                    download_filename_prefix=f"{UPLOAD_IMAGE_PREFIX}_{sku}_",
                )


if __name__ == "__main__":
    main()
