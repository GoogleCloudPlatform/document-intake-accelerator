import pandas as pd

taggers_df = pd.read_csv("dl-docs/Copy of Doc AI Entities - DL-Taggers-sort.csv")
extracted_df = pd.read_csv("dl-docs/DL_entities_without_noisy-new.csv")

# Both dfs should have same structure
unique_cols = list(extracted_df.columns)
join_key = "FileName"
unique_cols.remove(join_key)

temp_df = pd.merge(extracted_df, taggers_df, how='inner', left_on=join_key, right_on=join_key)

total_records = temp_df.shape[0]

print("total records", total_records)

result_df = pd.DataFrame()

extraction_data_matching_acc = {"total_records": total_records}
for each_col in unique_cols:
    each_col_x = each_col+ "_x"
    each_col_y = each_col + "_y"
    each_col_z = each_col + "_z"

    temp_df[each_col_z] = (temp_df[each_col_x] == temp_df[each_col_y])

    op = temp_df[each_col_z].sum()
    extraction_data_matching_acc.update({each_col: {"matched_records": op, "acc_perc": round(op*100/total_records, 2)}})

    # print(op)

print(extraction_data_matching_acc)

temp_df.to_csv("dl-docs/extracted_data_match-new.csv")

# Identifying unmatched cols

actual_cols = list(extracted_df["FileName"])
matched_cols = list(temp_df["FileName"])

unmatched_cols = [col for col in actual_cols if col not in matched_cols]

print("debug")