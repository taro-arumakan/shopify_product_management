skus = [
    "OVBAX25001CHE",
    "OVBAX25001MAN",
    "OVBAX25001SBL",
    "OVBAX24502CBR",
    "OVBAX24502GOD",
]
import logging
import utils

logging.basicConfig(level=logging.DEBUG)

client = utils.client("archivépke")
client.archive_and_remove_variant_by_skus(skus, option_name="カラー")
