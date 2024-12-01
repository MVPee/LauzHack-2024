import pandas as pd
# keep only rows with and external_id present more times than a threshold

df = pd.read_csv('./data/train/persons_association_2.csv')
# transaction_reference_id,external_id
min_threshold = 1
max_threshold = 10
external_ids_count = df['external_id'].value_counts().sort_values(ascending=False)
print(external_ids_count)
#filtered_df = df[df['external_id'].isin(external_ids_count[external_ids_count > min_threshold].index)]
filtered_df = df[df['external_id'].isin(external_ids_count[(external_ids_count > min_threshold) & (external_ids_count < max_threshold)].index)]
print(filtered_df.shape)


filtered_df.to_csv('./data/train/persons_association_filtred.csv', index=False)