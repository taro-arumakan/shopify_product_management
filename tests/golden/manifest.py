"""Manifest of canonical (brand client, sheet) pairs for golden-master tests of
``to_product_inputs``.

Each case names a concrete brand client class and a representative sheet so that
the recorder (``record.py``) can capture the raw sheet rows plus the resulting
``product_inputs`` once, and ``tests/test_product_inputs_golden.py`` can replay
that recording offline. The sheet names / start rows / handle suffixes mirror the
values used in each brand's ``product_create`` script.
"""

import dataclasses
import importlib


@dataclasses.dataclass(frozen=True)
class GoldenCase:
    brand: str  # fixture file stem and pytest id
    module: str  # import path of the client class
    cls: str  # client class name
    shop_name: str  # credentials() prefix (the client's SHOPNAME)
    sheet_name: str
    start_row: int
    handle_suffix: str | None = None

    def client_class(self):
        return getattr(importlib.import_module(self.module), self.cls)

    def new_client(self):
        """Build a client without running ``__init__`` (which authenticates and
        opens network clients). Only ``product_sheet_start_row`` is needed for
        the column-map methods and ``to_product_inputs``."""
        instance = self.client_class().__new__(self.client_class())
        instance.product_sheet_start_row = self.start_row
        return instance


CASES = [
    GoldenCase(
        brand="alvana",
        module="brands.alvana.client",
        cls="AlvanaClient",
        shop_name="alvanas",
        sheet_name="26SS Product Master",
        start_row=1,
    ),
    GoldenCase(
        brand="apricotstudios",
        module="brands.apricotstudios.client",
        cls="ApricotStudiosClient",
        shop_name="apricot-studios",
        sheet_name="[Summer] 5/20",
        start_row=1,
    ),
    GoldenCase(
        brand="archivepke",
        module="brands.archivepke.client",
        cls="ArchivepkeClient",
        shop_name="archive-epke",
        sheet_name="2026.04.22(26SS Collection)",
        start_row=3,
        handle_suffix="26SS",
    ),
    GoldenCase(
        brand="blossom",
        module="brands.blossom.client",
        cls="BlossomClientClothes",
        shop_name="blossomhcompany",
        sheet_name="clothes(SS DROP 1)",
        start_row=1,
    ),
    GoldenCase(
        brand="gbh",
        module="brands.gbh.client",
        cls="GbhClient",
        shop_name="gbhjapan",
        sheet_name="26ss アパレル１次spring1차스프링오픈(COLOR+SIZE)",
        start_row=1,
    ),
    GoldenCase(
        brand="kume",
        module="brands.kume.client",
        cls="KumeClient",
        shop_name="kumej",
        sheet_name="26SS_3次_4月6日",
        start_row=2,
    ),
    GoldenCase(
        brand="lememe",
        module="brands.lememe.client",
        cls="LememeClientApparel",
        shop_name="lememek",
        sheet_name="0520_RTW_summer",
        start_row=1,
    ),
    GoldenCase(
        brand="rohseoul",
        module="brands.rohseoul.client",
        cls="RohseoulClient",
        shop_name="rohseoul",
        sheet_name="26ss 2nd(NEW)",
        start_row=2,
        handle_suffix="26ss_2nd",
    ),
    GoldenCase(
        brand="ssil",
        module="brands.ssil.client",
        cls="SsilClient",
        shop_name="ssilkr",
        sheet_name="APPAREL",
        start_row=1,
    ),
]

CASES_BY_BRAND = {case.brand: case for case in CASES}
