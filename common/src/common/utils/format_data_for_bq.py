"""
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
  if entity is not None:
    new_list = []
    for i in entity:
      entity_dict = {}
      entity_dict[i.get("entity")] = i.get("value")
      new_list.append(entity_dict)
    res= dict(ChainMap(*new_list))
    new_json = json.dumps(res)
    return new_json
  else:
    return None
