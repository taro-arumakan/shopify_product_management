"""Rotate the ASHEIS top-page hero banner to the next numbered image.

The TOP page's hero is a `slideshow` section, and the banner is the `image`
block in it whose image is a numbered tb_NN file, e.g.
    "image": "shopify://shop_images/tb_00.jpg"
Each run advances the number by one (tb_00 -> tb_01 -> ...) and wraps back to
tb_00 when the next file is not in Content > Files, so the banners cycle.

The slideshow's other blocks carry one-off announcement images, so the banner
block is found by the tb_NN filename rather than by its position in the slides.

Only the main image changes: mobile is forced to 393:762 by CSS, so there is no
separate mobile image to keep in step.

NOT idempotent by design: every execute=True run advances one step, so a retried
or duplicated trigger skips a banner. Cosmetic here; if it ever matters, derive
the index from the date instead of incrementing.

Wire from Shopify Flow -> `run_func` GitHub Action (the every-two-weeks cadence
lives in the Flow trigger; this script just advances one step per run):
    script_path  brands/asheis/rotate_topbanner_biweekly.py
    func_name    rotate_topbanner
    params       {"execute": true}
"""

import logging
import re

import utils

BANNER_URL_PATTERN = re.compile(r"shopify://shop_images/tb_(?P<index>\d\d)\.jpg$")


def rotate_topbanner(execute=False, theme_name=None):
    """run_func entrypoint. Dry run unless execute=True."""
    logging.basicConfig(level=logging.INFO)
    return utils.client("asheis").rotate_theme_images(
        BANNER_URL_PATTERN,
        section_type="slideshow",
        block_type="image",
        pad=2,
        wrap_to=0,
        theme_name=theme_name,
        dry_run=not execute,
    )


if __name__ == "__main__":
    rotate_topbanner()
