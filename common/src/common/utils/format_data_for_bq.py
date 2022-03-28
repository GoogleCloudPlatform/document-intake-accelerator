"""
Function to format data to be inserted in Bigqury
"""

import json
from collections import ChainMap
def format_data_for_bq(entity):
  """
    Taakes list of dictionaries as input and converts it
    for BQ compatible format as string of dictionaries
    Args :
    entity : list of dictionaries
    output : string format of enties and values
  """
  new_list = []
  for i in entity:
    entity_dict = {}
    entity_dict[i.get("entity")] = i.get("value")
    new_list.append(entity_dict)
  res= dict(ChainMap(*new_list))
  new_json = json.dumps(res)
  return new_json
