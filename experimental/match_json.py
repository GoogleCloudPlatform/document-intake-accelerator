from email.policy import strict
import json
import os
import logging
import pandas as pd

from utils import download_file_gcs


"""This script will help in matching two JSON files. JSON files can be loaded from
GCP or from local. An application form is approved if its values matches with atleast these standard fields
values as referenced in
https://docs.google.com/spreadsheets/d/1WB_fSH-nrsknoJyP0qvPmAt6y-ZQKxzXPZzAp62QQrQ/edit?resourcekey=0-Z5uzfFoLMCM3OQd27wZ_Yw#gid=810561467 
"""

def download_and_load_file(file_path: str) -> json: 
    """ Downloads the file from GCS or local"""

    if file_path[:3] == 'gs:' and file_path.endswith('.json'):
        temp_file = download_file_gcs(gcs_uri=file_path)

    # if not a GCS Path then its a local path
    elif file_path.endswith('.json') and os.path.exists(file_path):
        temp_file = file_path
    
    else:
        return None

    return json.load(open(temp_file, 'r'))

def compare_json(application_form_path: str, supporting_doc_path:str):
    """Function takes two JSON files, 1. application form JSON and 2. supporting doc JSON file


    Args:
        application_form_path (str): JSON file path (GCS/local). For GCS path, a file's gcs uri is required
        supporting_doc_path (str): JSON file path (GCS/local)
    """
    # Load the JSONs
    app_json = download_and_load_file(application_form_path)
    support_json = download_and_load_file(supporting_doc_path)


    # Both JSON should be available for comparison
    try:
        # run the comparison for = total keys in the supporting docs
        app_df = pd.DataFrame(app_json)
        support_df = pd.DataFrame(support_json)
        
        total_keys = len(support_df)
        matched = 0
        not_found = []

        for s_key in list(support_df['key']):

            # check if the same key is also present in the application doc
            # if found compare their respectives values
            if s_key in list(app_df['key']):

                app_val = list(app_df.loc[app_df['key'] == s_key, 'value'])[0]
                support_val = list(support_df.loc[support_df['key'] == s_key, 'value'])[0]
                
                # remove '\n' and whitespaces
                if "".join(app_val.split()) == "".join(support_val.split()):
                    matched +=1
            else:
                not_found.append(s_key)

        print("Matching Score: {0}%".format(matched/total_keys*100))
    except Exception as e:
        print(e)
        return None

if __name__ == "__main__":
    
    application_form_path = "/Users/sumitvaise/Documents/Quantiphi/extracted/desired_Illinois_UE_99.json"
    supporting_doc_path = "/Users/sumitvaise/DOCAI/claims-processing/experimental/support.json"

    compare_json(application_form_path, supporting_doc_path)