import argparse
import datetime
import logging
import sys
import zoneinfo
import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Add variants to products from Google Sheet"
    )
    parser.add_argument(
        "--client",
        type=lambda s: s.lower(),
        choices=[
            "gbh",
            "ssil",
            "rohseoul",
            "kume",
            "lememe",
            "blossom",
            "apricot-studios",
            "archivepke",
        ],
        required=True,
        help="Client name",
    )
    parser.add_argument(
        "--sheet",
        type=str,
        required=True,
        help="Sheet name in Google Sheets",
    )
    parser.add_argument(
        "--client-variant",
        type=str,
        choices=["default", "color_only", "size_only", "material_only"],
        default="default",
        help="GBH: default/color_only/size_only, SSIL: default/material_only",
    )
    args = parser.parse_args()

    # クライアントの生成（ブランドごとにクラスを切り替え）
    client_name = args.client
    client_variant = args.client_variant
    if client_name == "gbh":
        if client_variant == "color_only":
            from brands.gbh.client import GbhClientColorOptionOnly as ClientCls
        elif client_variant == "size_only":
            from brands.gbh.client import GbhClientSizeOptionOnly as ClientCls
        else:
            from brands.gbh.client import GbhClient as ClientCls
        client = ClientCls()
    elif client_name == "ssil":
        if client_variant == "material_only":
            from brands.ssil.client import SsilClientMaterialOptionOnly as ClientCls
        else:
            from brands.ssil.client import SsilClient as ClientCls
        client = ClientCls()
    elif client_name == "rohseoul":
        from brands.rohseoul.client import RohseoulClient as ClientCls

        client = ClientCls()
    elif client_name == "kume":
        from brands.kume.client import KumeClient as ClientCls

        client = ClientCls()
    elif client_name == "lememe":
        from brands.lememe.client import LememeClient as ClientCls

        client = ClientCls()
    elif client_name == "blossom":
        from brands.blossom.client import BlossomClient as ClientCls

        client = ClientCls()
    elif client_name == "apricot-studios":
        from brands.apricotstudios.client import ApricotStudiosClient as ClientCls

        client = ClientCls(None, None)
    elif client_name == "archivepke":
        from brands.archivepke.client import ArchivepkeClient as ClientCls

        client = ClientCls()
    else:
        logger.error(f"Unknown client name: {args.client}")
        sys.exit(1)
    logger.info(f"シートから商品情報を読み込み中: {args.sheet}")
    product_inputs = client.product_inputs_from_sheet(args.sheet)

    if not product_inputs:
        logger.error(f"シートに商品が見つかりませんでした: {args.sheet}")
        sys.exit(1)

    logger.info(f"シート内に {len(product_inputs)} 件の商品が見つかりました")

    for i, product_input in enumerate(product_inputs):
        logger.info(
            f"[{i+1}/{len(product_inputs)}] 商品のバリアントを追加中: {product_input['title']}"
        )
        try:
            client.add_variants_from_product_input(product_input)
            logger.info(f"バリアントの追加が完了しました: {product_input['title']}")
        except Exception as e:
            logger.error(
                f"バリアントの追加に失敗しました {product_input['title']}: {e}"
            )
            # エラーが発生しても次の商品の処理を続行
            continue

    logger.info("全ての商品の処理が完了しました")


if __name__ == "__main__":
    main()
