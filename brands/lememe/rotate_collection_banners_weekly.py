"""Rotate the LEMEME top-page collection banners to the next numbered images.

Below the hero, the TOP page has a `collection-list` section whose `collection`
blocks (BAGS VIEW ALL / CLOTHES VIEW ALL) each show a numbered
<name>_view_all_N image, e.g.
    "image": "shopify://shop_images/bags_view_all_3.jpg"
    "image": "shopify://shop_images/clothes_view_all_3.jpg"
Each run advances every such banner by one (3 -> 4 -> ...) and wraps back to 1
when the next file is not in Content > Files, so the banners cycle.

The numbers are not zero-padded (bags_view_all_1 ... bags_view_all_8), unlike
the top banner's tb_<season>_pc_01.

Each banner cycles independently — bags wraps when bags_view_all_<N+1> is
missing, clothes when clothes_view_all_<N+1> is — so the two sets may hold
different numbers of images. The <name> is read from the live URL rather than
hard-coded, and the blocks are found by filename rather than by position.

NOT idempotent by design: every execute=True run advances one step, so a retried
or duplicated trigger skips a banner. Cosmetic here; if it ever matters, derive
the index from the date instead of incrementing.

Wire from Shopify Flow -> `run_func` GitHub Action (the weekly cadence lives in
the Flow trigger; this script just advances one step per run):
    script_path  brands/lememe/rotate_collection_banners_weekly.py
    func_name    rotate_collection_banners
    params       {"execute": true}
"""

import logging
import re

import utils

BANNER_URL_PATTERN = re.compile(
    r"shopify://shop_images/[a-z0-9]+_view_all_(?P<index>\d+)\.jpg$"
)


def rotate_collection_banners(execute=False, theme_name=None):
    """run_func entrypoint. Dry run unless execute=True."""
    logging.basicConfig(level=logging.INFO)
    return utils.client("lememe").rotate_theme_images(
        BANNER_URL_PATTERN,
        section_type="collection-list",
        block_type="collection",
        wrap_to=1,
        theme_name=theme_name,
        dry_run=not execute,
    )


if __name__ == "__main__":
    rotate_collection_banners()
