import datetime
import pathlib
import utils

client = utils.client("asheis")

product_images_parent_dir = (
    "https://drive.google.com/drive/folders/1p7XAlJJEibinkDnn47hcfSkld783-i0D"
)
look_images_parent_dir = (
    "https://drive.google.com/drive/folders/1x8DuFlT03AF75XZDOiJ7mzGQ3CAHJ4TB"
)

product_dirs = client.list_folders(product_images_parent_dir.rsplit("/", 1)[-1])
print(len(product_dirs))

for product_image_dir in product_dirs[:2]:
    product_title = product_image_dir["name"]
    look_dir = client.find_by_folder_id_by_name(
        look_images_parent_dir.rsplit("/", 1)[-1], product_title, exact_name=False
    )

    print(client.get_drive_image_details(product_image_dir["id"]))
    print(client.get_drive_image_details(look_dir["id"]))
    res = client.product_create(
        title=product_title,
        description_html="""
<div id="cataldesignProduct">
    <h3>商品説明</h3>
    <p>ゆとりのあるオーバーサイズシルエットが魅力のボーイフレンドフィットシャツです。リラックス感のある着心地で、カジュアルからセミフォーマルまで幅広いスタイルにマッチ。レイヤードにも取り入れやすく、着こなしの幅を広げてくれる一枚です。胸ポケットにはROH SEOULのロゴ刺繍をあしらい、さりげないアクセントをプラス。快適さと洗練を兼ね備えたデイリーアイテムです。</p>
    <h3>手入れ方法</h3>
    <p>革表面に跡や汚れなどが残る場合がありますが、天然皮革の特徴である不良ではございませんのでご了承ください。また、時間経過により金属の装飾や革の色が変化する場合がございますが、製品の欠陥ではありません。あらかじめご了承ください。<br>
1: 熱や直射日光に長時間さらされると革に変色が生じることがありますのでご注意ください。<br>
2: 変形の恐れがありますので、無理のない内容量でご使用ください。<br>
3: 水に弱い素材です。濡れた場合は柔らかい布で水気を除去した後、乾燥させてください。<br>
4: 使用しないときはダストバッグに入れ、涼しく風通しのいい場所で保管してください。<br>
5: アルコール、オイル、香水、化粧品などにより製品が損傷することがありますので、ご使用の際はご注意ください。</p>
    <h3>サイズ・素材</h3>
    <table>
<thead><tr>
<th>Total length (side neck center: 77</th>
<th>Shoulder width: 54</th>
<th>Sleeve length: 57</th>
<th>Bust: 120</th>
<th>Armhole: 27</th>
</tr></thead>
<tbody><tr>
<td>cm</td>
<td>cm</td>
<td>cm</td>
<td>cm</td>
<td>cm</td>
</tr></tbody>
</table>
    <br>
    <table width="100%">
    <tbody>
        <tr>
        <th>素材</th>
        <td>Outer fabric : COTTON 80% / POLYESTER 20%</td>
        </tr>
        <tr>
        <th>原産国</th>
        <td>韓國</td>
        </tr>
    </tbody>
    </table>
</div>
        """,
        vendor="asheis",
        tags=["dummy", "clothes"],
        option_dicts=[
            {
                "option_values": {"Color": "BLACK", "Size": "S"},
                "price": 35200,
                "sku": "ASHEIS-90154-BK-2",
                "stock": 2,
            },
            {
                "option_values": {"Color": "BLACK", "Size": "M"},
                "price": 35200,
                "sku": "ASHEIS-90154-BK-3",
                "stock": 2,
            },
            {
                "option_values": {"Color": "WHITE", "Size": "S"},
                "price": 35200,
                "sku": "ASHEIS-90154-WH-2",
                "stock": 2,
            },
            {
                "option_values": {"Color": "WHITE", "Size": "M"},
                "price": 35200,
                "sku": "ASHEIS-90154-WH-3",
                "stock": 2,
            },
        ],
    )
    local_dir = f"{pathlib.Path.home()}/Downloads/{client.shop_name}_{datetime.date.today():%Y%m%d}/"
    filename_prefix = f"upload_{datetime.date.today():%Y%m%d}_{product_title}_"

    client.add_product_images(
        res["id"], product_image_dir["id"], local_dir, filename_prefix
    )
    client.add_product_images(res["id"], look_dir["id"], local_dir, filename_prefix)

    print()
