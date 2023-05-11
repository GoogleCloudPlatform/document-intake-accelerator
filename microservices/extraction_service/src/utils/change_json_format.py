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
  This module used to format response

  Input json format
  json=[{
        "entity": "name",
        "value": "Kathr1n    marie",
        "key_confidence": 1.0,
        "value_confidence": 1.0
    },
    {
        "entity": "dob",
        "value": "2022-jan-09\n",
        "key_confidence": 1.0,
        "value_confidence": 1.0
    },
    {
        "entity": "phone_no",
        "value": "123A",
        "key_confidence": 1.0,
        "value_confidence": 1.0
    },
    {
        "entity": "address",
        "value": "XYZ",
        "key_confidence": 1.0,
        "value_confidence": 1.0
    },
    ]
"""

from collections import ChainMap

def get_json_format_for_processing(input_json):
  """Function to change list of dictionary json format to key value mapping
        dictionary
  Input:
    input_json: input json with list of dictionary format
  Output:
    new_json: list of key value mapping dictionary"""

  a = input_json
  new_list = []
  # for dictionary in input json
  for i in a:
    # get list of keys for the dictionary
    a = {}
    # create a dictionary from input dictionary
    a[i.get("entity")] = i.get("value")
    # append the new dictionary in a list
    new_list.append(a)
  res = {}
  # convert list to dictionary
  res = dict(ChainMap(*new_list))
  # get new_json as list of dictionary
  new_json = [res]
  return new_json


def correct_json_format_for_db(output_dict, input_json):
  """Function to add a list of dictionary for key value mapping
       to input list of dictionary json
  Input:
    output_dict: list of dictionary with key value mapping
    input_json: list of dictionary json
  Output:
    input_json: list of dictionary json"""
  print(f"input: {input_json}")
  # traverse input json
  for item in input_json:
    # traverse the keys in dictionary
    for entity in output_dict[0].keys():
      # if keys are matched
      if item.get("entity") == entity:
        # reassign input json value to new one
        item["value"] = output_dict[0][entity]
  print(f"output: {output_dict}")
  return input_json
