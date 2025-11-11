import logging
import utils
from brands.kume.client import KumeClient

logging.basicConfig(level=logging.INFO)

skus = [
  "KM-25FW-CT01-BK-F",
  "KM-25FW-CT03-IV-M",
  "KM-25FW-CT03-IV-S",
  "KM-25FW-CT03-MGR-M",
  "KM-25FW-CT03-MGR-S",
  "KM-25FW-CT04-NV-M",
  "KM-25FW-CT04-NV-S",
  "KM-25FW-CT05-CH-F",
  "KM-25FW-CT05-CM-F",
  "KM-25FW-JK01-BK-M",
  "KM-25FW-JK01-BK-S",
  "KM-25FW-JK01-TBK-M",
  "KM-25FW-JK01-TBK-S",
  "KM-25FW-JK02-KH-F",
  "KM-25FW-JP01-IV-M",
  "KM-25FW-JP01-IV-S",
  "KM-25FW-JP02-DBE-M",
  "KM-25FW-JP02-DBE-S",
  "M-KM-25FW-CT02-BK-L",
  "M-KM-25FW-CT02-BK-XL",
  "M-KM-25FW-CT06-CH-L",
  "M-KM-25FW-CT06-CH-XL",
  "M-KM-25FW-CT06-KH-L",
  "M-KM-25FW-CT06-KH-XL",
  "M-KM-25FW-JK03-KH-L",
  "M-KM-25FW-JK03-KH-XL",
  "M-KM-25FW-JP03-DGR-L",
  "M-KM-25FW-JP03-DGR-XL",
  "KM-25SS-SW02-LYE-F",
  "KM-25SS-SW02-IV-F",
  "KM-25SS-SW02-BK-F",
  "KM-25SS-CT01-BE-F",
  "KM-25SS-JK01-IV-M",
  "KM-25SS-JK01-IV-S",
  "KM-25SS-JK01-LBE-M",
  "KM-25SS-JK01-LBE-S",
  "KM-25SS-JK02-BK-M",
  "KM-25SS-JK02-BK-S",
  "KM-25SS-JK02-LYE-M",
  "KM-25SS-JK02-LYE-S",
  "KM-25SS-JP01-PC-S",
  "KM-25SS-JP01-PC-M",
  "KM-25SS-JP01-IV-S",
  "KM-25SS-JP01-IV-M",
]

def main():
    client = KumeClient()
    product_ids = {client.product_id_by_sku(sku) for sku in skus}
    print(len(product_ids))
    client.collection_create("2025 outer sale 11/18-11/23 10% OFF", product_ids)


if __name__ == "__main__":
    main()
