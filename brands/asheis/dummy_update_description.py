import utils

client = utils.client("asheis")

products = client.products_by_query()

description_html = """

<div id="alvanaProduct">
    <p>やわらかく広がるフレアシルエットが女性らしい印象を纏う、Marie Flare Skirt（マリー フレア スカート）。薄手でありながら程よい張りとハリ感のある素材が、夏の暑い日でも肌に張り付かず、一日中快適な着心地を叶えます。ミディ丈の上品な佇まいが、日常のコーディネートに優雅さを添える一着です。</p>
</div>
"""

product_care = """
お取り扱いのご注意
- この商品の素材は天然素材のため、ネップ・染めムラがある場合がございます。（ネップは必ずありますが織りキズではありませんのでご了承ください。
- 濃色のものは、汗や水などの湿った状態での強い摩擦等により、他のものに色移りすることがありますのでご注意ください
- 強い日光（または照明）を長時間受けますと変色の恐れがありますので、ご着用及び保管の際にはご注意ください。
- 蛍光増白剤入りの洗剤は変色の恐れがありますのでご注意ください。
"""

size_table_html = """
<table border="1" style="border-collapse: collapse;" class="size-table">
  <thead>
    <tr>
      <th>Size</th>
      <th>LENGTH</th>
      <th>WAIST</th>
      <th>HIP</th>
      <th>THIGH</th>
      <th>RISE</th>
      <th>HEM</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>S</td>
      <td>104</td>
      <td>36</td>
      <td>45</td>
      <td>27.5</td>
      <td>37</td>
      <td>28</td>
    </tr>
    <tr>
      <td>M</td>
      <td>105</td>
      <td>38</td>
      <td>47</td>
      <td>28.5</td>
      <td>38</td>
      <td>29</td>
    </tr>
  </tbody>
</table>
"""

material = "NYLON52% POLYESTER48%"
made_in = "Japan"

for product in products:
    client.update_product_description(product["id"], description_html)
    client.update_product_care_metafield(
        product["id"], client.text_to_simple_richtext(product_care)
    )
    client.update_size_table_html_metafield(product["id"], size_table_html)
    client.update_product_metafield(product["id"], "custom", "material", material)
    client.update_product_metafield(product["id"], "custom", "made_in", made_in)
