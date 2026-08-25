"""Offline tests for EpokheClient. No network, no credentials.

Instantiating via __new__ skips BrandClientBase.__init__, which would otherwise
build Google and Shopify clients -- the same trick tests/golden/manifest.py uses.
"""

import pytest

from brands.leisureallstars.client import (
    STYLE_TITLES,
    EpokheClient,
    style_title,
    to_shopify_product_title,
)


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


@pytest.mark.parametrize(
    "style, expected",
    [
        # The sheet shouts; the store title-cases the collaborator.
        ("STEREO x EITHAN OSBORNE", "STEREO x Eithan Osborne"),
        ("REPRISE  x JACK FREESTONE", "Reprise x Jack Freestone"),
        ("GUILTY x THOMAS TOWNEND", "GUILTY x Thomas Townend"),
        # Not a collaboration, so the sheet's own spelling stands.
        ("WILSON", "WILSON"),
        ("DYLAN  ZERO", "DYLAN ZERO"),
    ],
)
def test_style_title(style, expected):
    assert style_title(style) == expected


def test_seo_title(client):
    assert (
        client.seo_title("WILSON ARMGRNP/GRN", "Army Green Polished / Green")
        == "WILSON ARMGRNP/GRN - Army Green Polished / Green"
    )


def test_collection_gid_for_uses_the_base_style(client):
    # A collaboration belongs in the base style's collection, so only the part
    # before the "x" is looked up.
    client._collections = {"GUILTY": "gid://shopify/Collection/1", "DOME": "gid://2"}
    assert client.collection_gid_for("GUILTY x THOMAS TOWNEND") == (
        "gid://shopify/Collection/1"
    )
    assert client.collection_gid_for("DOME") == "gid://2"


def test_collection_gid_for_returns_none_when_the_collection_is_missing(client):
    # 12 of the new styles have no collection yet; the metafield is left unset
    # rather than pointing at the wrong one.
    client._collections = {"GUILTY": "gid://shopify/Collection/1"}
    assert client.collection_gid_for("CORE CAP") is None


def test_style_titles_keys_are_normalised():
    # style_title looks the key up upper-cased with whitespace collapsed, so a
    # key that is not already in that form would never match.
    for key in STYLE_TITLES:
        assert key == " ".join(key.split()).upper()


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
