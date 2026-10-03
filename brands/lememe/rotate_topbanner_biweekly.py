"""Rotate the LEMEME top-page hero banner to the next numbered image pair.

The TOP page's hero is a `slideshow` section, and the banner is the `image`
block in it whose images are a numbered tb_<season>_pc_NN / tb_<season>_m_NN
pair, e.g.
    "image":        "shopify://shop_images/tb_sepoct_pc_01.jpg"
    "mobile_image": "shopify://shop_images/tb_sepoct_m_01.jpg"
Each run advances the number by one (01 -> 02 -> ...) and wraps back to 01 when
the next pair is not in Content > Files, so the banners cycle.

Both the desktop and the mobile image move together — unlike ASHEIS, LEMEME
serves a separate 2:3 mobile crop, so the pair must stay in step.

The slideshow's other blocks carry one-off announcement images, so the banner
block is found by the tb_<season>_pc_NN filename rather than by its position in
the slides.

The season token (`sepoct`) is read from the live URL rather than hard-coded:
when the next season's images go up, point the block at tb_novdec_pc_01.jpg once
in the theme editor and this script keeps cycling within the new set unchanged.

NOT idempotent by design: every execute=True run advances one step, so a retried
or duplicated trigger skips a banner. Cosmetic here; if it ever matters, derive
the index from the date instead of incrementing.

Wire from Shopify Flow -> `run_func` GitHub Action (the every-two-weeks cadence
lives in the Flow trigger; this script just advances one step per run):
    script_path  brands/lememe/rotate_topbanner_biweekly.py
    func_name    rotate_topbanner
    params       {"execute": true}
"""

import logging
import re

import utils

BANNER_URL_PATTERN = re.compile(
    r"shopify://shop_images/tb_[a-z0-9]+_(pc|m)_(?P<index>\d\d)\.jpg$"
)


def rotate_topbanner(execute=False, theme_name=None):
    """run_func entrypoint. Dry run unless execute=True."""
    logging.basicConfig(level=logging.INFO)
    return utils.client("lememe").rotate_theme_images(
        BANNER_URL_PATTERN,
        section_type="slideshow",
        block_type="image",
        setting_keys=("image", "mobile_image"),
        pad=2,
        wrap_to=1,
        theme_name=theme_name,
        dry_run=not execute,
    )


if __name__ == "__main__":
    rotate_topbanner()
