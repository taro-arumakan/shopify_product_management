import logging

from brands.apricotstudios.client import ApricotStudiosClient

logging.basicConfig(level=logging.INFO)

STOCK_ADD_MAP: dict[str, int] = {
    "BCSE622BS-411BL18M": 1,
    "APTO622SL-107NA090": 1,
    "APTO622SL-107NA110": 1,
    "APTO622SL-107NA120": 1,
    "APBO622SP-208BL120": 1,
    "BCSE622SE-416MU12M": 1,
    "BCBO622SP-207BE18M": 4,
    "APTO622TS-113RE090": 1,
    "APTO622SL-122IV110": 4,
    "APBO622SP-213BL090": 4,
    "APBO622PT-207BL130": 4,
    "BCAC52NBI-500BE0FR": 3,
    "BCAC52NBI-500BL0FR": 2,
    "APAC423BI-013GY0FR": 3,
    "APAC423BI-013BL0FR": 3,
    "BCAC52NBI-502BR0FR": 19,
    "BCAC62NBI-599BR0FR": 50,
    "BCAC62NBI-599IV0FR": 37,
    "BCAC62NBI-599CH0FR": 45,
    "BCAC62NBI-503BL0FR": 61,
    "BCAC52NBI-507BL0FR": 2,
    "BCAC52NBI-507PU0FR": 3,
    "BCBO621PT-204LB12M": 1,
    "BCBO621PT-204MB12M": 4,
    "BCBO621PT-204MB18M": 1,
    "BCSE621BS-403BL06M": 4,
    "BCSE621BS-403BL12M": 4,
    "BCSE621BS-403BL18M": 4,
    "BCSE621BS-403PK12M": 4,
    "BCSE621BS-402PK12M": 1,
    "BCSE621BS-400NA06M": 2,
    "BCSE621BS-400NA12M": 2,
    "BCBO621SP-201IV18M": 4,
    "BCSE621BS-401BL18M": 1,
    "BCBO621PT-205BL12M": 4,
    "BCBO621PT-202EM18M": 1,
    "BCAC621HA-501MG048": 2,
    "BCAC621HA-501MG050": 2,
    "BCAC621HA-501PK046": 2,
    "BCSE621BS-405YE06M": 2,
    "BCTO621TS-102MG12M": 2,
    "BCTO621TS-103MG18M": 5,
    "APTO621TS-122NA120": 2,
    "APBO621PT-200YE100": 2,
    "APTO621TS-105OR120": 2,
    "APBO621SP-205OR090": 2,
    "APAC621HA-504NA050": 2,
    "APAC621HA-504BE050": 2,
    "APTO621TS-111CA090": 2,
    "APTO621TS-111CA120": 4,
    "APTO621TS-115NA090": 2,
    "APTO621TS-115NA120": 2,
    "APTO621TS-115LA100": 2,
    "APTO621TS-115MG100": 2,
    "APBO621PT-209BL110": 2,
    "APAC621SO-500BL00S": 2,
    "APAC621SO-500CH00S": 2,
    "APTO621TS-118NA100": 4,
    "APTO621TS-118OT120": 2,
    "APAC621SO-501PK00M": 2,
    "JOTO621TS-101CH090": 2,
    "JOTO621TS-101CH100": 4,
    "APLF52NBA-802BL0FR": 5,
    "APLF52NBA-802PK0FR": 9,
    "BCLF52NGD-803PK0FR": 1,
    "BCLF52NGD-802BL0FR": 1,
    "APLF223BA-007GR0FR": 1,
    "APLF223BA-007BR0FR": 2,
    "APLF223BA-007BL0FR": 2,
    "APLF422BA-001BK0FR": 4,
    "APLF52NGD-898GY0FR": 2,
    "MCET322ET-001BL0FR": 2,
}


def main(testrun=True):
    client = ApricotStudiosClient()
    location_id = client.location_id_by_name(client.LOCATIONS[0])

    for sku, add_qty in STOCK_ADD_MAP.items():
        variant = client.variant_by_sku(sku)
        current_qty = variant.get("inventoryQuantity") or 0
        new_qty = current_qty + add_qty
        logging.info(
            "%s: %s + %s = %s%s",
            sku,
            current_qty,
            add_qty,
            new_qty,
            " [DRY]" if testrun else "",
        )
        if not testrun:
            client.set_inventory_quantity_by_sku_and_location_id(
                sku, location_id, new_qty
            )


if __name__ == "__main__":
    main(testrun=False)
