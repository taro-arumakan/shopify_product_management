"""CEC-509: Chuseok shipping notice page for the Korean brands.

Creates /pages/shipping-notice on each brand managed by CATALDESIGN. ASHEIS is
a Japanese brand and the Korean holiday does not apply to it; GBH and Archivépke
are no longer managed here, so all three are out of scope.

The copy is CEC-509's, with the opening and closing lines these stores have used
for every previous holiday notice (年末年始 / 韓国旧正月 / GW / お盆) so it reads
the way customers are used to. The brand name comes from each client's
BRAND_NAME. The earlier notices disagree with it in three places — they say
KUME, Blossom and APRICOT STUDIOS where BRAND_NAME has KUMÉ, BLOSSOM and Apricot
Studios — and BRAND_NAME is the correct form, so this does not follow them.

Re-running is safe: an existing /pages/shipping-notice is updated in place
rather than duplicated, which is also how the wording above was corrected after
the first run.

The handle is the English `shipping-notice` that CEC-509 asks for, rather than
the descriptive Japanese handle the earlier notices use, so the announcement bar
link stays the same between holidays. The trade-off is that the next notice has
to overwrite this page or pick another handle.

    PYTHONPATH=. uv run brands/scripts/create_shipping_notice_page.py            # dry run
    PYTHONPATH=. uv run brands/scripts/create_shipping_notice_page.py --apply
"""

import logging
import sys

import utils

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
for noisy in ("googleapiclient", "urllib3", "google"):
    logging.getLogger(noisy).setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

BRANDS = ["ssil", "rohseoul", "lememe", "kume", "blossom", "apricotstudios"]

HANDLE = "shipping-notice"
TITLE = "韓国の秋夕（チュソク）連休に伴う配送・お問い合わせ対応のお知らせ"

# `page` is the suffix every previous holiday notice on these stores uses.
TEMPLATE_SUFFIX = "page"

# The title is rendered by the page template, so it is deliberately not repeated
# as a heading in the body — same as the earlier notices.
BODY_TEMPLATE = """<p><strong>【お知らせ】</strong></p>
<p>いつも{brand}をご愛顧いただき、誠にありがとうございます。</p>
<p>韓国の祝日（秋夕連休）に伴い、下記の期間、商品の発送およびカスタマーサポート業務を一部休止いたします。</p>
<p><br></p>
<p><strong>■ 配送休止期間</strong></p>
<p>9月24日（木）〜9月27日（日）</p>
<p>9月28日（月）より順次発送いたします。</p>
<p>通常よりお届けまでにお時間をいただく場合がございますので、あらかじめご了承ください。</p>
<p><br></p>
<p><strong>■ お問い合わせ対応</strong></p>
<p>9月24日（木）以降、日本側で対応可能なお問い合わせは順次ご案内いたします。</p>
<p>韓国側での確認が必要な場合は、9月28日（月）以降の回答となります。</p>
<p><br></p>
<p>お客様にはご不便をおかけいたしますが、何卒ご理解のほどよろしくお願いいたします。</p>
<p>引き続き{brand}をよろしくお願い申し上げます。</p>"""


def body_for(brand_name):
    return BODY_TEMPLATE.format(brand=brand_name)


def main(apply_changes):
    for shop_key in BRANDS:
        client = utils.client(shop_key)
        brand_name = client.BRAND_NAME
        body = body_for(brand_name)

        # Creating over an existing handle silently gets a -1 suffix, which is
        # how KUME ended up with two 年末年始 pages. Update in place instead.
        existing = client.pages_by_query(f"handle:{HANDLE}")
        action = "update" if existing else "create"

        if not apply_changes:
            print(f"===== {shop_key} ({brand_name}) — would {action} =====")
            print(f"  title  : {TITLE}")
            print(f"  handle : {HANDLE}")
            print(f"  suffix : {TEMPLATE_SUFFIX}")
            print(body)
            print()
            continue

        if existing:
            page = client.page_update(
                existing[0]["id"],
                title=TITLE,
                body=body,
                is_published=True,
                template_suffix=TEMPLATE_SUFFIX,
            )
        else:
            page = client.page_create(
                title=TITLE,
                body=body,
                handle=HANDLE,
                is_published=True,
                template_suffix=TEMPLATE_SUFFIX,
            )
        logger.info(
            f"{shop_key}: {action}d {page['id']} /pages/{page['handle']} "
            f"published={page['isPublished']}"
        )


if __name__ == "__main__":
    main(apply_changes="--apply" in sys.argv)
