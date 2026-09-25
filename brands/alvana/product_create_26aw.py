"""OT-28: process the alvana 26AW Product Master sheet.

Rules, from the ticket plus the decisions taken on 2026-09-24:

- stocks are never touched; variants created here start at 0
- an SKU that already exists only ever gains images, appended at the end, and only
  images that are genuinely new -- the 26AW drive folders are renamed re-exports of the
  26SS shots, so a file name alone proves nothing; see ImageHasher.new_drive_images
- a new product or colourway with images is registered live; without images it goes to
  the '(no image)' UNLISTED twin, as in the 26SS run
- a colourway parked in a twin that now has images is promoted onto the live product,
  carrying its stock over, and dropped from the twin
- everything this script changes is written back to column T (変更情報) of the sheet

Run with DRY_RUN = True first: it prints the plan and writes nothing.
"""

import collections
import datetime
import logging
import pathlib
import re
import string
import urllib.request

from PIL import Image

from brands.alvana.client import AlvanaClient
from helpers.exceptions import NoProductsFoundException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SHEET_NAME = "26AW Product Master"
SEASON_TAG = "26aw"
DRY_RUN = True
COLUMN_T = string.ascii_uppercase.index("T") + 1  # 変更情報, 1-based for gspread

CACHE_DIR = pathlib.Path.home() / "Downloads" / "alvana_26aw_image_cache"
# Hamming distance over a 256-bit dHash, used only on files whose name is not already on
# the product. Measured: a 26AW re-export of a 26SS shot lands at 0-10, and a genuinely
# different shot of the same garment at 58+. Re-encoding drifts further than that gap
# suggests -- our own 2026-09-24 uploads read 13-26 against their drive originals -- which
# is why the name test comes first and this threshold stays tight.
SAME_IMAGE_DISTANCE = 12

# Restrict a run to these sheet products; empty means the whole sheet. The plan is still
# built for everything, so the log shows what is being left for later.
ONLY = set()

# Products held back pending confirmation from the brand (see OT-28). Both the
# consolidation and the BLUE images it needed are done, so nothing is held here now.
ON_HOLD = {}

# Single colourways held back, where the rest of the product is fine.
ON_HOLD_COLOURS = {}

# The sheet spells khaki KAHKI; the shop has said KHAKI since 25FW, and the storefront
# filter vocabulary only knows KHAKI and GRAY.
COLOUR_ALIASES = {"KAHKI": "KHAKI"}
FILTER_COLOUR_ALIASES = {"KAHKI": "KHAKI", "TOP GRAY": "GRAY"}

# What can happen to one colourway.
CREATE_LIVE = "create live product"
CREATE_TWIN = "create/extend (no image) twin"
ADD_COLOURWAY = "add colourway to live product"
PROMOTE = "promote out of (no image) twin"
APPEND_IMAGES = "append new images"
NOTHING = "no change"
HELD = "on hold"

# Column T (変更情報) notes, written back to the colourway's first row.
NOTE_NEW = "画像あり新規登録"
NOTE_NO_IMAGE = "画像未入稿のため非公開で登録"
NOTE_APPEND = "画像追加"
NOTE_PROMOTE = "画像登録により公開商品へ移動（在庫引継ぎ済）"
NOTE_ADD_COLOUR = "既存商品に新色として追加"


class Plan(
    collections.namedtuple(
        "Plan", "title colour action skus images shop_title detail note"
    )
):
    def __str__(self):
        skus = (
            f"{self.skus[0]}..{self.skus[-1][-1]}"
            if len(self.skus) > 1
            else self.skus[0]
        )
        images = f"{len(self.images)} image(s)" if self.images else ""
        return (
            f"  {self.colour:12} {self.action:30} {skus:24} {images:12} {self.detail}"
        )


def dhash(image, size=16):
    """Row-wise gradient hash: tolerant of re-encoding and resizing, not of content."""
    grey = image.convert("L").resize((size + 1, size), Image.Resampling.LANCZOS)
    pixels = list(grey.getdata())
    bits = []
    for row in range(size):
        line = pixels[row * (size + 1) : (row + 1) * (size + 1)]
        bits += [line[i] > line[i + 1] for i in range(size)]
    return sum(1 << i for i, bit in enumerate(bits) if bit)


def distance(a, b):
    return bin(a ^ b).count("1")


def normalise_name(name):
    """A drive filename reduced to what survives an upload: Shopify rewrites dots and
    spaces, so compare on alphanumerics alone."""
    return re.sub(r"[^0-9a-z]", "", name.rsplit(".", 1)[0].lower())


def media_name(url):
    """An uploaded image's filename, normalised.

    Not stripped of its prefix: every upload path here names the file
    <prefix>_<seq>_<drive name>, but the prefixes differ per script (upload_<date>_<sku>_,
    append_, insert_, black_, ink_black_) and a regex per convention is a standing
    invitation to miss one. The drive name is always the tail, so callers match on that
    with is_already_on_product instead. Guessing wrong here is not harmless: an unmatched
    name falls through to the content test, where our own re-uploads read 13-26 and get
    re-uploaded as duplicates.
    """
    return normalise_name(url.split("/")[-1].split("?")[0])


def is_already_on_product(drive_filename, media_names):
    """Whether a drive file is among the product's images, by name."""
    tail = normalise_name(drive_filename)
    return any(name.endswith(tail) for name in media_names)


class ImageHasher:
    """dHashes of drive originals and of what is already on the shop, cached on disk."""

    def __init__(self, client):
        self.client = client
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def shop(self, url):
        path = CACHE_DIR / ("s_" + url.split("/")[-1].split("?")[0])
        if not path.exists():
            urllib.request.urlretrieve(url, path)
        return dhash(Image.open(path))

    def drive(self, file_id):
        # download_and_process_image renames by image mode, so take the path it returns
        cached = list(CACHE_DIR.glob(f"d_{file_id}.*"))
        path = (
            cached[0]
            if cached
            else pathlib.Path(
                self.client.download_and_process_image(
                    file_id, str(CACHE_DIR / f"d_{file_id}.img")
                )
            )
        )
        return dhash(Image.open(path))

    def new_drive_images(self, drive_link, product):
        """Drive files of this colourway that are not already on the product.

        Two tests, because neither is sufficient alone. An upload keeps the drive file's
        name at the end of its own, so a name match is proof the file is already there --
        content alone would not tell, since Shopify re-encodes on upload and our own
        re-uploads drift 13-26 from the original. And a content match catches the opposite
        case, the 26AW folders being renamed re-exports of the 26SS shots, where the names
        share nothing.
        """
        files = sorted(
            self.client.get_drive_image_details(
                self.client.drive_link_to_id(drive_link)
            ),
            key=lambda f: f["name"],
        )
        images = [m["image"] for m in product["media"]["nodes"] if m.get("image")]
        names = {media_name(image["url"]) for image in images}
        new = []
        for f in files:
            if is_already_on_product(f["name"], names):
                continue
            closest = min(
                (
                    distance(self.drive(f["id"]), self.shop(image["url"]))
                    for image in images
                ),
                default=999,
            )
            if closest > SAME_IMAGE_DISTANCE:
                new.append((f, closest))
        return files, new


def shop_index(client):
    """sku -> (product, variant) over the live catalogue.

    Archived products are left out on purpose: retiring a product by archiving it leaves
    its SKUs behind (Shopify keeps no product without a variant), and an archived hit
    would make a colourway that is already live look like it still needs moving.
    """
    query = """query($after:String){ products(first:100, after:$after){
      pageInfo{hasNextPage endCursor}
      nodes{ id title handle status tags
        media(first:100){nodes{... on MediaImage{ image{ url } }}}
        variants(first:100){nodes{ id sku title inventoryQuantity }} } } }"""
    products, after = [], None
    while True:
        page = client.run_query(query, {"after": after})["products"]
        products += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            break
        after = page["pageInfo"]["endCursor"]
    return {
        variant["sku"]: (product, variant)
        for product in products
        if product["status"] != "ARCHIVED"
        for variant in product["variants"]["nodes"]
        if variant["sku"]
    }


def incomplete_skus(product_input):
    """True when any size row of any colourway is missing its 品番."""
    return any(
        not size_option.get("sku")
        for colour_option in product_input["options"]
        for size_option in colour_option["options"]
    )


def live_title_of(product_input, by_sku):
    """The live product this sheet product already exists as, if it does.

    A colourway whose SKUs are nowhere in the shop is only a new product when the rest of
    the sheet product is new too; when a sibling colourway is already live, the colourway
    is a new colour on that product, not a second product under the same name.
    """
    for colour_option in product_input["options"]:
        for size_option in colour_option["options"]:
            if hit := by_sku.get(size_option.get("sku")):
                product = hit[0]
                return product["title"].replace(" (no image)", "")
    return None


def plan_colour(product_input, colour_option, by_sku, hasher, live_title=None):
    """Decide what happens to one colourway of one sheet product."""
    title = product_input["title"]
    colour = colour_option["カラー"]
    skus = [o["sku"] for o in colour_option["options"] if o.get("sku")]
    drive_link = colour_option.get("drive_link", "no image")
    has_images = drive_link != "no image"
    hits = [by_sku[sku] for sku in skus if sku in by_sku]

    def plan(action, images=(), shop_title=None, detail="", note=None):
        return Plan(
            title, colour, action, skus or ["-"], list(images), shop_title, detail, note
        )

    if held := ON_HOLD.get(title) or ON_HOLD_COLOURS.get((title, colour)):
        return plan(HELD, detail=held)
    if incomplete_skus(product_input):
        # The SKU is the product's identity here, and the sheet is filled in by hand over
        # days: a product with a gap is still being typed, so leave all of it alone rather
        # than registering the colourways that happen to be done.
        return plan(
            HELD, detail="品番未記入の色があるため保留 - sheet entry unfinished"
        )

    if not hits:  # this colourway is nowhere in the shop yet
        if live_title and has_images:
            return plan(
                ADD_COLOURWAY,
                shop_title=live_title,
                detail=f"new colour on {live_title!r}",
                note=NOTE_ADD_COLOUR,
            )
        if has_images:
            return plan(CREATE_LIVE, note=NOTE_NEW)
        return plan(CREATE_TWIN, note=NOTE_NO_IMAGE)

    product = hits[0][0]
    is_twin = "(no image)" in product["title"]
    carried = ", ".join(
        f"{sku}:{variant['inventoryQuantity']}"
        for sku, (_, variant) in zip(skus, hits)
        if variant["inventoryQuantity"]
    )

    if is_twin and has_images:
        # the images land on the live product, so compare them against that one
        live_title = product["title"].replace(" (no image)", "")
        live = next((p for p, _ in by_sku.values() if p["title"] == live_title), None)
        _, new = hasher.new_drive_images(drive_link, live or product)
        return plan(
            PROMOTE,
            images=[f["name"] for f, _ in new],
            shop_title=live_title,
            detail=f"out of {product['title']!r}"
            + (f", stock {carried}" if carried else ""),
            note=NOTE_PROMOTE,
        )
    if is_twin:
        return plan(
            NOTHING,
            shop_title=product["title"],
            detail=f"stays in {product['title']!r}",
        )
    if has_images:
        files, new = hasher.new_drive_images(drive_link, product)
        if not new:
            return plan(
                NOTHING,
                shop_title=product["title"],
                detail=f"{len(files)} drive file(s) already on {product['title']!r}",
            )
        return plan(
            APPEND_IMAGES,
            images=[f["name"] for f, _ in new],
            shop_title=product["title"],
            detail=f"append to {product['title']!r}",
            note=NOTE_APPEND,
        )
    return plan(
        NOTHING, shop_title=product["title"], detail=f"live in {product['title']!r}"
    )


class Alvana26AWClient(AlvanaClient):
    """The 26AW sheet carries no 寸法 and no 重さ yet: the size table is skipped rather
    than fed an empty string (formatted_size_text_to_html_table raises on one), and
    update_weight already no-ops without a weight."""

    def update_metafields(self, product_id, product_input):
        if product_input.get("size_text"):
            return super().update_metafields(product_id, product_input)
        logger.info(f'no 寸法 for {product_input["title"]} - skipping the size table')
        self.update_product_care_metafield(
            product_id, self.text_to_simple_richtext(product_input["product_care"])
        )
        self.update_filter_color(product_id, product_input)


def load_product_inputs(client):
    """Sheet rows, with the colour spellings normalised to the shop's vocabulary."""
    product_inputs = client.product_inputs_by_sheet_name(SHEET_NAME)
    for product_input in product_inputs:
        for colour_option in product_input["options"]:
            colour_option["sheet_colour"] = colour_option["カラー"]
            colour_option["カラー"] = COLOUR_ALIASES.get(
                colour_option["カラー"], colour_option["カラー"]
            )
            colour_option["filter_color"] = FILTER_COLOUR_ALIASES.get(
                colour_option["filter_color"], colour_option["filter_color"]
            )
    return product_inputs


def build_plan(client, product_inputs):
    by_sku = shop_index(client)
    hasher = ImageHasher(client)
    return collections.OrderedDict(
        (
            product_input["title"],
            [
                plan_colour(
                    product_input,
                    colour_option,
                    by_sku,
                    hasher,
                    live_title_of(product_input, by_sku),
                )
                for colour_option in product_input["options"]
            ],
        )
        for product_input in product_inputs
    )


def note_rows(client):
    """(title, colour) -> sheet row, so column T can be annotated per colourway."""
    worksheet = client.gspread_client.open_by_key(client.sheet_id).worksheet(SHEET_NAME)
    rows, title = {}, None
    for row_number, row in enumerate(worksheet.get_all_values()[1:], 2):
        if row[1].strip():
            title = " ".join(row[1].split())
        colour = row[11].strip()
        if title and colour:
            rows[(title, colour)] = row_number
            rows[(title, COLOUR_ALIASES.get(colour, colour))] = row_number
    return worksheet, rows


def write_note(worksheet, rows, plan):
    row = rows.get((plan.title, plan.colour))
    if not row:
        logger.warning(
            f"no sheet row for {plan.title} / {plan.colour}; note not written"
        )
        return
    note = f"{datetime.date.today():%Y-%m-%d} {plan.note}"
    logger.info(f"  column T row {row}: {note}")
    if not DRY_RUN:
        worksheet.update_cell(row, COLUMN_T, note)


def colour_subset(product_input, plans):
    """The sheet product narrowed to the colourways of these plans."""
    colours = {p.colour for p in plans}
    return dict(
        product_input,
        options=[o for o in product_input["options"] if o["カラー"] in colours],
    )


def create_live(client, product_input, plans):
    subset = colour_subset(product_input, plans)
    res = client.process_product_input(subset)
    client.post_process_product_input(res, subset)
    client.activate_and_publish_by_product_id(res["create_product"]["id"])
    return res


def create_twin(client, product_input, plans):
    subset = colour_subset(product_input, plans)
    subset["title"] += " (no image)"
    try:
        client.products_by_title(subset["title"])
    except NoProductsFoundException:
        pass
    else:
        raise RuntimeError(f"{subset['title']!r} already exists; extend it by hand")
    res = client.create_product_by_product_input(
        subset, client.VENDOR, description_html="", tags=[SEASON_TAG]
    )
    client.update_product_status(res["id"], "UNLISTED")
    client.enable_and_activate_inventory_by_product_input(subset, client.LOCATIONS)
    client.update_stock(subset)  # every stock in this sheet is 0
    return res


def promote(client, product_input, plan, by_sku):
    """Move a colourway out of its (no image) twin onto the live product, with its stock."""
    twin, _ = by_sku[plan.skus[0]]
    live_title = plan.shop_title
    stock = {
        variant["sku"]: variant["inventoryQuantity"]
        for variant in twin["variants"]["nodes"]
        if variant["sku"] in plan.skus
    }
    subset = colour_subset(product_input, [plan])
    subset["title"] = live_title
    for colour_option in subset["options"]:
        for size_option in colour_option["options"]:
            size_option["stock"] = stock.get(size_option["sku"], 0)
    res = client.add_variants_from_product_input(subset)
    # add_variants_from_product_input does not carry metafields, and the twins never had
    # a filter colour to begin with, so the storefront filter is set here
    client.update_filter_color(client.product_id_by_title(live_title), subset)
    variant_ids = [
        variant["id"]
        for variant in twin["variants"]["nodes"]
        if variant["sku"] in plan.skus
    ]
    logger.info(
        f"  removing {len(variant_ids)} promoted variant(s) from {twin['title']!r}"
    )
    if len(variant_ids) < len(twin["variants"]["nodes"]):
        client.remove_product_variants(twin["id"], variant_ids)
    else:
        # Shopify keeps no product without a variant: the emptied twin is archived, not
        # deleted, so it can be restored if a colourway comes back image-less.
        logger.info(f"  {twin['title']!r} has no colourway left - archiving it")
        client.update_product_status(twin["id"], "ARCHIVED")
    return res


def add_colourway(client, product_input, plan):
    """A new colour on a product that is already live: variants at 0 stock, its own
    images, and the storefront filter colour."""
    subset = colour_subset(product_input, [plan])
    subset["title"] = plan.shop_title
    for colour_option in subset["options"]:
        for size_option in colour_option["options"]:
            size_option["stock"] = 0
    res = client.add_variants_from_product_input(subset)
    client.update_filter_color(client.product_id_by_title(plan.shop_title), subset)
    return res


def append_images(client, product_input, plan):
    """Upload only the genuinely new drive files, appended after the existing media."""
    colour_option = next(
        o for o in product_input["options"] if o["カラー"] == plan.colour
    )
    product_id = client.product_id_by_title(plan.shop_title)
    # drive_images_to_local makes its own directory; downloading file by file does not
    local_dir = pathlib.Path.home() / "Downloads" / f"{client.shop_name}_26aw"
    local_dir.mkdir(parents=True, exist_ok=True)
    drive_id = client.drive_link_to_id(colour_option["drive_link"])
    wanted = set(plan.images)
    files = [f for f in client.get_drive_image_details(drive_id) if f["name"] in wanted]
    local_paths = [
        client.download_and_process_image(
            f["id"], str(local_dir / f"append_{plan.skus[0]}_{seq:03}_{f['name']}")
        )
        for seq, f in enumerate(sorted(files, key=lambda f: f["name"]))
    ]
    # remove_existings=False keeps the 26SS shots and their variant assignments in place
    return client.upload_and_assign_images_to_product(product_id, local_paths, False)


def execute(client, product_inputs, plans):
    by_sku = shop_index(client)
    worksheet, rows = note_rows(client)
    for product_input in product_inputs:
        colour_plans = plans[product_input["title"]]
        actions = collections.Counter(p.action for p in colour_plans)
        if ONLY and product_input["title"] not in ONLY:
            if set(actions) - {NOTHING, HELD}:
                logger.info(
                    f'{product_input["title"]}: not in ONLY, left for later: {dict(actions)}'
                )
            continue
        logger.info(f'{product_input["title"]}: {dict(actions)}')
        for plan in colour_plans:
            if plan.action == HELD:
                logger.info(f"  {plan.colour}: on hold, skipped - {plan.detail}")
        # a held colourway holds back only itself; its siblings still go through
        colour_plans = [p for p in colour_plans if p.action != HELD]
        for action, handler in (
            (CREATE_LIVE, create_live),
            (CREATE_TWIN, create_twin),
        ):
            batch = [p for p in colour_plans if p.action == action]
            if batch and not DRY_RUN:
                handler(client, product_input, batch)
        for plan in colour_plans:
            if DRY_RUN:
                break
            if plan.action == PROMOTE:
                promote(client, product_input, plan, by_sku)
            elif plan.action == ADD_COLOURWAY:
                add_colourway(client, product_input, plan)
            elif plan.action == APPEND_IMAGES:
                append_images(client, product_input, plan)
        for plan in colour_plans:
            if plan.note:
                write_note(worksheet, rows, plan)


def main():
    client = Alvana26AWClient(
        product_sheet_start_row=1,
        products_season_tag=SEASON_TAG,
        remove_existing_new_product_indicators=False,
    )
    product_inputs = load_product_inputs(client)
    plans = build_plan(client, product_inputs)
    for title, colour_plans in plans.items():
        print(f"\n{title}")
        for plan in colour_plans:
            print(plan)
    print("\n--- totals")
    counts = collections.Counter(p.action for ps in plans.values() for p in ps)
    for action, count in counts.most_common():
        print(f"  {action:30} {count}")
    if DRY_RUN:
        print("\nDRY_RUN: nothing was written to the shop or the sheet.")
        return
    execute(client, product_inputs, plans)


if __name__ == "__main__":
    main()
