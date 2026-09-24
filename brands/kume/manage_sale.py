from brands.kume.client import KumeClient


def start_end_discounts(testrun=True, start_or_end="start"):
    """
    SS Pre Sale (0720-0731)
    """
    client = KumeClient()

    sku_discount_map = {
        "KM-26SS-TS01-IV-S": 0.9,
        "KM-26SS-TS01-IV-M": 0.9,
        "KM-26SS-TS01-IV-L": 0.9,
        "KM-26SS-TS01-BK-S": 0.9,
        "KM-26SS-TS01-BK-M": 0.9,
        "KM-26SS-TS01-BK-L": 0.9,
        "KM-26SS-SK03IVS": 0.9,
        "KM-26SS-SK03IVM": 0.9,
        "KM-26SS-SK03IVL": 0.9,
        "KM-26SS-PT03-WH-S": 0.9,
        "KM-26SS-PT03-WH-M": 0.9,
        "KM-26SS-PT03-WH-L": 0.9,
        "KM-26SS-PT02-BK-S": 0.9,
        "KM-26SS-PT02-BK-M": 0.9,
        "KM-26SS-PT02-BK-L": 0.9,
        "KM-26SS-OP01-NV-S": 0.9,
        "KM-26SS-OP01-NV-M": 0.9,
        "KM-26SS-OP01-NV-L": 0.9,
        "KM-26SS-OP01-IV-S": 0.9,
        "KM-26SS-OP01-IV-M": 0.9,
        "KM-26SS-OP01-IV-L": 0.9,
        "KM-26SS-BL05-WH-S": 0.9,
        "KM-26SS-BL05-WH-M": 0.9,
        "KM-26SS-BL05-WH-L": 0.9,
        "KM-26SS-BL05-BK-S": 0.9,
        "KM-26SS-BL05-BK-M": 0.9,
        "KM-26SS-BL05-BK-L": 0.9,
        "M-KM-26SS-TS04-NV-XL": 0.9,
        "M-KM-26SS-TS04-NV-M": 0.9,
        "M-KM-26SS-TS04-NV-L": 0.9,
        "M-KM-26SS-TS04-IV-XL": 0.9,
        "M-KM-26SS-TS04-IV-M": 0.9,
        "M-KM-26SS-TS04-IV-L": 0.9,
        "M-KM-26SS-TS04-CH-XL": 0.9,
        "M-KM-26SS-TS04-CH-M": 0.9,
        "M-KM-26SS-TS04-CH-L": 0.9,
        "M-KM-26SS-TS03-NV-XL": 0.9,
        "M-KM-26SS-TS03-NV-M": 0.9,
        "M-KM-26SS-TS03-NV-L": 0.9,
        "M-KM-26SS-TS03-GR-XL": 0.9,
        "M-KM-26SS-TS03-GR-M": 0.9,
        "M-KM-26SS-TS03-GR-L": 0.9,
        "M-KM-26SS-SW08ORM": 0.9,
        "M-KM-26SS-SW08ORL": 0.9,
        "M-KM-26SS-SW08OLM": 0.9,
        "M-KM-26SS-SW08OLL": 0.9,
        "M-KM-26SS-SW08GRM": 0.9,
        "M-KM-26SS-SW08GRL": 0.9,
        "M-KM-26SS-SW08BEM": 0.9,
        "M-KM-26SS-SW08BEL": 0.9,
        "M-KM-26SS-SW07-NV-M": 0.9,
        "M-KM-26SS-SW07-NV-L": 0.9,
        "M-KM-26SS-SW07-GR-M": 0.9,
        "M-KM-26SS-SW07-GR-L": 0.9,
        "M-KM-26SS-SW06-IV-XL": 0.9,
        "M-KM-26SS-SW06-IV-M": 0.9,
        "M-KM-26SS-SW06-IV-L": 0.9,
        "M-KM-26SS-SW06-GR-XL": 0.9,
        "M-KM-26SS-SW06-GR-M": 0.9,
        "M-KM-26SS-SW06-GR-L": 0.9,
        "M-KM-26SS-SW06-BK-XL": 0.9,
        "M-KM-26SS-SW06-BK-M": 0.9,
        "M-KM-26SS-SW06-BK-L": 0.9,
        "M-KM-26SS-PT08-LGR-XL": 0.9,
        "M-KM-26SS-PT08-LGR-M": 0.9,
        "M-KM-26SS-PT08-LGR-L": 0.9,
        "M-KM-26SS-PT07ECXL": 0.9,
        "M-KM-26SS-PT07ECM": 0.9,
        "M-KM-26SS-PT07ECL": 0.9,
        "M-KM-26SS-PT07CHXL": 0.9,
        "M-KM-26SS-PT07CHM": 0.9,
        "M-KM-26SS-PT07CHL": 0.9,
        "M-KM-26SS-PT07BEXL": 0.9,
        "M-KM-26SS-PT07BEM": 0.9,
        "M-KM-26SS-PT07BEL": 0.9,
        "M-KM-26SS-JP02GRXL": 0.9,
        "M-KM-26SS-JP02GRL": 0.9,
        "M-KM-26SS-JP02CHXL": 0.9,
        "M-KM-26SS-JP02CHL": 0.9,
        "M-KM-26SS-BL11IVXL": 0.9,
        "M-KM-26SS-BL11IVL": 0.9,
        "M-KM-26SS-BL11DGRXL": 0.9,
        "M-KM-26SS-BL11DGRL": 0.9,
        "M-KM-26SS-BL10PKXL": 0.9,
        "M-KM-26SS-BL10PKM": 0.9,
        "M-KM-26SS-BL10PKL": 0.9,
        "M-KM-26SS-BL10LGRXL": 0.9,
        "M-KM-26SS-BL10LGRM": 0.9,
        "M-KM-26SS-BL10LGRL": 0.9,
        "M-KM-26SS-BL09-DBN-XL": 0.9,
        "M-KM-26SS-BL09-DBN-L": 0.9,
        "M-KM-26SS-BL08-NV-XL": 0.9,
        "M-KM-26SS-BL08-NV-L": 0.9,
        "M-KM-26SS-BL08-IV-XL": 0.9,
        "M-KM-26SS-BL08-IV-L": 0.9,
        "KM-26SS-TS02-WH-S": 0.9,
        "KM-26SS-TS02-WH-M": 0.9,
        "KM-26SS-TS02-WH-L": 0.9,
        "KM-26SS-TS02-PK-S": 0.9,
        "KM-26SS-TS02-PK-M": 0.9,
        "KM-26SS-TS02-PK-L": 0.9,
        "KM-26SS-TS02-BU-S": 0.9,
        "KM-26SS-TS02-BU-M": 0.9,
        "KM-26SS-TS02-BU-L": 0.9,
        "KM-26SS-SW05-WH-S": 0.9,
        "KM-26SS-SW05-WH-M": 0.9,
        "KM-26SS-SW05-WH-L": 0.9,
        "KM-26SS-SW05-PC-S": 0.9,
        "KM-26SS-SW05-PC-M": 0.9,
        "KM-26SS-SW05-PC-L": 0.9,
        "KM-26SS-SW05-BK-S": 0.9,
        "KM-26SS-SW05-BK-M": 0.9,
        "KM-26SS-SW05-BK-L": 0.9,
        "KM-26SS-SW04MTS": 0.9,
        "KM-26SS-SW04MTM": 0.9,
        "KM-26SS-SW04MTL": 0.9,
        "KM-26SS-SW04IVS": 0.9,
        "KM-26SS-SW04IVM": 0.9,
        "KM-26SS-SW04IVL": 0.9,
        "KM-26SS-SW04BKS": 0.9,
        "KM-26SS-SW04BKM": 0.9,
        "KM-26SS-SW04BKL": 0.9,
        "KM-26SS-SW03-SK-S": 0.9,
        "KM-26SS-SW03-SK-M": 0.9,
        "KM-26SS-SW03-SK-L": 0.9,
        "KM-26SS-SW03-NV-S": 0.9,
        "KM-26SS-SW03-NV-M": 0.9,
        "KM-26SS-SW03-NV-L": 0.9,
        "KM-26SS-SW03-LBL-S": 0.9,
        "KM-26SS-SW03-LBL-M": 0.9,
        "KM-26SS-SW03-LBL-L": 0.9,
        "KM-26SS-SW03-IV-S": 0.9,
        "KM-26SS-SW03-IV-M": 0.9,
        "KM-26SS-SW03-IV-L": 0.9,
        "KM-26SS-SW02-NV-S": 0.9,
        "KM-26SS-SW02-NV-M": 0.9,
        "KM-26SS-SW02-NV-L": 0.9,
        "KM-26SS-SW02-IV-S": 0.9,
        "KM-26SS-SW02-IV-M": 0.9,
        "KM-26SS-SW02-IV-L": 0.9,
        "KM-26SS-SW02-BK-S": 0.9,
        "KM-26SS-SW02-BK-M": 0.9,
        "KM-26SS-SW02-BK-L": 0.9,
        "KM-26SS-SW01MTS": 0.9,
        "KM-26SS-SW01MTM": 0.9,
        "KM-26SS-SW01MTL": 0.9,
        "KM-26SS-SW01IVS": 0.9,
        "KM-26SS-SW01IVM": 0.9,
        "KM-26SS-SW01IVL": 0.9,
        "KM-26SS-SW01BKS": 0.9,
        "KM-26SS-SW01BKM": 0.9,
        "KM-26SS-SW01BKL": 0.9,
        "KM-26SS-SK04-BK-S": 0.9,
        "KM-26SS-SK04-BK-M": 0.9,
        "KM-26SS-SK04-BK-L": 0.9,
        "KM-26SS-SK02IVS": 0.9,
        "KM-26SS-SK02IVM": 0.9,
        "KM-26SS-SK02IVL": 0.9,
        "KM-26SS-SK02ECS": 0.9,
        "KM-26SS-SK02ECM": 0.9,
        "KM-26SS-SK02ECL": 0.9,
        "KM-26SS-SK01-OL-S": 0.9,
        "KM-26SS-SK01-OL-M": 0.9,
        "KM-26SS-SK01-OL-L": 0.9,
        "KM-26SS-SK01-IV-S": 0.9,
        "KM-26SS-SK01-IV-M": 0.9,
        "KM-26SS-SK01-IV-L": 0.9,
        "KM-26SS-PT05LBLS": 0.9,
        "KM-26SS-PT05LBLM": 0.9,
        "KM-26SS-PT05LBLL": 0.9,
        "KM-26SS-PT05IVS": 0.9,
        "KM-26SS-PT05IVM": 0.9,
        "KM-26SS-PT05IVL": 0.9,
        "KM-26SS-PT04-LKK-S": 0.9,
        "KM-26SS-PT04-LKK-M": 0.9,
        "KM-26SS-PT04-LKK-L": 0.9,
        "KM-26SS-PT04-CH-S": 0.9,
        "KM-26SS-PT04-CH-M": 0.9,
        "KM-26SS-PT04-CH-L": 0.9,
        "KM-26SS-PT03-LBE-S": 0.9,
        "KM-26SS-PT03-LBE-M": 0.9,
        "KM-26SS-PT03-LBE-L": 0.9,
        "KM-26SS-PT03-BK-S": 0.9,
        "KM-26SS-PT03-BK-M": 0.9,
        "KM-26SS-PT03-BK-L": 0.9,
        "KM-26SS-PT01-BK-S": 0.9,
        "KM-26SS-PT01-BK-M": 0.9,
        "KM-26SS-PT01-BK-L": 0.9,
        "KM-26SS-OP02-LBE-S": 0.9,
        "KM-26SS-OP02-LBE-M": 0.9,
        "KM-26SS-OP02-LBE-L": 0.9,
        "KM-26SS-JP01-OL-F": 0.9,
        "KM-26SS-JP01-CH-F": 0.9,
        "KM-26SS-JK01-IV-S": 0.9,
        "KM-26SS-JK01-IV-M": 0.9,
        "KM-26SS-BL10PKXL": 0.9,
        "KM-26SS-BL10PKM": 0.9,
        "KM-26SS-BL10PKL": 0.9,
        "KM-26SS-BL10LGRXL": 0.9,
        "KM-26SS-BL10LGRM": 0.9,
        "KM-26SS-BL10LGRL": 0.9,
        "KM-26SS-BL07-IV-S": 0.9,
        "KM-26SS-BL07-IV-M": 0.9,
        "KM-26SS-BL07-IV-L": 0.9,
        "KM-26SS-BL06-IV-S": 0.9,
        "KM-26SS-BL06-IV-M": 0.9,
        "KM-26SS-BL06-IV-L": 0.9,
        "KM-26SS-BL04-MT-S": 0.9,
        "KM-26SS-BL04-MT-M": 0.9,
        "KM-26SS-BL04-MT-L": 0.9,
        "KM-26SS-BL04-BE-S": 0.9,
        "KM-26SS-BL04-BE-M": 0.9,
        "KM-26SS-BL04-BE-L": 0.9,
        "KM-26SS-BL03-WH-S": 0.9,
        "KM-26SS-BL03-WH-M": 0.9,
        "KM-26SS-BL03-WH-L": 0.9,
        "KM-26SS-BL03-LBL-S": 0.9,
        "KM-26SS-BL03-LBL-M": 0.9,
        "KM-26SS-BL03-LBL-L": 0.9,
        "KM-26SS-BL02-IV-S": 0.9,
        "KM-26SS-BL02-IV-M": 0.9,
        "KM-26SS-BL02-IV-L": 0.9,
        "KM-26SS-BL02-BK-S": 0.9,
        "KM-26SS-BL02-BK-M": 0.9,
        "KM-26SS-BL02-BK-L": 0.9,
        "KM-26SS-BL01-EC-F": 0.9,
        "KM-26SS-BL01-BK-F": 0.9,
        "KM-26SS-BG02ORFREE": 0.9,
        "KM-26SS-BG02NVFREE": 0.9,
        "KM-26SS-BG02MTFREE": 0.9,
        "KM-26SS-BG01-KH-F": 0.9,
        "KM-26SS-BG01-BK-F": 0.9,
        "KM-26SS-ACC01OLFREE": 0.9,
        "KM-26SS-ACC01NVFREE": 0.9,
        "KM-26SS-ACC01BYFREE": 0.9,
        "KM-26SS-ACC01BCFREE": 0.9,
        "KM-25SS-TS02-WH-S": 0.9,
        "KM-25SS-TS02-WH-M": 0.9,
        "KM-25SS-TS02-MOT-S": 0.9,
        "KM-25SS-TS02-MOT-M": 0.9,
        "KM-25SS-TS02-LYE-S": 0.9,
        "KM-25SS-TS02-LYE-M": 0.9,
        "KM-25SS-TS02-BK-S": 0.9,
        "KM-25SS-TS02-BK-M": 0.9,
        "KM-25SS-TS01-WH-S": 0.9,
        "KM-25SS-TS01-WH-M": 0.9,
        "KM-25SS-TS01-MGY-S": 0.9,
        "KM-25SS-TS01-MGY-M": 0.9,
        "KM-25SS-TS01-LYE-S": 0.9,
        "KM-25SS-TS01-LYE-M": 0.9,
        "KM-25SS-TS01-BK-S": 0.9,
        "KM-25SS-TS01-BK-M": 0.9,
        "KM-25SS-SW03-WH-S": 0.9,
        "KM-25SS-SW03-WH-M": 0.9,
        "KM-25SS-SW03-LYE-S": 0.9,
        "KM-25SS-SW03-LYE-M": 0.9,
        "KM-25SS-SW03-LBL-S": 0.9,
        "KM-25SS-SW03-LBL-M": 0.9,
        "KM-25SS-SW03-BK-S": 0.9,
        "KM-25SS-SW03-BK-M": 0.9,
        "KM-25SS-SK04-IV-S": 0.9,
        "KM-25SS-SK04-IV-M": 0.9,
        "KM-25SS-SK04-IV-L": 0.9,
        "KM-25SS-BL08-SBL-F": 0.9,
        "KM-25SS-BL08-PK-F": 0.9,
        "KM-25SS-BL08-LM-F": 0.9,
        "KM-25SS-BL08-BLS-F": 0.9,
        "KM-25SS-BL06-NV-S": 0.9,
        "KM-25SS-BL06-NV-M": 0.9,
        "KM-25SS-BL06-IV-S": 0.9,
        "KM-25SS-BL06-IV-M": 0.9,
        "KM-25SS-BL01-WH-F": 0.9,
        "KM-25SS-BL01-SBL-F": 0.9,
        "KM-25SS-BL01-PK-F": 0.9,
        "KM-25SS-BL01-LM-F": 0.9,
        "KM-25SS-TS03-IV-S": 0.8,
        "KM-25SS-TS03-IV-M": 0.8,
        "KM-25SS-TS03-BK-S": 0.8,
        "KM-25SS-TS03-BK-M": 0.8,
        "KM-25SS-SW06-MBE-S": 0.8,
        "KM-25SS-SW06-MBE-M": 0.8,
        "KM-25SS-SW06-LYE-S": 0.8,
        "KM-25SS-SW06-LYE-M": 0.8,
        "KM-25SS-SW06-IV-S": 0.8,
        "KM-25SS-SW06-IV-M": 0.8,
        "KM-25SS-SW06-BK-S": 0.8,
        "KM-25SS-SW06-BK-M": 0.8,
        "KM-25SS-SW05-LKK-S": 0.8,
        "KM-25SS-SW05-LKK-M": 0.8,
        "KM-25SS-SW05-LBL-S": 0.8,
        "KM-25SS-SW05-LBL-M": 0.8,
        "KM-25SS-SW05-IV-S": 0.8,
        "KM-25SS-SW05-IV-M": 0.8,
        "KM-25SS-SW04-MBE-S": 0.8,
        "KM-25SS-SW04-MBE-M": 0.8,
        "KM-25SS-SW04-IV-S": 0.8,
        "KM-25SS-SW04-IV-M": 0.8,
        "KM-25SS-SK05-LBE-S": 0.8,
        "KM-25SS-SK05-LBE-M": 0.8,
        "KM-25SS-SK01-WH-S": 0.8,
        "KM-25SS-SK01-WH-M": 0.8,
        "KM-25SS-PT07-OL-S": 0.8,
        "KM-25SS-PT07-OL-M": 0.8,
        "KM-25SS-PT07-OL-L": 0.8,
        "KM-25SS-PT06-MBL-S": 0.8,
        "KM-25SS-PT06-MBL-M": 0.8,
        "KM-25SS-PT06-MBL-L": 0.8,
        "KM-25SS-PT05-IV-S": 0.8,
        "KM-25SS-PT05-IV-M": 0.8,
        "KM-25SS-PT02-LYL-S": 0.8,
        "KM-25SS-PT02-LYL-M": 0.8,
        "KM-25SS-PT01-WH-S": 0.8,
        "KM-25SS-PT01-WH-M": 0.8,
        "KM-25SS-PT01-BLS-S": 0.8,
        "KM-25SS-PT01-BLS-M": 0.8,
        "KM-25SS-OP02-IV-F": 0.8,
        "KM-25SS-OP02-BK-F": 0.8,
        "KM-25SS-OP01-BK-S": 0.8,
        "KM-25SS-OP01-BK-M": 0.8,
        "KM-25SS-BL07-LBE-S": 0.8,
        "KM-25SS-BL07-LBE-M": 0.8,
        "KM-25SS-BL07-BK-S": 0.8,
        "KM-25SS-BL07-BK-M": 0.8,
        "KM-25SS-BL05-IV-S": 0.8,
        "KM-25SS-BL05-IV-M": 0.8,
        "KM-25SS-BL05-IV-L": 0.8,
        "KM-25SS-BL04-WH-S": 0.8,
        "KM-25SS-BL04-WH-M": 0.8,
        "KM-25SS-BL03-BLS-F": 0.8,
        "KM-25HS-SK01-PC-S": 0.8,
        "KM-25HS-SK01-PC-M": 0.8,
        "KM-25HS-SK01-PC-L": 0.8,
        "KM-25HS-SK01-IV-S": 0.8,
        "KM-25HS-SK01-IV-M": 0.8,
        "KM-25HS-SK01-IV-L": 0.8,
        "KM-24SS-SK06-IV-S": 0.8,
        "KM-24SS-SK06-IV-M": 0.8,
        "KM-24SS-SK06-IV-L": 0.8,
        "KM-24SS-SK04-BL-S": 0.8,
        "KM-24SS-SK04-BL-M": 0.8,
        "KM-24SS-OP04-BK-S": 0.7,
        "KM-24SS-OP04-BK-M": 0.7,
        "KM-24SS-OP03-YE-S": 0.7,
        "KM-24SS-OP03-YE-M": 0.7,
        "KM-24SS-BL02-LYE-S": 0.7,
        "KM-24SS-BL02-LYE-M": 0.7,
        "KM-24SS-BL02-DBE-S": 0.7,
        "KM-24SS-BL02-DBE-M": 0.7,
        "KM-24FW-TS02-SBL-S": 0.7,
        "KM-24FW-TS02-SBL-M": 0.7,
        "KM-24FW-TS02-IV-S": 0.7,
        "KM-24FW-TS02-IV-M": 0.7,
        "KM-23SP-BL03-IV-S": 0.6,
        "KM-23SP-BL03-IV-M": 0.6,
        "KM-23SP-BL03-BK-S": 0.6,
        "KM-23SP-BL03-BK-M": 0.6,
        "KM-23SM-OP01-BL-S": 0.6,
        "KM-23SM-OP01-BL-M": 0.6,
        "KM-23FW-PT05-BL-S": 0.6,
        "KM-23FW-PT05-BL-M": 0.6,
        "KM-23FW-PT05-BL-L": 0.6,
        "KM-23FW-PT05-BK-S": 0.6,
        "KM-23FW-PT05-BK-M": 0.6,
        "KM-23FW-PT05-BK-L": 0.6,
    }

    variants = client.variants_by_skus(sku_discount_map.keys())

    if start_or_end == "end":
        client.revert_variant_prices(variants, testrun=testrun)
        return

    new_prices_by_variant_id = {
        v["id"]: int(
            int(v["compareAtPrice"] or v["price"]) * sku_discount_map[v["sku"]]
        )
        for v in variants
    }
    client.update_variant_prices_by_dict(
        variants, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
    )


def start_end_discounts_26fw1_0909(testrun=True, start_or_end="start"):
    """
    26FW1 09.09 Sale (10% OFF)
    """
    client = KumeClient()

    sku_discount_map = {
        "KS-26FW-BG01-BK-F": 0.9,
        "KM-26FW-TS02-BK-S": 0.9,
        "KM-26FW-TS02-BK-M": 0.9,
        "KM-26FW-TS02-BR-S": 0.9,
        "KM-26FW-TS02-BR-M": 0.9,
        "KM-26FW-TS02-BL-S": 0.9,
        "KM-26FW-TS02-BL-M": 0.9,
        "KM-26FW-TS03-WH-S": 0.9,
        "KM-26FW-TS03-WH-M": 0.9,
        "KM-26FW-TS03-MT-S": 0.9,
        "KM-26FW-TS03-MT-M": 0.9,
        "KM-26FW-TS03-MGR-S": 0.9,
        "KM-26FW-TS03-MGR-M": 0.9,
        "M-KM-26FW-SW04MGRM": 0.9,
        "M-KM-26FW-SW04MGRL": 0.9,
        "M-KM-26FW-SW04MGRXL": 0.9,
        "M-KM-26FW-SW04DERM": 0.9,
        "M-KM-26FW-SW04DERL": 0.9,
        "M-KM-26FW-SW04DERXL": 0.9,
        "M-KM-26FW-SW04DKKM": 0.9,
        "M-KM-26FW-SW04DKKL": 0.9,
        "M-KM-26FW-SW04DKKXL": 0.9,
        "KM-26FW-SK02GRS": 0.9,
        "KM-26FW-SK02GRM": 0.9,
        "KM-26FW-SK02BRS": 0.9,
        "KM-26FW-SK02BRM": 0.9,
        "KM-26FW-SK01BKS": 0.9,
        "KM-26FW-SK01BKM": 0.9,
        "KM-26FW-SK01BKL": 0.9,
        "KM-26FW-PT01IVS": 0.9,
        "KM-26FW-PT01IVM": 0.9,
        "KM-26FW-PT01IVL": 0.9,
        "KM-26FW-PT01GRS": 0.9,
        "KM-26FW-PT01GRM": 0.9,
        "KM-26FW-PT01GRL": 0.9,
        "M-KM-26FW-PT01BEM": 0.9,
        "M-KM-26FW-PT01BEL": 0.9,
        "M-KM-26FW-PT01BEXL": 0.9,
        "M-KM-26FW-PT01DBNM": 0.9,
        "M-KM-26FW-PT01DBNL": 0.9,
        "M-KM-26FW-PT01DBNXL": 0.9,
    }

    variants = client.variants_by_skus(sku_discount_map.keys())

    if start_or_end == "end":
        client.revert_variant_prices(variants, testrun=testrun)
        return

    new_prices_by_variant_id = {
        v["id"]: int(
            int(v["compareAtPrice"] or v["price"]) * sku_discount_map[v["sku"]]
        )
        for v in variants
    }
    client.update_variant_prices_by_dict(
        variants, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
    )


def start_end_discounts_26fw2_0916(testrun=True, start_or_end="start"):
    """
    26FW2 09.16 Sale (10% OFF)
    """
    client = KumeClient()

    sku_discount_map = {
        "KM-26FW-JK03-BE-F": 0.9,
        "KM-26FW-JK03-MGR-F": 0.9,
        "M-KM-26FW-BL02-RD-M": 0.9,
        "M-KM-26FW-BL02-RD-L": 0.9,
        "M-KM-26FW-BL02-RD-XL": 0.9,
        "M-KM-26FW-BL02-BL-M": 0.9,
        "M-KM-26FW-BL02-BL-L": 0.9,
        "M-KM-26FW-BL02-BL-XL": 0.9,
        "KM-26FW-TS01-IV-S": 0.9,
        "KM-26FW-TS01-IV-M": 0.9,
        "KM-26FW-TS01-MT-S": 0.9,
        "KM-26FW-TS01-MT-M": 0.9,
        "KM-26FW-TS01-MBE-S": 0.9,
        "KM-26FW-TS01-MBE-M": 0.9,
        "KM-26FW-TS01-BK-S": 0.9,
        "KM-26FW-TS01-BK-M": 0.9,
        "KM-26FW-TS04-BK-S": 0.9,
        "KM-26FW-TS04-BK-M": 0.9,
        "KM-26FW-TS04-WH-S": 0.9,
        "KM-26FW-TS04-WH-M": 0.9,
        "KM-26FW-TS04-GR-S": 0.9,
        "KM-26FW-TS04-GR-M": 0.9,
        "KM-26FW-TS04-BL-S": 0.9,
        "KM-26FW-TS04-BL-M": 0.9,
        "M-KM-26FW-SW01CHL": 0.9,
        "M-KM-26FW-SW01CHXL": 0.9,
        "M-KM-26FW-SW01LBLL": 0.9,
        "M-KM-26FW-SW01LBLXL": 0.9,
        "M-KM-26FW-SW01BKL": 0.9,
        "M-KM-26FW-SW01BKXL": 0.9,
        "KM-26FW-SK03BRS": 0.9,
        "KM-26FW-SK03BRM": 0.9,
        "KM-26FW-PT06BRS": 0.9,
        "KM-26FW-PT06BRM": 0.9,
        "KM-26FW-PT06BRL": 0.9,
        "KM-26FW-PT06CHS": 0.9,
        "KM-26FW-PT06CHM": 0.9,
        "KM-26FW-PT06CHL": 0.9,
        "KM-26FW-PT07BKS": 0.9,
        "KM-26FW-PT07BKM": 0.9,
        "KM-26FW-PT07BKL": 0.9,
        "M-KM-26FW-PT02BKM": 0.9,
        "M-KM-26FW-PT02BKL": 0.9,
        "M-KM-26FW-PT02BKXL": 0.9,
    }

    variants = client.variants_by_skus(sku_discount_map.keys())

    if start_or_end == "end":
        client.revert_variant_prices(variants, testrun=testrun)
        return

    new_prices_by_variant_id = {
        v["id"]: int(
            int(v["compareAtPrice"] or v["price"]) * sku_discount_map[v["sku"]]
        )
        for v in variants
    }
    client.update_variant_prices_by_dict(
        variants, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
    )


def start_end_discounts_26fw3_0923(testrun=True, start_or_end="start"):
    """
    26FW3 09.23 Sale (10% OFF)
    """
    client = KumeClient()

    sku_discount_map = {
        "M-KM-26FW-JP01-BK-L": 0.9,
        "M-KM-26FW-JP01-BK-XL": 0.9,
        "M-KM-26FW-JP01-BR-L": 0.9,
        "M-KM-26FW-JP01-BR-XL": 0.9,
        "M-KM-26FW-JP01-BK-F": 0.9,
        "M-KM-26FW-JP01-BR-F": 0.9,
        "KM-26FW-JK04-BK-S": 0.9,
        "KM-26FW-JK04-BK-M": 0.9,
        "M-KM-26FW-BL03-BR-M": 0.9,
        "M-KM-26FW-BL0-BR-L": 0.9,
        "M-KM-26FW-BL03-BR-XL": 0.9,
        "KM-26FW-SW04BKS": 0.9,
        "KM-26FW-SW04BKM": 0.9,
        "KM-26FW-SW04IVS": 0.9,
        "KM-26FW-SW04IVM": 0.9,
        "KM-26FW-SW04DBNS": 0.9,
        "KM-26FW-SW04DBNM": 0.9,
        "KM-26FW-SW04BES": 0.9,
        "KM-26FW-SW04BEM": 0.9,
        "KM-26FW-SW10BKS": 0.9,
        "KM-26FW-SW10BKM": 0.9,
        "KM-26FW-SW10BKL": 0.9,
        "KM-26FW-SW10IVS": 0.9,
        "KM-26FW-SW10IVM": 0.9,
        "KM-26FW-SW10IVL": 0.9,
        "KM-26FW-SW10DBNS": 0.9,
        "KM-26FW-SW10DBNM": 0.9,
        "KM-26FW-SW10DBNL": 0.9,
        "KM-26FW-SW10BES": 0.9,
        "KM-26FW-SW10BEM": 0.9,
        "KM-26FW-SW10BEL": 0.9,
        "KM-26FW-SW05BKS": 0.9,
        "KM-26FW-SW05BKM": 0.9,
        "KM-26FW-SW05BKL": 0.9,
        "KM-26FW-SW05IVS": 0.9,
        "KM-26FW-SW05IVM": 0.9,
        "KM-26FW-SW05IVL": 0.9,
        "KM-26FW-SW05BRS": 0.9,
        "KM-26FW-SW05BRM": 0.9,
        "KM-26FW-SW05BRL": 0.9,
        "KM-26FW-SW05BLS": 0.9,
        "KM-26FW-SW05BLM": 0.9,
        "KM-26FW-SW05BLL": 0.9,
        "KM-26FW-SK04BKS": 0.9,
        "KM-26FW-SK04BKM": 0.9,
        "KM-26FW-SK04BKL": 0.9,
        "KM-26FW-PT05BES": 0.9,
        "KM-26FW-PT05BEM": 0.9,
        "KM-26FW-PT05BEL": 0.9,
        "KM-26FW-PT05GRS": 0.9,
        "KM-26FW-PT05GRM": 0.9,
        "KM-26FW-PT05GRL": 0.9,
    }

    variants = client.variants_by_skus(sku_discount_map.keys())

    if start_or_end == "end":
        client.revert_variant_prices(variants, testrun=testrun)
        return

    new_prices_by_variant_id = {
        v["id"]: int(
            int(v["compareAtPrice"] or v["price"]) * sku_discount_map[v["sku"]]
        )
        for v in variants
    }
    client.update_variant_prices_by_dict(
        variants, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
    )


def start_end_discounts_26fw4_1001(testrun=True, start_or_end="start"):
    """
    26FW4 10.01 Sale (10% OFF) — products tagged 26_1001_FW_4
    """
    client = KumeClient()
    tag = "26_1001_FW_4"
    rate = 0.9

    products = client.products_by_tag(tag)
    if not products:
        return

    if start_or_end == "end":
        client.revert_product_prices(products, testrun=testrun)
        return

    new_prices_by_variant_id = {
        v["id"]: int(int(v["compareAtPrice"] or v["price"]) * rate)
        for p in products
        for v in p["variants"]["nodes"]
    }
    client.update_product_prices_by_dict(
        products, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
    )


def start_end_discounts_26fw5_1008(testrun=True, start_or_end="start"):
    """
    26FW5 10.08 Sale (10% OFF) — products tagged 26_1008_FW_5
    """
    client = KumeClient()
    tag = "26_1008_FW_5"
    rate = 0.9

    products = client.products_by_tag(tag)
    if not products:
        return

    if start_or_end == "end":
        client.revert_product_prices(products, testrun=testrun)
        return

    new_prices_by_variant_id = {
        v["id"]: int(int(v["compareAtPrice"] or v["price"]) * rate)
        for p in products
        for v in p["variants"]["nodes"]
    }
    client.update_product_prices_by_dict(
        products, new_prices_by_variant_id=new_prices_by_variant_id, testrun=testrun
    )


def main():
    start_end_discounts_26fw4_1001(testrun=False, start_or_end="start")
    start_end_discounts_26fw5_1008(testrun=False, start_or_end="start")


if __name__ == "__main__":
    main()
