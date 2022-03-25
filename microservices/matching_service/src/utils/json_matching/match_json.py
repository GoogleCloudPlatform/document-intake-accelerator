"""This script will help in matching two JSON files. JSON files
can be loaded from GCP or from local. An application form is approved
if its values matches with at least these standard fields
values as referenced below
https://docs.google.com/spreadsheets/d/1WB_fSH-nrsknoJyP0qvPmAt6y
-ZQKxzXPZzAp62QQrQ/edit?resourcekey=0-Z5uzfFoLMCM3OQd27wZ_Yw#gid=810561467
"""

import datetime
from fuzzywuzzy import fuzz
import pandas as pd
from utils.json_matching.matching_config import MATCHING_USER_KEYS_SUPPORTING_DOC
from utils.json_matching.matching_config import APPLICATION_DOC_DATE_FORMAT
from common.utils.logging_handler import Logger


def compare_dates(date1: str,date2: str,date1_format: str,date2_format: str):
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
    # date1 = re.sub(r'[^0-9/\- ]', '', date1)
    # date2 = re.sub(r'[^0-9/\- ]', '', date2)

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
    Logger.error('Invalid date format does not match with the date provided.')
    return 0.0


def compare_json(application_json_obj, supporting_json_obj, SD_doc_type,
                 AF_doc_type, context):
  """Function takes two JSON files, 1. application form JSON and 2.
   supporting doc JSON file
  Args:
  Returns: json object with a dictionary expressing the matching score.
  """
  try:
    # Get the doc type for application doc and supporting doc
    support_doc_type = SD_doc_type.lower()
    app_doc_type = AF_doc_type.lower()
    state = context.lower()
    out_sd_dict = []
    # Both JSON should be available for comparison

    # run the comparison for = total keys in the supporting docs
    app_df = pd.DataFrame(application_json_obj)
    app_keys = list(app_df['entity'])
    print(app_keys)
    Logger.info(app_keys)
    support_df = pd.DataFrame(supporting_json_obj)
    support_df['matching_score'] = 0.0
    support_keys = list(support_df['entity'])
    print(support_keys)
    Logger.info(app_keys)
    if support_doc_type not in MATCHING_USER_KEYS_SUPPORTING_DOC:
      Logger.error('Unsupported supporting doc')
      return None

    support_doc_dict = MATCHING_USER_KEYS_SUPPORTING_DOC[support_doc_type]
    matched = []
    not_found = []

    for u_key in support_doc_dict.keys():
      # check if the user provided key is present in the both the docs
      # if found compare their respectives values
      if u_key in app_keys and u_key in support_keys:
        app_val = list(app_df.loc[app_df['entity'] == u_key,
                                  'value'])[0].lower()
        support_val = list(support_df.loc[support_df['entity'] == u_key,
                                          'value'])[0].lower()

        if app_val[-1] in ['\n', ' ']:
          app_val = app_val[:-1]

        if support_val[-1] in ['\n', ' ']:
          support_val = support_val[:-1]

        # 1. check for dates. date related keys contains value in tuple format
        if isinstance(support_doc_dict[u_key], tuple):# a key signifies a date
          wt_score = compare_dates(
              app_val, support_val,
              APPLICATION_DOC_DATE_FORMAT[app_doc_type][state],
              support_doc_dict[u_key][1]) * support_doc_dict[u_key][0]

          matched.append(round(wt_score, 2))

        # 2. match values with only integers
        # remove any special characters 
        # and check if the remaining string is contains
        # # only digit
        # elif re.sub('[^A-Za-z0-9]+', '', support_val).isdigit() and \
        #             re.sub('[^A-Za-z0-9]+', '', app_val).isdigit():
        elif support_val.isdigit() and app_val.isdigit():
          wt_score = (1.0 if support_val == app_val else
                      0.0) * support_doc_dict[u_key]
          matched.append(round(wt_score, 2))

        # 3. match values with only characters
        else:
          # if a sentence apply fuzzy logic
          wt_score = float(fuzz.token_sort_ratio(support_val, app_val) / 100)
          wt_score = round(wt_score * support_doc_dict[u_key], 2)
          matched.append(wt_score)

        final_score = wt_score
      else:
        final_score = 0.0

      for i_dict in supporting_json_obj:
        if u_key == i_dict['entity']:
          i_dict['matching_score'] = final_score
          out_sd_dict.append(i_dict)

    avg_matching_score = {'Avg Matching Score': round(sum(matched), 2)}
    out_sd_dict.append(avg_matching_score)

    return out_sd_dict

  except Exception as e:
    Logger.error(e)
    return None
