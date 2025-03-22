lines = '''/*
 * ------------------------------------------------------------
 * IMPORTANT: The contents of this file are auto-generated.
 *
 * This file may be updated by the Shopify admin theme editor
 * or related systems. Please exercise caution as any changes
 * made to this file may be overwritten.
 * ------------------------------------------------------------
 */
{
  "wrapper": "div.page-tt_handle",
  "sections": {
    "main": {
      "type": "main-page",
      "disabled": true,
      "settings": {
        "color_scheme": "",
        "show_title": true,
        "page_width": "xs"
      }
    },
    "images_list_A8pTVn": {
      "type": "images-list",
      "blocks": {
        "image_zmfUBA": {
          "type": "image",
          "settings": {
            "image": "shopify://shop_images/lp_tthandle_000.png"
          }
        },
        "image_kDbdKr": {
          "type": "image",
          "settings": {
            "image": "shopify://shop_images/lp_tthandle_001.png"
          }
        },
        "image_WpyDQC": {
          "type": "image",
          "settings": {
            "image": "shopify://shop_images/lp_tthandle_002.png"
          }
        },
        "image_dNzhUR": {
          "type": "image",
          "settings": {
            "image": "shopify://shop_images/lp_tthandle_003.png"
          }
        },
        "image_Yj4YXx": {
          "type": "image",
          "settings": {
            "image": "shopify://shop_images/lp_tthandle_004.png"
          }
        },
        "image_wGQmRg": {
          "type": "image",
          "settings": {
            "image": "shopify://shop_images/lp_tthandle_005.png"
          }
        },
        "image_DK8BUN": {
          "type": "image",
          "settings": {
            "image": "shopify://shop_images/lp_tthandle_006.png"
          }
        },
        "image_kj8tnW": {
          "type": "image",
          "settings": {
            "image": "shopify://shop_images/lp_tthandle_007.png"
          }
        },
        "image_kqYicx": {
          "type": "image",
          "settings": {
            "image": "shopify://shop_images/lp_tthandle_008.png"
          }
        }
      },
      "block_order": [
        "image_zmfUBA",
        "image_kDbdKr",
        "image_WpyDQC",
        "image_dNzhUR",
        "image_Yj4YXx",
        "image_wGQmRg",
        "image_DK8BUN",
        "image_kj8tnW",
        "image_kqYicx"
      ],
      "custom_css": [
        ".images-list-item:nth-of-type(2) {margin-top: 11vh;}",
        ".images-list-item:nth-of-type(3),.images-list-item:nth-of-type(4),.images-list-item:nth-of-type(5),.images-list-item:nth-of-type(6) {margin-top: 8vh;}"
      ],
      "settings": {
        "color_scheme": "",
        "image_position": "center",
        "overlay_color": "#000000",
        "overlay_opacity": 0
      }
    }
  },
  "order": [
    "main",
    "images_list_A8pTVn"
  ]
}'''.splitlines()
image_file_names = [line.strip().replace('"image": "shopify://shop_images/', '')[:-1] for line in lines if line.strip().startswith('"image": "shopify://shop_images/')]
print(image_file_names)

from shopify_product_management.shopify_utils import image_htmlfragment_in_description
SHOPIFY_FILE_URL_PREFIX = 'https://cdn.shopify.com/s/files/1/0726/9187/6081/'
paths = [image_htmlfragment_in_description(image_file_name, i, SHOPIFY_FILE_URL_PREFIX) for i, image_file_name in enumerate(image_file_names)]
import pprint
pprint.pprint(paths, width=200)
description = '\n'.join(paths)
print(description)

