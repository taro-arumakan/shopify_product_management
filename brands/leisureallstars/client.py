"""EPOKHE on the leisureallstars store.

EPOKHE differs from the other brands in three ways that shape this class:

* **The master sheet is a wholesale order sheet**, not a product sheet. There is
  no description column, no images column, and one row per colourway.
* **Each colourway is its own product**, titled ``{STYLE} {COLOUR-INITIALS}``
  (``TRINITY BP/B``), carrying a single option named ``Color`` whose value is the
  full colour name. All 143 existing EPOKHE products on the store have exactly
  one variant and one option named ``Color``.
* **Images come from local files**, resolved by :mod:`.image_mapping` from a copy
  of the brand's Dropbox share, rather than from a Drive link in the sheet.

Product descriptions are bespoke Japanese copy per style and cannot be derived
from the order sheet. Where a style already has a live product this class reuses
its ``descriptionHtml``; where it does not, it raises rather than inventing copy.
"""

import logging
import os
import string

from brands.client.brandclientbase import BrandClientBase
from brands.leisureallstars import descriptions, image_mapping
from brands.leisureallstars.sanity_checks import EpokheSanityChecks

logger = logging.getLogger(__name__)


#: Canonical code for every colour word in the EPOKHE vocabulary.
#:
#: A single initial cannot work: BLACK, BROWN, BRONZE, BLUE, BONE, BEIGE,
#: BERRY, BLOOD, BURNT and BUTTER all begin with B, and the live catalogue
#: abbreviates BLACK as B, BK and BLK on different products. Three letters per
#: colour word is the shortest length that is unambiguous across the whole
#: vocabulary. Dropping leading qualifiers to shorten the code is not safe --
#: DARK TORTOISE POLISHED / GREEN POLARIZED and TORTOISE POLISHED / GREEN
#: POLARIZED would both become TORP/GRNP.
COLOUR_CODES = {
    "BLACK": "BLK",
    "BROWN": "BRN",
    "BRONZE": "BRZ",
    "BLUE": "BLU",
    "BONE": "BON",
    "BEIGE": "BEI",
    "BERRY": "BER",
    "BLOOD": "BLD",
    "BURNT": "BNT",
    "BUTTER": "BTR",
    "GREEN": "GRN",
    "GREY": "GRY",
    "GOLD": "GLD",
    "GRADIENT": "GRD",
    "GUN": "GUN",
    "METAL": "MTL",
    "GUNPOLISHED": "GUNP",
    "CRYSTAL": "CRY",
    "COLA": "COL",
    "CAMO": "CAM",
    "CITRINE": "CIT",
    "CARBON": "CRB",
    "CHARCOAL": "CHR",
    "CLASSIC": "CLS",
    "CONCRETE": "CNC",
    "CONTRAST": "CNT",
    "COPPER": "CPR",
    "MAPLE": "MAP",
    "MAUVE": "MAU",
    "MAROON": "MAR",
    "MARBLE": "MRB",
    "TORTOISE": "TOR",
    "TREE": "TRE",
    "TAN": "TAN",
    "TOBACCO": "TOB",
    "SMOKE": "SMK",
    "SMOKED": "SMK",
    "SILVER": "SLV",
    "SCARLET": "SCR",
    "SEPIA": "SEP",
    "STITCH": "STC",
    "REAL": "REA",
    "RAINBOW": "RBW",
    "RED": "RED",
    "ROOTBEER": "RTB",
    "ROSEWATER": "ROS",
    "IRIDIUM": "IRI",
    "IVORY": "IVY",
    "ICED": "ICE",
    "HAVANA": "HAV",
    "HAVANNA": "HAV",
    "HAZEL": "HAZ",
    "AMBER": "AMB",
    "ARMY": "ARM",
    "ANTHRACITE": "ANT",
    "OLIVE": "OLV",
    "OFF": "OFF",
    "WHITE": "WHT",
    "PINK": "PNK",
    "VELVET": "VLV",
    "WASHED": "WSH",
    "WASH": "WSH",
    "DARK": "DK",
    "LIGHT": "LT",
    "EMERALD": "EMR",
    "FOREST": "FST",
    "JADE": "JDE",
    "KHAKI": "KHK",
    "YELLOW": "YEL",
    "ZERO": "ZRO",
    "DEAD": "DED",
}

#: Finishes collapse to a single trailing letter so codes stay short.
FINISH_CODES = {
    "POLISHED": "P",
    "POLOSHED": "P",
    "POLARIZED": "P",
    "POLARISED": "P",
    "PORALIZED": "P",
    "MATTE": "M",
    "MATT": "M",
    "GLOSS": "G",
}


def colour_code(segment):
    """One slash-separated colour segment to its code.

    ``"BLACK POLISHED"`` -> ``"BLKP"``, ``"BLACK"`` -> ``"BLK"``.
    An unrecognised word falls back to its first three letters.
    """
    codes = []
    for word in segment.split():
        key = word.upper().strip(",-")
        if key in FINISH_CODES and codes:
            codes.append(FINISH_CODES[key])
        elif key in COLOUR_CODES:
            codes.append(COLOUR_CODES[key])
        elif key in FINISH_CODES:
            codes.append(FINISH_CODES[key])
        else:
            logger.warning(f"no colour code for {word!r}, using {key[:3]!r}")
            codes.append(key[:3])
    return "".join(codes)


def to_shopify_product_title(style, colour):
    """``("TRINITY", "BLACK POLISHED / BLACK")`` -> ``"TRINITY BLKP/BLK"``."""
    segments = [segment.strip() for segment in colour.split("/") if segment.strip()]
    codes = [colour_code(segment) for segment in segments]
    assert codes and all(codes), f"no colour code from {colour!r} (style {style!r})"
    return f"{' '.join(style.split())} {'/'.join(codes)}"


class EpokheClient(EpokheSanityChecks, BrandClientBase):
    """The mixin must come first so its check_images_link wins the MRO."""

    SHOPNAME = "leisureallstars"
    VENDOR = "EPOKHE"
    BRAND_NAME = "EPOKHE"
    # The store has exactly one location.
    LOCATIONS = ["一宮町東浪見"]

    #: Every live EPOKHE product uses this template.
    TEMPLATE_SUFFIX = "product-with-collection"
    EYEWEAR_PRODUCT_TYPE = "サングラス"
    #: No EPOKHE headwear exists yet, but the store already carries one cap --
    #: AFENDS "VIBRATION - ヘンプキャップ" -- typed メンズキャップ and tagged HEADWEAR.
    #: Following it keeps the collections and theme filters working.
    HEADWEAR_PRODUCT_TYPE = "メンズキャップ"
    #: Headwear SKUs are the EPK-* family; eyewear SKUs are numeric style codes.
    HEADWEAR_SKU_PREFIX = "EPK-"

    #: Tags every EPOKHE product carries, alongside the style and season tags.
    #: The base class prepends products_season_tag and NEW_PRODUCT_TAG.
    BASE_TAGS = ["all"]
    #: What the 143 live eyewear products carry.
    EYEWEAR_TAGS = ["EPØKHE EYEWEAR", "sunglasses"]
    #: Matches the AFENDS cap already on the store.
    HEADWEAR_TAGS = ["HEADWEAR"]

    #: Titles that the initials rule cannot make unique. Two colourways can
    #: collapse to the same initials -- BLACK POLISHED / BLACK and BROWN
    #: POLISHED / BROWN are both "BP/B". The live store disambiguates by
    #: inserting the colour word (e.g. "DYLAN Cola CP/B"), but which word to use
    #: is a merchandising decision, so collisions raise and are resolved here.
    TITLE_OVERRIDES = {}

    MAX_MEGAPIXELS = 15
    MAX_MB = 15
    UPLOADABLE_EXTENSIONS = (".jpg", ".jpeg", ".png")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._description_cache = {}
        self._brand_products = None

    # ------------------------------------------------------------------
    # Sheet layout.  A=SKU B=STYLE C=COLOUR D=LENS E=REMARKS F=RRP(excl)
    # G=RRP(incl tax) H=WS I=QTY J=TOTAL K=SOH L=SMS M=Streamer N=TOTAL(stock)
    # ------------------------------------------------------------------
    @staticmethod
    def _column(letter):
        return string.ascii_lowercase.index(letter)

    def product_attr_column_map(self):
        # The FIRST key groups consecutive rows into one product, so it must be
        # unique per row -- the SKU. Using style would merge a style's colourways
        # into a single product; using colour would merge across style boundaries.
        return dict(
            sku=self._column("a"),
            style=self._column("b"),
            colour=self._column("c"),
            lens=self._column("d"),
            price=self._column("g"),
            stock=self._column("n"),
        )

    def option1_attr_column_map(self):
        # The first key becomes the Shopify option NAME, so it must read "Color"
        # to match the 142 live EPOKHE products.
        # sku/price/stock are repeated from the product level because
        # populate_option_dicts reads them here while get_sku_stocks_map reads
        # them at product level; one sheet row is one product, so they agree.
        return {
            "Color": self._column("c"),
            "sku": self._column("a"),
            "price": self._column("g"),
            "stock": self._column("n"),
        }

    def option2_attr_column_map(self):
        return {}

    # ------------------------------------------------------------------
    # Title, handle, option value
    # ------------------------------------------------------------------
    @staticmethod
    def is_data_row(row):
        """True for the 113 product rows, false for TOTAL, blanks and the footer.

        The sheet's TOTAL row carries a value in column A but none in column C,
        which would start a product with an empty options list and blow up
        inside ``to_product_inputs``.
        """
        return (
            len(row) > 2
            and str(row[0]).strip()
            and str(row[0]).strip().upper() != "TOTAL"
            and str(row[2]).strip()
        )

    def product_inputs_by_sheet_name(self, sheet_name, handle_suffix=None):
        # Called directly rather than via super() so a row filter can be passed:
        # the base does not forward one, and this sheet has non-product rows.
        # handle_suffix is not forwarded either -- the base would compute the
        # handle from product_input["title"], which the pass below creates.
        self.drive_link_cache = {}
        product_inputs = self.to_product_inputs(
            self.sheet_id,
            sheet_name,
            self.product_sheet_start_row,
            product_attr_column_map=self.product_attr_column_map(),
            option1_attr_column_map=self.option1_attr_column_map(),
            option2_attr_column_map=self.option2_attr_column_map(),
            row_filter_func=self.is_data_row,
        )
        for product_input in product_inputs:
            sku = product_input["sku"]
            product_input["title"] = self.TITLE_OVERRIDES.get(
                sku,
                to_shopify_product_title(
                    product_input["style"], product_input["colour"]
                ),
            )
            product_input["handle"] = self.product_title_to_handle(
                product_input["title"], handle_suffix=handle_suffix
            )
            # The option value is the full colour name, title-cased to match the
            # live products ("Black Polished / Black").
            product_input["options"][0]["Color"] = product_input["colour"].title()
        return product_inputs

    def title_clashes(self, product_inputs):
        """Titles that are not unique within the batch, or already on the store.

        The initials rule is a good default but not a complete one: the live
        store titles Black Polished / Black as ``TRINITY BP/B`` on one style and
        ``SUPERSTAR BP/BLK`` on another, so a colliding pair needs a human
        decision recorded in :attr:`TITLE_OVERRIDES`.
        """
        within = {}
        for product_input in product_inputs:
            within.setdefault(product_input["title"], []).append(product_input["sku"])
        clashes = {
            title: {"skus": skus, "reason": "duplicate within this batch"}
            for title, skus in within.items()
            if len(skus) > 1
        }
        live = {
            product["title"].upper(): product["title"]
            for product in self.products_by_query(f"vendor:'{self.VENDOR}'")
        }
        for product_input in product_inputs:
            title = product_input["title"]
            if title.upper() in live and title not in clashes:
                clashes[title] = {
                    "skus": [product_input["sku"]],
                    "reason": f"already on the store as {live[title.upper()]!r}",
                }
        return clashes

    # ------------------------------------------------------------------
    # Attributes
    # ------------------------------------------------------------------
    def is_headwear(self, product_input):
        return product_input["sku"].upper().startswith(self.HEADWEAR_SKU_PREFIX)

    def product_type_for(self, product_input):
        if not self.is_headwear(product_input):
            return self.EYEWEAR_PRODUCT_TYPE
        assert self.HEADWEAR_PRODUCT_TYPE, (
            f"{product_input['sku']} is headwear and no HEADWEAR_PRODUCT_TYPE is set. "
            f"The store has no hat products yet, so there is no precedent to copy -- "
            f"ask the owner which productType the collections key off."
        )
        return self.HEADWEAR_PRODUCT_TYPE

    def get_tags_from_product_input(self, product_input):
        tags = list(self.BASE_TAGS)
        tags += (
            self.HEADWEAR_TAGS if self.is_headwear(product_input) else self.EYEWEAR_TAGS
        )
        tags.append(" ".join(product_input["style"].split()))
        if lens := (product_input.get("lens") or "").strip():
            # The sheet spells it both POLARIZED and POLARISED; the store tag is
            # "Polarized".
            tags.append(
                "Polarized" if lens.upper().startswith("POLAR") else lens.title()
            )
        return tags

    def get_size_field(self, product_input):
        # Eyewear and caps have no size table. Must not raise: check_size_field
        # calls this for every product.
        return ""

    # ------------------------------------------------------------------
    # Description -- reused from a live sibling colourway, never invented
    # ------------------------------------------------------------------
    def description_html_by_style(self, style):
        """``descriptionHtml`` of a live product sharing this style, or None."""
        style = " ".join(style.split()).upper()
        if style in self._description_cache:
            return self._description_cache[style]
        # Collaboration styles ("GUILTY x THOMAS TOWEND") sit under the base
        # style's tag on the store.
        base_style = style.split(" X ")[0].strip()
        if getattr(self, "_brand_products", None) is None:
            # One fetch for the whole run; a query per style is far too slow.
            self._brand_products = self.products_by_query(
                f"vendor:'{self.VENDOR}'", additional_fields=["descriptionHtml"]
            )
        products = self._brand_products
        match = None
        for candidate in products:
            tags = [t.upper() for t in candidate["tags"]]
            if (style in tags or base_style in tags) and candidate.get(
                "descriptionHtml"
            ):
                match = candidate["descriptionHtml"]
                break
        self._description_cache[style] = match
        return match

    def description_source(self, product_input):
        """``("live"|"drafted", html)`` for this product, or ``(None, None)``.

        A live sibling wins so colourways of one style cannot drift apart;
        :mod:`.descriptions` covers the styles new to the store.
        """
        style = product_input["style"]
        if live := self.description_html_by_style(style):
            return "live", live
        if drafted := descriptions.description_html(style):
            return "drafted", drafted
        return None, None

    def get_description_html(self, product_input):
        style = product_input["style"]
        _source, description = self.description_source(product_input)
        assert description, (
            f"no copy for style {style!r} ({product_input['sku']}): no live product "
            f"shares it and brands.leisureallstars.descriptions has no entry. Add one "
            f"before creating this product."
        )
        return description

    # ------------------------------------------------------------------
    # Images -- local files, not Drive
    # ------------------------------------------------------------------
    def process_product_images(
        self, product_input, local_dir=None, filename_prefix=None
    ):
        """Upload the SKU's local images. local_dir/filename_prefix are unused.

        The inherited implementation walks the sheet for a ``drive_link`` and
        raises ``KeyError: 'options'`` for this brand's shape, so it is replaced
        rather than extended.
        """
        sku = product_input["sku"]
        paths = [
            path
            for path in image_mapping.local_files(sku)
            if path.lower().endswith(self.UPLOADABLE_EXTENSIONS)
        ]
        assert paths, (
            f"no local images for {sku} ({product_input['title']}) -- run "
            f"`python -m brands.leisureallstars.verify_local_images`"
        )
        paths = [self.shrink_if_oversized(path, sku) for path in paths]
        product_id = self.product_id_by_product_input(product_input)
        logger.info(f"uploading {len(paths)} images for {product_input['title']}")
        return self.upload_and_assign_images_to_product(
            product_id, paths, remove_existings=True
        )

    def shrink_if_oversized(self, path, sku):
        """Return a path within Shopify's limits, resizing to scratch if needed.

        Never writes back to the source drive -- those are the brand's masters.
        """
        from PIL import Image

        with Image.open(path) as image:
            megapixels = image.width * image.height / 1_000_000
        megabytes = os.path.getsize(path) / (1024 * 1024)
        if megapixels <= self.MAX_MEGAPIXELS and megabytes <= self.MAX_MB:
            return path
        output_dir = os.path.join(
            os.path.expanduser("~/Downloads"), f"epokhe_resized_{sku}"
        )
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, os.path.basename(path))
        logger.warning(
            f"{os.path.basename(path)} is {megapixels:.1f}MP/{megabytes:.1f}MB, "
            f"resizing a copy to {output_path}"
        )
        return self.resize_image_to_limit(
            path, output_path, max_megapixels=self.MAX_MEGAPIXELS, max_mb=self.MAX_MB
        )

    # ------------------------------------------------------------------
    # Post-create: productType and template have no place in ProductSetInput
    # ------------------------------------------------------------------
    def post_process_product_input(self, process_product_input_res, product_input):
        product_id = process_product_input_res["create_product"]["id"]
        self.update_product_attributes(
            product_id,
            ["productType", "templateSuffix"],
            [self.product_type_for(product_input), self.TEMPLATE_SUFFIX],
        )

    # ------------------------------------------------------------------
    # Which rows are new: the sheet marks them with a yellow fill
    # ------------------------------------------------------------------
    YELLOW = (1.0, 1.0, 0.0)

    def row_background_colors(self, sheet_name, first_row=12, last_row=124, column="A"):
        """``{sheet row number: rgb tuple or None}`` for one column."""
        response = (
            self.sheets_service.spreadsheets()
            .get(
                spreadsheetId=self.sheet_id,
                ranges=f"'{sheet_name}'!{column}{first_row}:{column}{last_row}",
                includeGridData=True,
                fields="sheets(data(rowData(values(effectiveFormat(backgroundColorStyle)))))",
            )
            .execute()
        )
        row_data = response["sheets"][0]["data"][0].get("rowData", [])
        colors = {}
        for offset, row in enumerate(row_data):
            values = row.get("values") or [{}]
            style = (values[0].get("effectiveFormat") or {}).get(
                "backgroundColorStyle"
            ) or {}
            rgb = style.get("rgbColor")
            colors[first_row + offset] = (
                None
                if rgb is None
                else (
                    round(rgb.get("red", 0.0), 2),
                    round(rgb.get("green", 0.0), 2),
                    round(rgb.get("blue", 0.0), 2),
                )
            )
        return colors

    def highlighted_skus(self, sheet_name, first_row=12, last_row=124):
        """SKUs of the yellow-highlighted rows -- the owner's marker for new."""
        rows = self.worksheet_rows(self.sheet_id, sheet_name)
        colors = self.row_background_colors(sheet_name, first_row, last_row)
        skus = set()
        for row_number, rgb in colors.items():
            if rgb != self.YELLOW:
                continue
            index = row_number - 1
            if index < len(rows) and str(rows[index][0]).strip():
                skus.add(str(rows[index][0]).strip())
        return skus
