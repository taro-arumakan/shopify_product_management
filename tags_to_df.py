import pandas as pd
df = pd.read_csv('/Users/taro/Downloads/products_export_1-2.csv')
df = df[df['Tags'].notnull()]
df = df[['Handle', 'Title', 'Tags']]
tagss = df['Tags'].to_list()
tags = sum((t.split(', ') for t in tagss), [])
tags = list(dict.fromkeys(tags))

tags_df = pd.DataFrame(columns=['Handle', 'Title'] + tags)
for index, row in df.iterrows():
    tagstf = [tag in row['Tags'].split(', ') for tag in tags]
    tags_df.loc[index] = [row['Handle'], row['Title']] + tagstf
tags_df = tags_df.sort_values(by=['Handle', 'Title'])
tags_df.to_csv('/Users/taro/Downloads/tags_df.csv', index=False)
