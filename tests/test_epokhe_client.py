"""Offline tests for EpokheClient. No network, no credentials.

Instantiating via __new__ skips BrandClientBase.__init__, which would otherwise
build Google and Shopify clients -- the same trick tests/golden/manifest.py uses.
"""

import pytest

from brands.leisureallstars.client import EpokheClient, to_shopify_product_title


@pytest.fixture
def client():
    instance = EpokheClient.__new__(EpokheClient)
    instance.product_sheet_start_row = 11
    return instance


@pytest.mark.parametrize(
    "style, colour, expected",
    [
        ("TRINITY", "BLACK POLISHED / BLACK", "TRINITY BLKP/BLK"),
        ("DOME", "GUN METAL POLISHED / BLACK PORALIZED", "DOME GUNMTLP/BLKP"),
        ("VOID", "CRYSTAL DARK TORTOISE POLISHED / BRONZE", "VOID CRYDKTORP/BRZ"),
        ("CORE CAP", "WASHED BLACK", "CORE CAP WSHBLK"),
        # A doubled space in a hand-maintained cell must not break the split.
        ("DYLAN  ZERO", "MAPLE POLISHED  / BROWN", "DYLAN ZERO MAPP/BRN"),
        ("STEREO", "TORTOISE POLISHED / GREEN POLARIZED ", "STEREO TORP/GRNP"),
        # The whole point of the codebook: these four no longer collide.
        ("DOME", "BLACK POLISHED / BLACK", "DOME BLKP/BLK"),
        ("DOME", "BROWN POLISHED / BROWN", "DOME BRNP/BRN"),
        ("CORE CAP", "WASH BROWN", "CORE CAP WSHBRN"),
        ("SUPERSTAR", "BROWN POLISHED / BROWN", "SUPERSTAR BRNP/BRN"),
    ],
)
def test_to_shopify_product_title(style, colour, expected):
    assert to_shopify_product_title(style, colour) == expected


def test_to_shopify_product_title_ignores_a_trailing_slash():
    # A stray trailing slash carries no colour, so it is dropped rather than
    # producing an empty code.
    assert to_shopify_product_title("DYLAN", "BLACK POLISHED /") == "DYLAN BLKP"


def test_colour_codes_are_unambiguous():
    from brands.leisureallstars.client import COLOUR_CODES

    # Any two colour words sharing a code must be spelling variants of the same
    # word -- SMOKE/SMOKED, WASH/WASHED, HAVANA/HAVANNA.
    by_code = {}
    for word, code in COLOUR_CODES.items():
        by_code.setdefault(code, []).append(word)
    for code, words in by_code.items():
        if len(words) > 1:
            stems = {w[:4] for w in words}
            assert len(stems) == 1, f"{code} is shared by unrelated words: {words}"


def test_column_maps_group_by_sku(client):
    product_map = client.product_attr_column_map()
    # The first key groups consecutive rows into one product, so it must be the
    # per-row-unique SKU; style would merge a style's colourways into one product.
    assert next(iter(product_map)) == "sku"
    assert product_map == dict(sku=0, style=1, colour=2, lens=3, price=6, stock=13)


def test_option_map_names_the_shopify_option(client):
    option_map = client.option1_attr_column_map()
    # The first key becomes the option NAME; 142 of 143 live EPOKHE products
    # use "Color".
    assert next(iter(option_map)) == "Color"
    # sku/price/stock are repeated from product level on purpose: option dicts
    # feed the variant, product level feeds get_sku_stocks_map.
    assert set(option_map) == {"Color", "sku", "price", "stock"}
    assert client.option2_attr_column_map() == {}


@pytest.mark.parametrize(
    "row, expected",
    [
        (["9005-LTTORPOBRZ", "COIL", "LIGHT TORTOISE POLISHED / BRONZE"], True),
        (["TOTAL", "", ""], False),  # the sheet's totals row
        (["", "", ""], False),
        (["9005-X", "COIL", ""], False),  # no colour -> would break option grouping
        (["9005-X"], False),  # short row
    ],
)
def test_is_data_row(client, row, expected):
    assert bool(client.is_data_row(row)) is expected


def test_headwear_is_detected_by_sku_prefix(client):
    assert client.is_headwear({"sku": "EPK-090-OS-S126"})
    assert not client.is_headwear({"sku": "9012-BLKPOBLK"})


def test_product_type_follows_the_store(client):
    assert client.product_type_for({"sku": "9012-BLKPOBLK"}) == "サングラス"
    # Matches the AFENDS cap already on the store.
    assert client.product_type_for({"sku": "EPK-090-OS-S126"}) == "メンズキャップ"


def test_tags_split_by_category_and_carry_the_lens(client):
    eyewear = client.get_tags_from_product_input(
        {"sku": "9003-TORPOGRNP", "style": "STEREO", "lens": "POLARIZED"}
    )
    assert eyewear == ["all", "EPØKHE EYEWEAR", "sunglasses", "STEREO", "Polarized"]
    # The sheet spells it both ways; the store tag is "Polarized".
    assert "Polarized" in client.get_tags_from_product_input(
        {"sku": "9003-X", "style": "STEREO", "lens": "POLARISED"}
    )
    headwear = client.get_tags_from_product_input(
        {"sku": "EPK-090-OS-S126", "style": "CORE CAP", "lens": ""}
    )
    assert headwear == ["all", "HEADWEAR", "CORE CAP"]
