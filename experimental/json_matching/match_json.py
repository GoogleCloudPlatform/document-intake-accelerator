"""This script will help in matching two JSON files. JSON files
can be loaded from GCP or from local. An application form is approved
if its values matches with at least these standard fields
values as referenced in
https://docs.google.com/spreadsheets/d/1WB_fSH-nrsknoJyP0qvPmAt6y
-ZQKxzXPZzAp62QQrQ/edit?resourcekey=0-Z5uzfFoLMCM3OQd27wZ_Yw#gid=810561467
"""

import datetime
import re
import os
import json

from fuzzywuzzy import fuzz
import pandas as pd
from matching_config import MATCHING_USER_KEYS_SUPPORTING_DOC
from matching_config import APPLICATION_DOC_DATE_FORMAT
from matching_utils import download_file_gcs



def download_and_load_file(file_path: str) -> json:
  """ Downloads the file from GCS or local"""

  if file_path[:3] == 'gs:' and file_path.endswith('.json'):
    temp_file = download_file_gcs(gcs_uri=file_path)

  # if not a GCS Path then its a local path
  elif file_path.endswith('.json') and os.path.exists(file_path):
    temp_file = file_path
  else:
    return None

  with open(temp_file, 'r', encoding='utf-8') as tfile:
    data = json.load(tfile)
  del temp_file
  return data


def compare_dates(date1: str, date2: str,
                  date1_format: str, date2_format: str):
  """Dates are compared after converting them to a specific format
  For this each dates format should be provided.

  Args:
      date1 (str): date 1 in str format
      date2 (str): date 2 in str format
      date1_format (str):  date format in str format
       Ex. 'yyyy/mm/dd' or 'yyyy-mm-dd'
      date2_format (str): date format in str format
      Ex. 'yyyy/mm/dd' or 'yyyy-mm-dd'

  Returns:
      _type_: _description_
  """
  try:
    # expecting certain special characters in the date
    date1 = re.sub(r'[^0-9/\- ]', '', date1)
    date2 = re.sub(r'[^0-9/\- ]', '', date2)

    # convert dates to similar format
    modified_date1 = datetime.datetime.strptime(
        date1, date1_format).strftime(date2_format)

    modified_date2 = datetime.datetime.strptime(
        date2, date2_format).strftime(date2_format)

    #compare
    if modified_date1 == modified_date2:
      return 1.0
    else:
      return 0.0
  except ValueError:
    print('Invalid date format does not match with the date')
    return 0.0


def compare_json(application_form_path: str, supporting_doc_path: str,
                 support_doc_type: str):
  """Function takes two JSON files, 1. application form JSON and 2.
   supporting doc JSON file
  Args:
      application_form_path (str): JSON file path (GCS/local). For GCS path,
       a file's gcs uri is required
      supporting_doc_path (str): JSON file path (GCS/local)
  """
  # Load the JSONs
  app_json = download_and_load_file(application_form_path)
  support_json = download_and_load_file(supporting_doc_path)


  # Both JSON should be available for comparison

  # run the comparison for = total keys in the supporting docs
  app_df = pd.DataFrame(app_json)
  app_keys = list(app_df['key'])

  support_df = pd.DataFrame(support_json)
  support_keys = list(support_df['key'])

  if support_doc_type not in MATCHING_USER_KEYS_SUPPORTING_DOC:
    print('Unsupported supporting doc')
    return None

  support_doc_dict = MATCHING_USER_KEYS_SUPPORTING_DOC[support_doc_type]
  matched = []
  not_found = []

  for u_key in support_doc_dict.keys():
    # check if the user provided key is present in the both the docs
    # if found compare their respectives values
    if u_key in app_keys and u_key in support_keys:
      app_val = list(app_df.loc[app_df['key'] == u_key, 'value'])[0].lower()
      support_val = list(
          support_df.loc[support_df['key'] == u_key, 'value'])[0].lower()

      if app_val[-1] in ['\n', ' ']:
        app_val = app_val[:-1]

      if support_val[-1] in ['\n', ' ']:
        support_val = support_val[:-1]

      # 1. check for dates. date related keys contains value in tuple format
      if isinstance(support_doc_dict[u_key], tuple): # a key signifies a date
        matched.append(
            compare_dates(
                app_val, support_val,
                APPLICATION_DOC_DATE_FORMAT, support_doc_dict[u_key][1]
                )*support_doc_dict[u_key][0]
        )

      # 2. match values with only integers
      elif support_val.isdigit() and  app_val.isdigit():
        matched.append(
            (1.0 if support_val == app_val else 0.0)*support_doc_dict[u_key])

      # 3. match values with only characters
      else:

        # check if its a sentence or a single word
        # if a sentence apply fuzzy logic
        if len(support_val.split(' ')) > 1 or len(app_val.split(' ')) > 1:
          # apply fuzzy logic --> score x wts
          score = float(fuzz.token_sort_ratio(
              support_val, app_val)/100)*support_doc_dict[u_key]
          matched.append(score)
        else:
          matched.append(
            (1.0 if support_val == app_val else 0.0)*support_doc_dict[u_key])

    else:
      not_found.append(u_key)

  return (
      f'Matching Score: {round(sum(matched),2)}',
      f'KeysNotFound: {not_found}')
