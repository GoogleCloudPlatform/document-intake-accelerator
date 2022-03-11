from fuzzywuzzy import fuzz
import json
import os
import logging
import pandas as pd
from matching_config import *
from utils import *
import datetime
import re


"""This script will help in matching two JSON files. JSON files can be loaded from
GCP or from local. An application form is approved if its values matches with at least these standard fields
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


def compare_dates(date1, date2, date1_format, date2_format):

    try:
        # expecting certain special characters in the date
        date1 = re.sub("[^0-9/\- ]", "",date1)
        date2 = re.sub("[^0-9/\- ]", "", date2)

        # finding the seperator / \ -
        delimiter1 = [c for c in date1_format if not c.isalpha()][0]
        delimiter2 = [c for c in date2_format if not c.isalpha()][0]

        # 
        d1_format = date1_format.split(delimiter1)
        d2_format = date2_format.split(delimiter2)

        # change 'y' --> 'Y'
        f1 = []
        for i in d1_format:
            if i[0] == 'y':
                f1.append(i[0].upper())
            else:
                f1.append(i[0])

        
        f2 = []
        for i in d2_format:
            if i[0] == 'y':
                f2.append(i[0].upper())
            else:
                f2.append(i[0])

        # # remove invalid characters from the date
        # clean_date1 = re.sub("[^0-9]", "", date1)
        # clean_date2 = re.sub("[^0-9]", "", date2)

        # create the format in which datetime module expects a string to be.
        d1_format = '%' + f1[0] + delimiter1 + '%' + f1[1] + delimiter1 + '%' + f1[2]

        d2_format = '%' + f2[0] + delimiter2 + '%' + f2[1] + delimiter2 + '%' + f2[2]

        # convert dates to similar format
        modified_date1 = datetime.datetime.strptime(date1, d1_format).strftime(d2_format)

        modified_date2 = datetime.datetime.strptime(date2, d2_format).strftime(d2_format)

        #compare
        if modified_date1 == modified_date2:
            return 1.0
        else:
            return 0.0
    
    except Exception as e:
        return 0.0

def compare_strings(str1, str2):
    if str1 is str2:
        return 1.0
    else:
        return 0.0

def compare_json(application_form_path: str, supporting_doc_path:str, support_doc_type:str):
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
        app_keys = list(app_df['key'])

        support_df = pd.DataFrame(support_json)
        support_keys = list(support_df['key'])
        
        if support_doc_type not in MATCHING_USER_KEYS_SUPPORTING_DOC:
            print("Unsupported supporting doc")
            return None

        support_doc_dict = MATCHING_USER_KEYS_SUPPORTING_DOC[support_doc_type]

        matched = []
        not_found = []

        for u_key in support_doc_dict.keys():

            # check if the user provided key is present in the both the docs
            # if found compare their respectives values
            if u_key in app_keys and u_key in support_keys:

                app_val = list(app_df.loc[app_df['key'] == u_key, 'value'])[0].lower()
                support_val = list(support_df.loc[support_df['key'] == u_key, 'value'])[0].lower()
                
                if app_val[-1] in ['\n', " "]:
                    app_val = app_val[:-1]

                if support_val[-1] in ['\n', " "]:
                    support_val = support_val[:-1]

                # match dates
                if isinstance(support_doc_dict[u_key], tuple): # a key signifies a date
                    matched.append(
                        compare_dates(
                            app_val,support_val, 
                           APPLICATION_DOC_DATE_FORMAT, support_doc_dict[u_key][1]
                           )*support_doc_dict[u_key][0] # date format for application doc and supporting doc
                    )
                
                # match values with only integers
                elif support_val.isdigit() and  app_val.isdigit():
                    matched.append(
                        compare_strings(support_val, app_val)*support_doc_dict[u_key]
                        )

                # match values with only characters
                else:
                    
                    # check if its a sentence or a single word

                    # if a sentence apply sort_ratio algo/cosine
                    if len(support_val.split()) >1 or len(app_val.split()) > 1:

                        # apply fuzzy logic
                        matched.append(float(fuzz.token_sort_ration(support_val, app_val))*support_doc_dict[u_key])
                    
                    else: # just do string to string comparison
                        matched.append(compare_strings(support_val, app_val))
            else:
                not_found.append(u_key)

        print("Matching Score: {0}%".format(sum(matched)/len(matched)*100))
    except Exception as e:
        print(e)
        return None

if __name__ == "__main__":
    
    # application_form_path = "/Users/sumitvaise/Documents/Quantiphi/extracted/desired_Illinois_UE_99.json"
    # supporting_doc_path = "/Users/sumitvaise/DOCAI/claims-processing/experimental/support.json"
    # support_doc_type = ""
    # compare_json(application_form_path, supporting_doc_path)
    date1, date2, date1_format, date2_format = "1234/5/21\n", "1234-5-21\n", 'yyyy/mm/dd', 'yyyy-mm-dd'
    print(compare_dates(date1, date2, date1_format, date2_format))