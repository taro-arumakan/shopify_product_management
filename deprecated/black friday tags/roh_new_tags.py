import pandas as pd
df = pd.read_csv(r'/Users/taro/Downloads/ROH\ SEOUL\ Products\ mst\ -\ products\ mst-3.csv'.replace('\\', ''))
df = df[2:]

df = df.rename(columns={'商品名\n상품명': 'Title', '品番\n품번': 'SKU',
                        'コレクション①\n컬렉션': 'collection',
                        'バッグ\nカテゴリー①\n상세 카테고리': 'tag1',
                        'バッグ\nカテゴリー②\n상세 카테고리': 'tag2',
                        'バッグ\nカテゴリー③\n상세 카테고리': 'tag3'})

df.fillna({'tag3': 0}, inplace=True)
df['Tags'] = df[['collection', 'tag1', 'tag2', 'tag3']].apply(lambda x: ', '.join(set(filter(None, x))), axis=1)


products = pd.read_csv(r'/Users/taro/Downloads/roh_products_export_20241121_2.csv')
products = products[products['Variant SKU'].notnull()]
products = products[['Handle', 'Title', 'Variant SKU', 'Tags']]
products = products.ffill()

def merge_tags(tags, new_tags):
    tags = [tag for tag in tags.split(', ') if tag in ['new', 'recommend']]
    tags += new_tags.split(', ')
    tag_map = {'Bag': 'bag',
               'Backpack': 'backpack'}
    tags = [tag_map.get(tag, tag) for tag in tags]
    return ', '.join(set(tags))

products['Tags'] = products[['Variant SKU', 'Tags']].apply(lambda x: merge_tags(x['Tags'], df[df['SKU'] == x['Variant SKU']]['Tags'].iloc[0]), axis=1)
s = products.groupby('Handle')['Tags'].nunique()
assert s[s > 1].empty, "multiple set of tags for a product"

products[['Handle', 'Title', 'Tags']].drop_duplicates().to_csv('/Users/taro/Downloads/roh_new_tags.csv', index=False)

# products['Collection'] = products['Tags'].apply(lambda x: [s for s in x.split(', ') if s in ['Summer24', 'Fall 24', 'RESORT24', 'spring 24']])
# products[products['Collection'].map(len) > 1].to_csv('/Users/taro/Downloads/roh_multiple_collections.csv')
# products = products[products['Collection'].map(len) == 1]
# products['Collection'] = products['Collection'].apply(lambda x: x[0])
# products[['Variant SKU', 'Collection']].to_csv('/Users/taro/Downloads/roh_collection.csv')
