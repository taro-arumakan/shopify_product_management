import datetime
import logging
import pathlib
import string
import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_IMAGE_PREFIX = f"uplaod{datetime.date.today():%Y%m%d}_rohseoul_"
IMAGES_LOCAL_DIR = f"{pathlib.Path.home()}/Downloads/{datetime.date.today():%Y%m%d}/"


def main():
    client = utils.client("rohseoul")
    rows = client.worksheet_rows(client.sheet_id, "26ss 1rd(CO)")[2:]
    sku_column_index = string.ascii_lowercase.index("f")
    drive_link_column_index = string.ascii_lowercase.index("q")
    for row in rows:
        sku = row[sku_column_index]
        drive_id = client.drive_link_to_id(row[drive_link_column_index])
        if drive_id:
            logger.info(f"going to process: {sku} - {drive_id}")
            client.replace_images_by_skus(
                [sku],
                drive_id,
                IMAGES_LOCAL_DIR,
                filename_prefix=f"{UPLOAD_IMAGE_PREFIX}_{sku}_",
            )


if __name__ == "__main__":
    main()
