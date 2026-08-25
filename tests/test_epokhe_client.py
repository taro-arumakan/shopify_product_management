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
        ("TRINITY", "BLACK POLISHED / BLACK", "TRINITY BP/B"),
        ("DOME", "GUN METAL POLISHED / BLACK PORALIZED", "DOME GMP/BP"),
        ("VOID", "CRYSTAL DARK TORTOISE POLISHED / BRONZE", "VOID CDTP/B"),
        ("CORE HAT", "WASHED BLACK", "CORE HAT WB"),
        # A doubled space in a hand-maintained cell must not produce an empty
        # initial -- this is why the rule uses split() rather than split(" ").
        ("DYLAN  ZERO", "MAPLE POLISHED  / BROWN", "DYLAN ZERO MP/B"),
        ("STEREO", "TORTOISE POLISHED / GREEN POLARIZED ", "STEREO TP/GP"),
    ],
)
def test_to_shopify_product_title(style, colour, expected):
    assert to_shopify_product_title(style, colour) == expected


def test_to_shopify_product_title_rejects_empty_segment():
    with pytest.raises(AssertionError):
        to_shopify_product_title("DYLAN", "BLACK POLISHED /")


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


def test_product_type_refuses_to_guess_for_headwear(client):
    assert client.product_type_for({"sku": "9012-BLKPOBLK"}) == "サングラス"
    with pytest.raises(AssertionError, match="HEADWEAR_PRODUCT_TYPE"):
        client.product_type_for({"sku": "EPK-090-OS-S126"})


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
        {"sku": "EPK-090-OS-S126", "style": "CORE HAT", "lens": ""}
    )
    assert headwear == ["all", "CORE HAT"]
