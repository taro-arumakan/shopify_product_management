"""EPOKHE-specific sanity checks.

EPOKHE's images do not come from a Drive link column in the sheet, they come
from local files resolved by :mod:`brands.leisureallstars.image_mapping`. The
inherited :meth:`SanityChecks.check_images_link` walks the sheet's option
structure looking for ``drive_link`` and raises ``KeyError: 'options'`` on the
way, which the base swallows into an unhelpful one-liner -- so it is replaced
wholesale here.
"""

import logging

from brands.leisureallstars import image_mapping

logger = logging.getLogger(__name__)

#: Every colourway shot so far has 5-6 images; fewer suggests a partial download.
EXPECTED_MIN_IMAGES = 4


class EpokheSanityChecks:
    """Mixin. Must be listed BEFORE BrandClientBase so it wins the MRO."""

    def check_images_link(self, product_inputs):
        errors = []
        for product_input in product_inputs:
            sku = product_input["sku"]
            label = f"{sku} ({product_input.get('title', '?')})"
            source = image_mapping.image_source(sku)
            if source is None:
                errors.append(f"no image_mapping entry for {label}")
                continue
            _path, _prefix, confidence, note = source
            if confidence == image_mapping.TODO:
                errors.append(f"image source unresolved for {label}: {note}")
                continue
            files = image_mapping.local_files(sku)
            if not files:
                errors.append(
                    f"no local files for {label} -- run "
                    f"`python -m brands.leisureallstars.verify_local_images`"
                )
            elif len(files) < EXPECTED_MIN_IMAGES:
                # The threshold exists to catch a partial download of the share.
                # A storefront-sourced folder holds exactly what the brand
                # publishes, so a short set there is expected, not broken.
                if image_mapping.STOREFRONT_DIR in (_path or ""):
                    logger.warning(
                        f"only {len(files)} images for {label}, but that is all "
                        f"epokhe.co publishes"
                    )
                else:
                    errors.append(f"only {len(files)} local images for {label}")
            if confidence == image_mapping.CHECK:
                # A warning, not an error: sanity_check_product_inputs raises on
                # any non-empty return, and these are eyeball items not blockers.
                logger.warning(f"image mapping needs confirming: {label} -- {note}")
        return errors
