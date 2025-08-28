import datetime
import logging
import pprint
import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_IMAGE_PREFIX = f"uplaod{datetime.date.today():%Y%m%d}_rohseoul_"
IMAGES_LOCAL_DIR = f"/Users/taro/Downloads/{datetime.date.today():%Y%m%d}/"


def main():
    client = utils.client("rohseoul")
    rows = client.worksheet_rows(client.sheet_id, "25FW 1ST")
    sku_column_index = 6
    state_column_index = 1
    drive_link_column_index = 16
    restart_from_sku = None  # "JLL00CC8SBK"
    started = False
    for row in rows:
        sku = row[sku_column_index]
        if (not restart_from_sku) or (sku == restart_from_sku):
            started = True
        if started and row[state_column_index] == "CO":
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
