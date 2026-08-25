"""SKU -> Dropbox image folder mapping for the EPOKHE 2026-08 drop (SOH260818-EPOKHE).

EPOKHE's Dropbox has no consistent folder convention: depth varies from 2 to 6
levels, colourway folders are named inconsistently (``COIL - LIGHT TORTOISE``,
``COIL_ARMY_GREEN_BLACK``, ``COIL-TORTOISE_GREEN_POLARIZED`` all sit side by
side), and some styles keep every colourway's files flat in one folder,
distinguished only by a SKU-ish filename prefix. So the mapping below is
curated by hand; ``brands/leisureallstars/data/dropbox_eyewear_tree.tsv`` holds
the crawled inventory it was derived from.

Each entry is ``sku -> (path, prefix, confidence, note)``:

* ``path``      folder path relative to :data:`EYEWEAR_ROOT` (or to the share
                root when it starts with ``/``).
* ``prefix``    when the folder is shared by several colourways, only files
                whose name starts with this prefix belong to this SKU.
                ``None`` means take every image in the folder.
* ``confidence``  ``exact``   SKU appears verbatim in the filenames
                  ``high``    SKU matches apart from a typo in the source files
                  ``check``   inferred from colour names, please eyeball once
                  ``todo``    not resolved, needs a human
* ``note``      why, whenever the mapping is not self-evident.

Only the 49 rows highlighted yellow in the master sheet are listed.
"""

SHARED_LINK_ROOT = "https://www.dropbox.com/scl/fo/z0gsgmn2qasobxu8e1pdx/h"
EYEWEAR_ROOT = "/1_EYEWEAR/1_COLLECTION"
HEADWEAR_ROOT = "/2_OBJECTS"

#: Images for four headwear SKUs are absent from the Dropbox share. They were
#: taken instead from EPOKHE's own storefront, which serves the same 2882x3600
#: web-res exports -- the brand and the shop owner have a standing agreement
#: covering EPOKHE marketing in Japan. Their paths start with this prefix so it
#: is obvious at a glance where they came from.
STOREFRONT_DIR = "/from_epokhe_co"

EXACT, HIGH, CHECK, TODO = "exact", "high", "check", "todo"

#: Sheet ``スタイル`` value -> Dropbox style folder under :data:`EYEWEAR_ROOT`.
#: Collaboration styles share the base style's folder.
STYLE_FOLDER = {
    "COIL": "33_COIL",
    "DOME": "45_DOME",
    "EMBER": "42_EMBER",
    "FREQUENCY X AUSTYN GILLETTE": "29_FREQUENCY",
    "GUILTY": "12_GUILTY",
    "GUILTY X THOMAS TOWEND": "12_GUILTY",
    "JACUZZZI X JALEESSA VINCENT": "43_JACUZZI",
    "PANO": "41_PANO",
    "REALM": "34_REALM",
    "REPRISE X JACK FREESTONE": "23_REPRISE",
    "STEREO": "26_STEREO",
    "STEREO X EITHAN OSBORNE": "26_STEREO",
    "TRINITY": "1_TRINITY",
    "VOID": "32_VOID",
}

_TRINITY_WEB = "1_TRINITY/1_ECOMMERCE/1_PRODUCT_SHOTS/2_UPDATED/WEB RES (2882x3600)"

#: sku -> (path, prefix, confidence, note)
SKU_IMAGE_SOURCE = {
    # --- COIL -------------------------------------------------------------
    "9005-LTTORPOBRZ": ("33_COIL/COIL - LIGHT TORTOISE/Web", None, EXACT, ""),
    # --- DOME -------------------------------------------------------------
    # All four colourways share one flat folder; the filename prefix selects.
    "9012-BLKPOBLK": ("45_DOME/WEB_RES_DOME", "9012-BLKPOBLK", EXACT, ""),
    "9012-BRNPOBRN": ("45_DOME/WEB_RES_DOME", "9012-BRNPOBRN", EXACT, ""),
    "9012-DKTORPOGRN": (
        "45_DOME/WEB_RES_DOME",
        "9012-DKTOPROGRN",
        HIGH,
        "files are misspelled DKTOPROGRN (letters transposed)",
    ),
    "9012-GUNMPOBLKP": (
        "45_DOME/WEB_RES_DOME",
        "9012-GUMMPOBLKP",
        HIGH,
        "files are misspelled GUMM (double M) for GUNM",
    ),
    # --- EMBER ------------------------------------------------------------
    # Files are named SUNNY <n>-<nn>.jpg; only the folder identifies the colour.
    "9006-BLKPOBLK": (
        "42_EMBER/WEB RES JPEG (2882x3600) 2/BLACK_PO_BLK",
        None,
        HIGH,
        "confirmed against epokhe.co/products/ember-black-polished-black",
    ),
    "9006-DKTORPOBRZP": (
        "42_EMBER/WEB RES JPEG (2882x3600) 2/DKTOR_PO_BRZP",
        None,
        HIGH,
        "confirmed against"
        "epokhe.co/products/ember-dark-tortoise-polished-bronze-polarized",
    ),
    "9006-BRNPOBRN": (
        "42_EMBER/WEB RES JPEG (2882x3600) 2/MAP_PO_BRN",
        None,
        HIGH,
        "folder is misnamed MAP (maple) but holds the brown colourway -- confirmed"
        "against epokhe.co/products/ember-brown-polished-brown",
    ),
    # --- FREQUENCY x AUSTYN GILLETTE -------------------------------------
    "1000-OLVPOJDE": (
        "29_FREQUENCY/FREQUENCY_OLIVE/WEB_RES_FREQUENCY_OLIVE",
        None,
        HIGH,
        "files are 2000-OLVPOIDE-*.jpg: 2000 style prefix and I/J both differ",
    ),
    "1000-AMBPOTORGRN": (
        "29_FREQUENCY/FREQUENCY_AMBER_TORTOISE/WEB_RES",
        None,
        HIGH,
        "files are 2000-AMTORPOGRN-*.jpg: 2000 style prefix, AMTOR for AMBPOTOR",
    ),
    # --- GUILTY -----------------------------------------------------------
    "1025-CRTORPOBRNP": (
        "12_GUILTY/1_ECOMMERCE/Guilty - Crystal Dark Tortoise Polished : Brown Polarized"
        "/web jpegs 2882x3600",
        None,
        EXACT,
        "",
    ),
    "1025-MAPPOBRN": ("12_GUILTY/1_ECOMMERCE/GUILTY_MAPLE_TT/WEB RES", None, EXACT, ""),
    # --- JACUZZZI x JALEESSA VINCENT -------------------------------------
    # One flat folder, files named JUJU THICK <COLOUR>-<n>.jpg, no SKU anywhere.
    # The folder holds a third colourway (PINK) that was not ordered.
    "9013-BLKPOBLK": (
        "43_JACUZZI/WEB_RES",
        "JUJU THICK BLACK",
        HIGH,
        "confirmed against"
        "epokhe.co/products/jacuzzi-x-jalessa-vincent-black-polished-black",
    ),
    "9013-DKTORPOBRN": (
        "43_JACUZZI/WEB_RES",
        "JUJU THICK TAN",
        HIGH,
        "TAN is the DARK TORTOISE / BROWN colourway -- confirmed against epokhe.co."
        "The unused JUJU THICK PINK set is 9013-PIKPOPIKI, not in this order",
    ),
    # --- PANO -------------------------------------------------------------
    "9011-BLKPOBLKP": ("41_PANO/2_BLACK_PO_BLK/WEB JPEG", None, EXACT, ""),
    "9011-DKTORPOBRN": ("41_PANO/3_DARK_TORTOISE/WEB", None, EXACT, ""),
    "9011-AGRNPOGRN": ("41_PANO/1_ARMY_GREEN/WEB JPEG", None, EXACT, ""),
    # --- REALM ------------------------------------------------------------
    # 34_REALM holds two vintages of the same colourways; REALM NEW is current.
    "1232-BLKPOBLKP": (
        "34_REALM/REALM NEW/Realm - Black Polished Black/WEB RES (2882x3600)",
        None,
        EXACT,
        "superseded folder REALM_BLACK_POLISHED_BLACK also exists",
    ),
    "1232-DKTORPOBRZ": (
        "34_REALM/REALM NEW/Realm - Dark Tortoise Polished Bronze/FULL SIZE (6000x7495)",
        None,
        EXACT,
        "this colourway has no WEB RES folder, only FULL SIZE",
    ),
    "1232-GUNMPOBLK": (
        "34_REALM/REALM_GUNMETAL_POLISHED_BLACK/WEB RES (2882x3600)",
        None,
        HIGH,
        "files are 1232-GUNPOBLK-*.jpg, missing the M of GUNM",
    ),
    # --- REPRISE x JACK FREESTONE ----------------------------------------
    "9002-CRTORPOBRZ": (
        "23_REPRISE/Reprise - JF - Crystal Dark Tortoise/Web",
        None,
        EXACT,
        "",
    ),
    # --- STEREO -----------------------------------------------------------
    "9003-LTTORPOBRZP": (
        "26_STEREO/Stereo - Light Tortoise/Web",
        None,
        HIGH,
        "files are 9003 LYYOROBRZP-*.jpg -- LYYORO is a typo for LTTOR",
    ),
    "9003-ICDGPOGRY": (
        "26_STEREO/STEREO_ICE_GREY/WEB_RES_ICE_GREY",
        None,
        HIGH,
        "files are 9003-ICDPOGRY-*.jpg, missing the G of ICDG",
    ),
    "9003-BLKPOBRZP": (
        "26_STEREO/STEREO_BLACK_BRONZE/WEB_RES_STEREO_BLACK_BRONZE",
        None,
        EXACT,
        "",
    ),
    # --- TRINITY ----------------------------------------------------------
    # Three colourways flat in one folder, selected by filename prefix.
    "0993-BLKPOBLK": (
        _TRINITY_WEB,
        "0993-BLKPOBLK",
        EXACT,
        "NOTE: this SKU is already live on the store as 'TRINITY BP/B' -- "
        "do not create, it is highlighted yellow by mistake",
    ),
    "0993-MTFSTREDI": (_TRINITY_WEB, "0993-MTFSTREDI", EXACT, ""),
    "0993-RTBPOLBRZI": (
        _TRINITY_WEB,
        "0993-RTVPOLBRZI",
        HIGH,
        "files read RTV where the sheet reads RTB",
    ),
    # --- VOID -------------------------------------------------------------
    "1212-BLKPOBLK": (
        "32_VOID/VOID_BLACK_POLISHED_BLACK/1_WEB_RES",
        None,
        HIGH,
        "files are 1212BLK0BLK-*.jpg -- digit zero used instead of letter O",
    ),
    "1212-CRTORPOBRZ": (
        "32_VOID/VOID_CRYSTAL_DARK_TORTOISE_BRONZE/1_WEB_RES",
        None,
        EXACT,
        "",
    ),
}

# --------------------------------------------------------------------------
# Headwear.
#
# The real hat photography is NOT in /43_HATS_JUNE_25_INTERNAL_FLATLAY (those
# are internal flatlays) nor in the owner's Drive folder "OBJECTS 5.0" (those
# are on-model lookbook shots). It lives under /2_OBJECTS, in the same
# FULL SIZE / WEB RES layout the eyewear uses, split across two season folders
# whose names do NOT line up with the SKUs' own season code -- SKUs ending
# -S126 appear in both HATS_COLLECTION_S126 and HATS_COLLECTION_S226.
#
# S126 uses one folder per colourway (files inside are named "HAT <n>-<nn>.jpg",
# so the folder is the only signal). S226 keeps every colourway flat in one
# folder, selected by filename prefix.
# --------------------------------------------------------------------------

_HAT_S126 = "/2_OBJECTS/HATS_COLLECTION_S126/WEB RES (2882x3600)"
_HAT_S226 = "/2_OBJECTS/HATS_COLLECTION_S226/WEB RES (2882x3600)"

_NAMING = "sheet and brand folder disagree on the style name"

SKU_IMAGE_SOURCE.update(
    {
        # --- CORE HAT ---------------------------------------------------------
        "EPK-090-OS-S126": (
            f"{_HAT_S126}/EPOKHE CORE CAP - WASHED BLACK",
            None,
            HIGH,
            f"{_NAMING}: sheet CORE HAT vs folder CORE CAP",
        ),
        "EPK-091-OS-S126": (
            _HAT_S226,
            "EPOKHE ACORE CAP WASHED BLACKCAMO-",
            HIGH,
            "in the S226 folder despite the -S126 SKU; files read ACORE for CORE",
        ),
        "EPK-128-OS-S126": (
            _HAT_S226,
            "EPOKHE ACORE CAP CLASSIC CAMO-",
            HIGH,
            "in the S226 folder despite the -S126 SKU; files read ACORE for CORE",
        ),
        "EPK-092-OS-S126": (
            f"{STOREFRONT_DIR}/EPK-092-OS-S126",
            None,
            HIGH,
            "3 images, taken from"
            "epokhe.co/products/epokhe-core-cap-wash-brown-pink-logo -- not in the"
            "Dropbox share",
        ),
        # --- ASHFALL CAP ------------------------------------------------------
        "EPK-094-OS-S126": (
            f"{_HAT_S126}/EPOKHE ASHFALL CAP - WASHED BLACK",
            None,
            HIGH,
            "",
        ),
        "EPK-096-OS-S126": (
            f"{_HAT_S126}/EPOKHE ASHFALL CAP - WASHED PINK REAL TREE",
            None,
            HIGH,
            "",
        ),
        "EPK-095-OS-S126": (
            _HAT_S226,
            "NO CODE HAT",
            HIGH,
            "filed under the placeholder name NO CODE HAT in the S226 folder --"
            "confirmed against"
            "epokhe.co/products/epokhe-ashfall-cap-washed-real-tree-camo",
        ),
        # --- INFERNO CAP ------------------------------------------------------
        "EPK-099-OS-S126": (
            f"{_HAT_S126}/EPOKHE INFERNO CAP - DEAD BERRY",
            None,
            HIGH,
            "",
        ),
        "EPK-098-OS-S126": (
            _HAT_S226,
            "EPOKHE INFERNO CAP WASHED BLK PINK REAL TREE CAMO-",
            HIGH,
            "in the S226 folder despite the -S126 SKU",
        ),
        # --- STELLAR CAP ------------------------------------------------------
        # S126 has STELLAR *BEANIE* folders; the CAP shots are in S226.
        "EPK-101-OS-S126": (
            _HAT_S226,
            "EPOKHE STELLAR CAP BLACK-",
            HIGH,
            "in the S226 folder; S126 only has STELLAR BEANIE, a different product",
        ),
        "EPK-102-OS-S126": (
            _HAT_S226,
            "EPOKHE STELLAR CAP WASHED REAL TREE CAMO-",
            HIGH,
            "in the S226 folder; S126 only has STELLAR BEANIE, a different product",
        ),
        # --- TUNDRA TRACKER CAP ----------------------------------------------
        "EPK-105-OS-S126": (
            f"{_HAT_S126}/EPOKHE TUNDRA TRUCKER CAP - WASHED BLACK",
            None,
            HIGH,
            f"{_NAMING}: sheet TUNDRA TRACKER vs folder TUNDRA TRUCKER",
        ),
        "EPK-106-OS-S126": (
            f"{_HAT_S126}/EPOKHE TUNDRA TRUCKER CAP - WASHED REAL TREE CAMO",
            None,
            HIGH,
            f"{_NAMING}: sheet TUNDRA TRACKER vs folder TUNDRA TRUCKER",
        ),
        # --- CAVE TRUCKER -----------------------------------------------------
        "EPK-110-OS-S126": (
            f"{_HAT_S126}/EPOKHE CAVE TRUCKER - BLACK CHARCOAL",
            None,
            HIGH,
            "",
        ),
        "EPK-111-OS-S126": (
            f"{_HAT_S126}/EPOKHE CAVE TRUCKER - DEAD BERRY",
            None,
            HIGH,
            "sheet says DEAD BERRY / TAN, folder says DEAD BERRY",
        ),
        # --- THOMAS TOWNEND ART SERIES HAT -----------------------------------
        "EPK-060-OS": (
            f"{_HAT_S126}/Epokhe Thomas Townend Art Series Cap - CONCRETE CAMO",
            None,
            HIGH,
            "",
        ),
        "EPK-023-OS": (
            f"{_HAT_S126}/Epokhe Thomas Townend Art Series Cap - CHOCOLATE COPPER",
            None,
            HIGH,
            "folder is misnamed CHOCOLATE but holds the maroon colourway -- confirmed"
            "against"
            "epokhe.co/products/epokhe-thomas-townend-art-series-hat-maroon-copper",
        ),
        "EPK-021-OS": (
            f"{STOREFRONT_DIR}/EPK-021-OS",
            None,
            HIGH,
            "6 images, taken from"
            "epokhe.co/products/epokhe-thomas-townend-art-series-hat-black-off-white"
            "-- not in the Dropbox share",
        ),
        "EPK-087-OS": (
            f"{STOREFRONT_DIR}/EPK-087-OS",
            None,
            HIGH,
            "5 images, taken from"
            "epokhe.co/products/epokhe-thomas-townend-art-series-hat-camo-yellow --"
            "not in the Dropbox share",
        ),
        "EPK-089-OS": (
            f"{STOREFRONT_DIR}/EPK-089-OS",
            None,
            HIGH,
            "6 images, taken from"
            "epokhe.co/products/epokhe-thomas-townend-art-series-hat-khaki-pink -- not"
            "in the Dropbox share",
        ),
    }
)

#: Folders searched for headwear, for the record. HATS_COLLECTION_1..6 hold
#: older seasons with anonymous filenames ("Hat 4-01.jpg") and were not mined;
#: the 5 TODO SKUs above are the likeliest residents.
HEADWEAR_SEARCHED = (
    "/2_OBJECTS/HATS_COLLECTION_S126",
    "/2_OBJECTS/HATS_COLLECTION_S226",
    "/43_HATS_JUNE_25_INTERNAL_FLATLAY",  # internal flatlays, unindexed
    "https://drive.google.com/drive/folders/106SIKgJwNCz_M72wZLriqpgjs9bc-cr_",  # lookbook
)


def image_source(sku):
    """Return ``(path, prefix, confidence, note)`` for ``sku``, or None."""
    return SKU_IMAGE_SOURCE.get(sku.strip())


def dropbox_url(sku):
    """Return the Dropbox browse URL for ``sku``'s image folder, or None."""
    source = image_source(sku)
    if not source or not source[0]:
        return None
    path = source[0]
    if not path.startswith("/"):
        path = f"{EYEWEAR_ROOT}/{path}"
    return f"{SHARED_LINK_ROOT}{path}"


def unresolved_skus():
    """SKUs whose image folder still needs a human decision."""
    return [s for s, v in SKU_IMAGE_SOURCE.items() if v[2] in (CHECK, TODO)]


# --------------------------------------------------------------------------
# Resolving a mapping entry to files on a local copy of the Dropbox share.
#
# The share was downloaded folder-by-folder rather than as one tree, so the
# local layout is flatter than the Dropbox one: the two headwear season
# folders both arrived as "WEB RES (2882x3600)", the second suffixed "-2".
# Matching is done on a normalised name (Unicode NFC, case-folded, and with the
# characters macOS rewrites in filenames neutralised) so a path copied from
# Dropbox still resolves on disk.
# --------------------------------------------------------------------------

import os
import unicodedata

DEFAULT_LOCAL_ROOT = "/Volumes/TOSHIBA/EPOKHE"

#: Places a copy of the share may live. The first complete pull of the eyewear
#: tree is TOSHIBA/EPOKHE/1_COLLECTION -- earlier attempts downloaded through
#: Safari and silently omitted ~63% of the files, so several partial copies are
#: still lying around. Resolution walks every root and every plausible base and
#: takes the first that actually holds images, so a stale partial copy alongside
#: a complete one is harmless.
LOCAL_ROOTS = (
    "/Volumes/TOSHIBA/EPOKHE",
    "/Users/taro/Downloads",
)

#: Sub-paths under a root at which the eyewear collection may sit.
_EYEWEAR_BASES = ("1_COLLECTION", "1_EYEWEAR/1_COLLECTION", "")

#: Dropbox path prefix -> path relative to the local root.
LOCAL_ROOT_MAP = {
    f"{_HAT_S126}": "WEB RES (2882x3600)",
    f"{_HAT_S226}": "WEB RES (2882x3600)-2",
}

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")


def _norm(name):
    """Normalise a path segment for comparison across Dropbox and macOS."""
    name = unicodedata.normalize("NFC", name).casefold()
    # macOS swaps ":" and "/" in filenames; collapse both plus whitespace runs.
    for ch in ":/":
        name = name.replace(ch, " ")
    return " ".join(name.split())


def _descend(base, segments):
    """Walk `segments` under `base`, matching each on its normalised name."""
    current = base
    for segment in segments:
        if not segment:
            continue
        candidate = os.path.join(current, segment)
        if os.path.isdir(candidate):
            current = candidate
            continue
        try:
            entries = os.listdir(current)
        except OSError:
            return None
        target = _norm(segment)
        match = next((e for e in entries if _norm(e) == target), None)
        if match is None:
            return None
        current = os.path.join(current, match)
    return current


def local_dir(sku, root=DEFAULT_LOCAL_ROOT):
    """Return the local directory holding ``sku``'s images, or None."""
    source = image_source(sku)
    if not source or not source[0]:
        return None
    path = source[0]
    for prefix, local in LOCAL_ROOT_MAP.items():
        if path == prefix:
            return os.path.join(root, local)
        if path.startswith(prefix + "/"):
            return _descend(
                os.path.join(root, local), path[len(prefix) + 1 :].split("/")
            )
    for candidate in _candidate_dirs(sku, root):
        return candidate
    return None


def _candidate_dirs(sku, root):
    """Yield every directory under `root` that could hold ``sku``'s images."""
    source = image_source(sku)
    if not source or not source[0]:
        return
    path = source[0]
    for prefix, local in LOCAL_ROOT_MAP.items():
        if path == prefix or path.startswith(prefix + "/"):
            base = os.path.join(root, local)
            rest = path[len(prefix) + 1 :]
            found = (
                _descend(base, rest.split("/"))
                if rest
                else (base if os.path.isdir(base) else None)
            )
            if found:
                yield found
            return
    if path.startswith("/"):
        found = _descend(root, path.lstrip("/").split("/"))
        if found:
            yield found
        return
    segments = path.split("/")
    for base in _EYEWEAR_BASES:
        directory = os.path.join(root, base) if base else root
        if not os.path.isdir(directory):
            continue
        found = _descend(directory, segments)
        if found:
            yield found


def local_files(sku, root=None):
    """Return ``sku``'s image files on disk, in filename order.

    Honours the entry's filename prefix when one folder holds several
    colourways. With no ``root``, searches :data:`LOCAL_ROOTS` in order and
    returns the first non-empty result. Returns [] when nothing is found.
    """
    source = image_source(sku)
    if not source or not source[0]:
        return []
    prefix = _norm(source[1]) if source[1] else None
    roots = (root,) if root else LOCAL_ROOTS
    for candidate_root in roots:
        for directory in _candidate_dirs(sku, candidate_root):
            files = [
                os.path.join(directory, name)
                for name in sorted(os.listdir(directory))
                if name.lower().endswith(IMAGE_EXTENSIONS)
                and not name.startswith(".")
                and (prefix is None or _norm(name).startswith(prefix))
            ]
            if files:
                return files
    return []
