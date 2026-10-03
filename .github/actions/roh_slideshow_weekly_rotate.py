"""ROH Seoul: トップ Slideshow の週次画像 URL を更新する。

Unlike the ASHEIS / LEMEME banners this does not wrap: when next week's images
are not in Files yet, the slideshow stays on the current week.

Run weekly by .github/workflows/roh_slideshow_weekly_rotate.yml.
"""

import argparse
import logging
import re

import utils

logging.basicConfig(level=logging.INFO)

# ROH の週次 Slideshow 画像のシーズン（キャンペーン）prefix。
# シーズンが変わったらここを更新する（例: "26_fall", "27_spring"）。
# ファイル名形式: {prefix}_pc_{N}w.jpg / {prefix}_m_{N}w.jpg
ROH_SEASON_PREFIX = "26_fall"

WEEKLY_URL_PATTERN = re.compile(
    rf"shopify://shop_images/{re.escape(ROH_SEASON_PREFIX)}_(pc|m)_"
    r"(?P<index>\d+)w\.(jpg|jpeg|png|webp)$",
    re.IGNORECASE,
)


def main():
    parser = argparse.ArgumentParser(
        description="ROH Seoul: トップ Slideshow の週次画像 URL を更新する。"
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    utils.client("roh").rotate_theme_images(
        WEEKLY_URL_PATTERN,
        section_type="slideshow",
        block_type="image",
        setting_keys=("image", "mobile_image"),
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
