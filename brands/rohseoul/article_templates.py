def article_template_lookbook():
    res = r"""{
  "wrapper": "div.rohseoul-collection",
  "sections": {
    "main": {
      "type": "main-article",
      "disabled": true,
      "settings": {
        "color_scheme": ""
      }
    },
    "multi_column_8DXQtm": {
      "type": "multi-column",
      "blocks": {
        "image_with_text_q7eXDM": {
          "type": "image_with_text",
          "settings": {
            "title": "ROH SEOUL LOOKBOOK:",
            "heading_tag": "h4",
            "content": "",
            "link_url": "",
            "link_text": ""
          }
        },
        "image_with_text_yx6t7H": {
          "type": "image_with_text",
          "settings": {
            "title": "",
            "heading_tag": "h3",
            "content": "",
            "link_url": "",
            "link_text": ""
          }
        },
        "image_with_text_Mf4qUd": {
          "type": "image_with_text",
          "settings": {
            "title": "${LOOKBOOK_TITLE}",
            "heading_tag": "h3",
            "content": "",
            "link_url": "",
            "link_text": ""
          }
        }
      },
      "block_order": [
        "image_with_text_q7eXDM",
        "image_with_text_yx6t7H",
        "image_with_text_Mf4qUd"
      ],
      "custom_css": [
        ".multi-column {row-gap: 0;}"
      ],
      "settings": {
        "color_scheme": "",
        "separate_section_with_border": false,
        "columns_per_row": 3,
        "stack_on_mobile": true,
        "overlap_image": false,
        "content_alignment": "start",
        "text_alignment": "start",
        "spacing": "sm",
        "subheading": "",
        "title": "",
        "content": ""
      }
    }
  },
  "order": [
    "main",
    "multi_column_8DXQtm"
  ]
}"""
    return res


def article_template_campaign():
    res = r"""{
  "wrapper": "div.rohseoul-collection",
  "sections": {
    "main": {
      "type": "main-article",
      "disabled": true,
      "settings": {
        "color_scheme": ""
      }
    },
    "multi_column_8DXQtm": {
      "type": "multi-column",
      "blocks": {
        "image_with_text_q7eXDM": {
          "type": "image_with_text",
          "settings": {
            "title": "ROH SEOUL CAMPAIGN:",
            "heading_tag": "h4",
            "content": "<h4>${CAMPAIGN_TITLE}</h4>",
            "link_url": "",
            "link_text": ""
          }
        },
        "image_with_text_yx6t7H": {
          "type": "image_with_text",
          "settings": {
            "title": "${CAMPAIGN_SUBTITLE}",
            "heading_tag": "h5",
            "content": "",
            "link_url": "",
            "link_text": ""
          }
        },
        "image_with_text_Mf4qUd": {
          "type": "image_with_text",
          "settings": {
            "title": "",
            "heading_tag": "h3",
            "content": "<p>${CAMPAIGN_DESCRIPTION}</p>",
            "link_url": "",
            "link_text": ""
          }
        }
      },
      "block_order": [
        "image_with_text_q7eXDM",
        "image_with_text_yx6t7H",
        "image_with_text_Mf4qUd"
      ],
      "settings": {
        "color_scheme": "",
        "separate_section_with_border": false,
        "columns_per_row": 3,
        "stack_on_mobile": true,
        "overlap_image": false,
        "content_alignment": "start",
        "text_alignment": "start",
        "spacing": "sm",
        "subheading": "",
        "title": "",
        "content": ""
      }
    }
  },
  "order": [
    "main",
    "multi_column_8DXQtm"
  ]
}"""
    return res
