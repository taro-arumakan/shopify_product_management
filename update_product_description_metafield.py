import json

def get_product_description(desc, care, size, material, origin):

  res = {
    'type': 'root',
    'children': [{'children': [{'type': 'text', 'value': '商品説明'}], 'level': 3, 'type': 'heading'},
                {'children': [{'type': 'text', 'value': desc}], 'type': 'paragraph'},
                {'children': [{'type': 'text', 'value': '使用上の注意'}], 'level': 3, 'type': 'heading'},
                {'children': [{'type': 'text',
                              'value': care}],
                'type': 'paragraph'},
                {'children': [{'type': 'text', 'value': ''}], 'type': 'paragraph'},
                {'children': [{'type': 'text', 'value': 'サイズ'}], 'level': 3, 'type': 'heading'},
                {'children': [{'type': 'text', 'value': size}], 'type': 'paragraph'},
                {'children': [{'type': 'text', 'value': '素材'}], 'level': 3, 'type': 'heading'},
                {'children': [{'type': 'text', 'value': material}], 'type': 'paragraph'},
                {'children': [{'type': 'text', 'value': '原産国'}], 'level': 3, 'type': 'heading'},
                {'children': [{'type': 'text', 'value': origin}], 'type': 'paragraph'}],
  }
  return res

desc = '''
最も重い荷物を最も楽に運ぶ方法、R TRUNK FRAME ep.3

ローローにとって、旅は移動と滞在の繰り返しです。
移動するときは便利でなければならないというこのシンプルな本質に忠実であるために、R TRUNKは生まれました。
SONYが開発した新素材SORPLAS™を使用し、韓国で初めてR TRUNKに適用されました。

POLYCARBONATE 100
SORPLAS™ by Sony Semiconductor Still
SONYが開発した新素材SORPLAS™は、30%に過ぎなかったリサイクル率を99%まで引き上げました。
リサイクル素材でありながら変形することなく堅牢で、優れた発色と高品質の仕上げが可能で、SONYの様々な製品の素材として使用されています。

ゴミと戦おう #fightwaste #fightwaste

TT HANDLE™ (TTハンドル)
広く伸びたハンドルで、服やバッグなどの荷物を掛けるのに適しています。
レザーやシリコングリップを使用して、お好みに合わせてカスタマイズすることができます。

SCALE HANDLE
トランクを持ち上げるだけで、どこでも簡単に重さを確認できます。
*63L、88L、105Lサイズのみ適用。

SILENT WHEEL
約20dBほど騒音が少ない日本ヒノモト社のサイレントホイールを採用。
360度スムーズに動き、手首の負担を軽減し、動線を簡単にコントロールできます。

TSA LOCK
米国運輸保安局が認証したロックで、破損することなく手荷物検査を受けることができます。

HIDEEN POCKET
紛失しがちなパスポートや財布などの小物を収納できます。

INSIDE
リサイクル抗菌素材の明るい裏地を使用し、暗い場所でも小物を見つけやすくなっています。
伸縮性のあるゴムバンドが内側から包み込んでくれるので、荷物が乱れにくく安定して収納できます。
'''.lstrip()

care = '''
1. 表面の汚れは柔らかい布と中性洗剤で拭いてください。
2. 紫外線を避け、湿度、温度が低く、風通しの良い場所に保管してください。
3. 使用後は、半日程度換気の良い場所で湿気を取り除いて保管してください。
4. 階段、アスファルトなど表面が粗い場所で無理に使用する場合、車輪の損傷の原因になることがあります。
5. 無理に荷物を入れて力を加えて閉める場合、フレームの変形やロックの故障などが発生する可能性があります。
6. 本製品は防水性がありませんので、雨天時には防水カバーを必ずご使用ください。
'''.lstrip()

size = '''
WEIGHT : 5.5kg

SIZE :
63L / 26inch 4~6days
BODY - W46 x H70 x D25.5
BAR HANDLE - W36.5 x H43.5
HIDDEN POCKET - W10.5 x H16 x D2 cm
'''.lstrip()

material = '''
OUTSIDE - POLYCARBONATE 100%
SORPLAS™ by Sony Semiconductor Still
INSIDE - POLYESTER
WHEELS - PLASTIC
'''.lstrip()

origin = 'CHINA'

s = get_product_description(desc, care, size, material, origin)

# to copy/paste into GraphiQL UI
print(json.dumps(s, ensure_ascii=False).replace('"', '\\"').replace('\\n', '\\\\n'))



"""
mutation updateProductMetafield($productSet: ProductSetInput!) {
  productSet(synchronous:true, input: $productSet) {
    product {
      id
      metafields (first:10) {
        nodes {
          id
          namespace
          key
          value
        }
      }
    }
    userErrors {
      field
      code
      message
    }
  }
}
"""

"""
{
  "productSet": {
    "id": "gid://shopify/Product/8735566954737",
    "metafields": [
      {
        "id": "gid://shopify/Metafield/37315032023281",
        "namespace": "custom",
        "key": "product_description",
        "type": "rich_text_field",
        "value": "{\"type\": \"root\", \"children\": [{\"children\": [{\"type\": \"text\", \"value\": \"商品説明\"}], \"level\": 3, \"type\": \"heading\"}, {\"children\": [{\"type\": \"text\", \"value\": \"最も重い荷物を最も楽に運ぶ方法、R TRUNK FRAME ep.3\\n \\nローローにとって、旅は移動と滞在の繰り返しです。\\n移動するときは便利でなければならないというこのシンプルな本質に忠実であるために、R TRUNKは生まれました。\\nSONYが開発した新素材SORPLAS™を使用し、韓国で初めてR TRUNKに適用されました。\\n\\nPOLYCARBONATE 100\\nSORPLAS™ by Sony Semiconductor Still\\nSONYが開発した新素材SORPLAS™は、30%に過ぎなかったリサイクル率を99%まで引き上げました。\\nリサイクル素材でありながら変形することなく堅牢で、優れた発色と高品質の仕上げが可能で、SONYの様々な製品の素材として使用されています。\\n\\nゴミと戦おう #fightwaste #fightwaste\\n\\nTT HANDLE™ (TTハンドル)\\n広く伸びたハンドルで、服やバッグなどの荷物を掛けるのに適しています。\\nレザーやシリコングリップを使用して、お好みに合わせてカスタマイズすることができます。\\n\\nSCALE HANDLE\\nトランクを持ち上げるだけで、どこでも簡単に重さを確認できます。\\n*63L、88L、105Lサイズのみ適用。\\n\\nSILENT WHEEL\\n約20dBほど騒音が少ない日本ヒノモト社のサイレントホイールを採用。\\n360度スムーズに動き、手首の負担を軽減し、動線を簡単にコントロールできます。\\n\\nTSA LOCK\\n米国運輸保安局が認証したロックで、破損することなく手荷物検査を受けることができます。\\n\\nHIDEEN POCKET\\n紛失しがちなパスポートや財布などの小物を収納できます。\\n\\nINSIDE\\nリサイクル抗菌素材の明るい裏地を使用し、暗い場所でも小物を見つけやすくなっています。\\n伸縮性のあるゴムバンドが内側から包み込んでくれるので、荷物が乱れにくく安定して収納できます。\\n\"}], \"type\": \"paragraph\"}, {\"children\": [{\"type\": \"text\", \"value\": \"使用上の注意\"}], \"level\": 3, \"type\": \"heading\"}, {\"children\": [{\"type\": \"text\", \"value\": \"1. 表面の汚れは柔らかい布と中性洗剤で拭いてください。\\n2. 紫外線を避け、湿度、温度が低く、風通しの良い場所に保管してください。\\n3. 使用後は、半日程度換気の良い場所で湿気を取り除いて保管してください。\\n4. 階段、アスファルトなど表面が粗い場所で無理に使用する場合、車輪の損傷の原因になることがあります。\\n5. 無理に荷物を入れて力を加えて閉める場合、フレームの変形やロックの故障などが発生する可能性があります。\\n6. 本製品は防水性がありませんので、雨天時には防水カバーを必ずご使用ください。\\n\"}], \"type\": \"paragraph\"}, {\"children\": [{\"type\": \"text\", \"value\": \"\"}], \"type\": \"paragraph\"}, {\"children\": [{\"type\": \"text\", \"value\": \"サイズ\"}], \"level\": 3, \"type\": \"heading\"}, {\"children\": [{\"type\": \"text\", \"value\": \"WEIGHT : 5.5kg\\n\\nSIZE :\\n63L / 26inch 4~6days\\nBODY - W46 x H70 x D25.5\\nBAR HANDLE - W36.5 x H43.5\\nHIDDEN POCKET - W10.5 x H16 x D2 cm\\n\"}], \"type\": \"paragraph\"}, {\"children\": [{\"type\": \"text\", \"value\": \"素材\"}], \"level\": 3, \"type\": \"heading\"}, {\"children\": [{\"type\": \"text\", \"value\": \"OUTSIDE - POLYCARBONATE 100%\\nSORPLAS™ by Sony Semiconductor Still\\nINSIDE - POLYESTER\\nWHEELS - PLASTIC\\n\"}], \"type\": \"paragraph\"}, {\"children\": [{\"type\": \"text\", \"value\": \"原産国\"}], \"level\": 3, \"type\": \"heading\"}, {\"children\": [{\"type\": \"text\", \"value\": \"CHINA\"}], \"type\": \"paragraph\"}]}"
      }
    ]
  }
}
"""