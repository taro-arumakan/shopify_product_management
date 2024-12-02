import pandas as pd
df = pd.read_csv('/Users/taro/Downloads/products_export_1-2.csv')
df = df[df['Tags'].notnull()]
df = df[['Handle', 'Title', 'Tags']]
tagss = df['Tags'].to_list()
all_tags = sum((t.split(', ') for t in tagss), [])
all_tags = list(dict.fromkeys(all_tags))

def row_to_dict(row):
    res = dict(Handle=row['Handle'],
               Title=row['Title'])
    res.update({tag: tag in row['Tags'].split(', ') for tag in all_tags})
    return res
rows = [row_to_dict(row) for i, row in df.iterrows()]
tags_df = pd.DataFrame(rows, columns=['Handle', 'Title'] + all_tags)
tags_df = tags_df.sort_values(by=['Handle', 'Title'])
tags_df.to_csv('/Users/taro/Downloads/tags_df.csv', index=False)
