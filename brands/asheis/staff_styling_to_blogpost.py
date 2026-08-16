"""Process a staff styling submission into a hidden Styling blog article.

Triggered by .github/workflows/staff_styling_article.yml on a
``repository_dispatch`` event of type ``staff-styling-submission``, sent by the
Apps Script in brands/asheis/staff_styling/Code.gs. The payload arrives via the
CLIENT_PAYLOAD env var:

    {
      "submission": {
        "response_id": str,
        "submitted_at": str,          # ISO 8601
        "respondent_email": str,
        "staff": {"name": str, "display_name": str, "height": str,
                  "instagram": str, "shop": str, "is_new": bool},
        "caption": str,
        "manual_skus": [str, ...],    # fallback when tag photos are unusable
        "styling_photo_ids": [str, ...],   # Drive file ids, first is the cover
        "tag_photo_ids": [str, ...],       # Drive file ids of price-tag photos
        "spreadsheet_id": str
      }
    }

Prototype status: validates and logs the payload only. The processing steps
below are stubbed and will be implemented next:

1. download photos from Drive with the service account
   (the form's "File responses" folders must be shared with the SA email)
2. decode JAN barcodes from tag photos; JAN == SKU for ASHEIS, so resolve
   variants with client.variant_by_sku, merging in manual_skus
3. convert HEIC to JPEG and resize styling photos
4. upload images to Shopify Files, create the article hidden in the Styling
   blog ("styling" template), author/tag = staff display name, set the
   Styling - * metafields
5. email the outcome to NOTIFYEES_STAFF_STYLING via send_smtp_email
"""

import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_submission():
    payload = json.loads(os.environ["CLIENT_PAYLOAD"])
    submission = payload["submission"]
    for key in ("staff", "styling_photo_ids", "tag_photo_ids"):
        assert key in submission, f"missing key in submission: {key}"
    return submission


def main():
    submission = parse_submission()
    staff = submission["staff"]
    logger.info(
        "staff: %s (%s) new=%s shop=%s",
        staff["name"],
        staff["display_name"],
        staff["is_new"],
        staff["shop"],
    )
    logger.info("styling photos: %s", len(submission["styling_photo_ids"]))
    logger.info("tag photos: %s", len(submission["tag_photo_ids"]))
    logger.info("manual skus: %s", submission["manual_skus"])
    logger.info("caption: %s", submission["caption"])
    logger.info(
        "respondent: %s submitted_at: %s",
        submission["respondent_email"],
        submission["submitted_at"],
    )
    logger.info(
        "prototype: payload received and validated, processing not implemented yet"
    )


if __name__ == "__main__":
    main()
