"""
This script used to calculate extraction percentages and extraction accuracy percentages
"""

# import libraries
import os
import json
import pandas as pd


def extraction_acc():
    """
    This function calculate extraction perc, and exxtraction accuracy perc
    """

    # read ip doc folder
    extracted_jsons = os.listdir(ip_folder_name)

    list_jsons = []

    # loop through each json
    for each_json in extracted_jsons:
        if ".json" in each_json:
            with open(os.path.join(ip_folder_name, each_json)) as f:
                data = json.load(f)
                data = json.loads(data)
                temp_dict = {}

                # create one dict for one file
                for each_entity in data:
                    temp_dict[each_entity['entity']] = each_entity['value']

                temp_dict["filename"] = each_json[:-5]

                list_jsons.append(temp_dict)

    # dataframe creation from json files
    extracted_df = pd.DataFrame(list_jsons)

    # create extraction csv
    extracted_df.to_csv(extraction_csv_path, index=False)

    # Extraction stats

    extracted_records = extracted_df.shape[0]

    print("============== Extraction stats ===============")

    print("total extracted_records", extracted_records)

    extraction_perc_df = extracted_df.isna().sum()
    extraction_dict = {}

    # extraction perc calclation
    for each_col, val in extraction_perc_df.iteritems():
        if each_col == "filename":
            continue
        extraction_dict[each_col] = {"missing_count": val, "extraction_percentage": 100 * (1 - round(val / extracted_records, 2))}

    print(extraction_dict)

    # taggers df

    taggers_df = pd.read_csv(data_taggers_csv_path)

    if rename_required:
        taggers_df.rename(columns=rename_columns, inplace=True)

    # remove file extension
    taggers_df['filename'] = taggers_df['filename'].apply(lambda x: x[:-4] if '.png' in x else x)

    # Both dfs should have same columns

    print("======== Extraction Accuracy Stats ==========")

    unique_cols = list(extracted_df.columns)
    join_key = "filename"
    unique_cols.remove(join_key)

    temp_df = pd.merge(extracted_df, taggers_df, how='inner', left_on=join_key, right_on=join_key)

    total_records = temp_df.shape[0]

    print("Extraction matched records with taggers data", total_records)

    extraction_data_matching_acc = {}

    # loop through each unique col
    for each_col in unique_cols:
        each_col_x = each_col + "_x"
        each_col_y = each_col + "_y"
        each_col_z = each_col + "_z"

        temp_df[each_col_z] = (temp_df[each_col_x] == temp_df[each_col_y])

        op = int(temp_df[each_col_z].sum())

        if total_records:
            extraction_data_matching_acc.update(
                {each_col: {"matched_records": op, "acc_perc": 100 * round((op / total_records), 2)}})
        else:
            extraction_data_matching_acc.update(
                {each_col: {"matched_records": op, "acc_perc": 0}})

    print(extraction_data_matching_acc)

    temp_df.to_csv(extraction_accuracy_csv_path, index=False)

    print("extraction accuracy process successfully completed")

if __name__=="__main__":

    # input variables

    ip_folder_name = "/home/venkatakrishna/Documents/Q/projects/doc-ai-test/paystub"
    extraction_csv_path = "/home/venkatakrishna/Documents/Q/projects/doc-ai-test/paystub/extracted-csv/extracted_entities.csv"
    data_taggers_csv_path = "/home/venkatakrishna/Documents/Q/projects/doc-ai-test/paystub/taggers-csv/taggers-paystub-test.csv"
    extraction_accuracy_csv_path = "/home/venkatakrishna/Documents/Q/projects/doc-ai-test/paystub/extracted-acc-csv/extraction-accuracy.csv"

    rename_required = True

    # rename data taggers cols, if they are different from standard key names
    rename_columns = {"Filename": "filename", "EMPLOYEE NAME": "name", "EMPLOYER NAME": "employer_name",
                      "EMPLOYER ADDRESS": "employer_address", "PAY PERIOD(FROM)": "pay_period_from",
                      "PAY PERIOD(TO)": "pay_period_to", "SSN": "ssn", "HOURS": "hours", "YTD Gross": "ytd",
                      "PAY DATE": "pay_date", "RATE": "rate"}

    # extraction accuracy function
    extraction_acc()

