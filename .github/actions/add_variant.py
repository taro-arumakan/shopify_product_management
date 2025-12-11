import argparse
import datetime
import logging
import sys
import zoneinfo
import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Add variants to products from Google Sheet")
    parser.add_argument(
        "--client",
        type=str,
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
        "--scheduled-time",
        type=str,
        default=None,
        help="Scheduled time for publishing products (format: YYYY-MM-DD HH:MM, timezone: Asia/Tokyo). Example: 2025-12-12 00:00",
    )

    args = parser.parse_args()

    # スケジュール日時のパース
    scheduled_time = None
    if args.scheduled_time:
        try:
            dt = datetime.datetime.strptime(args.scheduled_time, "%Y-%m-%d %H:%M")
            scheduled_time = dt.replace(tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo"))
            logger.info(f"スケジュール公開日時: {scheduled_time}")
        except ValueError as e:
            logger.error(f"スケジュール日時の形式が正しくありません: {args.scheduled_time}. 形式: YYYY-MM-DD HH:MM")
            sys.exit(1)

    client = utils.client(args.client)
    logger.info(f"シートから商品情報を読み込み中: {args.sheet}")
    product_info_list = client.product_info_list_from_sheet(args.sheet)
    
    if not product_info_list:
        logger.error(f"シートに商品が見つかりませんでした: {args.sheet}")
        sys.exit(1)
    
    logger.info(f"シート内に {len(product_info_list)} 件の商品が見つかりました")
    
    for i, product_info in enumerate(product_info_list):
        logger.info(f"[{i+1}/{len(product_info_list)}] 商品のバリアントを追加中: {product_info['title']}")
        try:
            # TODO: 確認のため一旦コメントアウト
            #client.add_variants_from_product_info(product_info)
            logger.info(f"バリアントの追加が完了しました: {product_info['title']}")
            
            # スケジュール日時が指定されている場合、商品をスケジュール公開
            if scheduled_time:
                product_id = client.product_id_by_title(product_info["title"])
                logger.info(f"商品をスケジュール公開します: {product_info['title']} (公開日時: {scheduled_time})")
                # TODO: 確認のため一旦コメントアウト
                #client.activate_and_publish_by_product_id(product_id, scheduled_time=scheduled_time)
                logger.info(f"スケジュール公開の設定が完了しました: {product_info['title']}")
        except Exception as e:
            logger.error(f"バリアントの追加に失敗しました {product_info['title']}: {e}")
            # エラーが発生しても次の商品の処理を続行
            continue
    
    logger.info("全ての商品の処理が完了しました")


if __name__ == "__main__":
    main()

