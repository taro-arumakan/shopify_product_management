import json

with open('collection.lookbook-24-summer.json') as f:
    j = json.loads(f.read())

current_series = False
subserieses = []

for k, v in j['sections'].items():
    if k.startswith('rich_text'):
        for kk, vv in v['blocks'].items():
            current_series = vv['settings']['text']
            subserieses = []
    elif current_series and k.startswith('multi_column'):
        for kk, vv in v['blocks'].items():
            assert kk.startswith('image_with_text'), kk
            if 'image' in vv['settings']:
                title = vv['settings']['title']
                image = vv['settings']['image']
                content = vv['settings']['content']
                subserieses.append((title, image, content))
    print(current_series)
    print(subserieses)
    print()
