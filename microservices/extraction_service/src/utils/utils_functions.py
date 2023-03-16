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
This script has all the common and re-usable functions
required for extraction framework
"""
import os
import re
import pandas as pd
import numpy as np
from functools import reduce
from google.cloud import storage
from .table_extractor import TableExtractor
from common.utils.logging_handler import Logger


def pattern_based_entities(parser_data, pattern):
  """
  Function return matched text as per pattern
  Parameters
  ----------
  parser_data: text in which pattern is applied
  pattern : pattern
  Returns: Extracted text by using pattern
  -------
  """

  text = parser_data["text"]
  pattern = re.compile(pattern, flags=re.DOTALL)
  # match as per pattern
  matched_text = re.search(pattern, text)
  if matched_text:
    op = matched_text.group(1)
  else:
    op = None
  return op


def update_confidence(dupp, without_noise):
  for key in dupp.keys():
    for i in without_noise:
      if i["key"] == key:
        i["value_confidence"] = 0.0
  return without_noise


def check_duplicate_keys(dictme, without_noise):
  # dictme is the mapping dictionary
  # without_noise is the raw dictionary which comes from Form parser
  dupp = {}
  for j, k in dictme.items():
    # print(j,k)
    if len(k) > 1:
      dupp[j] = len(k)
  for j, k in dupp.items():
    count = 0
    for i in without_noise:
      if i["key"] == j:
        count = count + 1
    # remove this later
    count = 0
    if count != k:
      without_noise = update_confidence(dupp, without_noise)
      return False

  return True


def default_entities_extraction(parser_data, default_entities, doc_type):
  """
   This function extracted default entities
   Parameters
   ----------
   parser_entities: Specialized parser entities
   default_entities: Default entities that need to extract from parser entities
   Returns : Default entites dict
   -------
  """
  parser_entities_dict = {}
  parser_entities = parser_data["entities"]
  pages_dimensions = []
  page_no = 0

  # Todo add recognizing of the page number and taking proper dimensions. now assume one page only
  for page in parser_data["pages"]:
    dimension = page["dimension"]
    pages_dimensions.append(dimension)

  # retrieve parser given entities
  for each_entity in parser_entities:
    # print(each_entity)
    key, val, confidence = each_entity.get("type", ""), \
                           each_entity.get("mentionText", ""), round(
        each_entity.get("confidence", 0), 2)
    val = strip_value(val)
    parser_entities_dict[key] = [val, confidence]

    for prop in each_entity.get("properties", []):
      key, val, confidence = prop.get("type", ""), \
                             prop.get("mentionText", ""), \
                             round(prop.get("confidence", 0), 2)
      val = strip_value(val)

      pa = prop.get("pageAnchor")
      if pa and len(pa.get("pageRefs", [])) > 0:
        page_no = int(pa.get("pageRefs")[0].get("page"))
        value_coordinates = []
        value_coordinates_dic = pa.get("pageRefs")[0].get("boundingPoly").get(
            "normalizedVertices")
        for coordinate in value_coordinates_dic:
          value_coordinates.append(float(coordinate["x"]))
          value_coordinates.append(float(coordinate["y"]))
      else:
        value_coordinates = []

      parser_entities_dict[key] = [val, confidence, value_coordinates]

  entity_dict = {}

  # create default entities
  for key in default_entities:
    if key in parser_entities_dict:
      entity_dict[default_entities[key][0]] = {
          "entity": default_entities[key][0],
          "value": parser_entities_dict[key][0],
          "extraction_confidence": parser_entities_dict[key][1],
          "value_coordinates": parser_entities_dict[key][2],
          "manual_extraction": False,
          "key_coordinates": parser_entities_dict[key][2],
          "corrected_value": None,
          "page_no": page_no + 1,
          "page_width": int(pages_dimensions[page_no]["width"]),
          "page_height": int(pages_dimensions[page_no]["height"])
      }
    else:
      # Entity not present
      entity_dict[default_entities[key][0]] = {
          "entity": default_entities[key][0], "value": None,
          "extraction_confidence": None,
          "value_coordinates": [],
          "key_coordinates": [],
          "manual_extraction": False,
          "corrected_value": None,
          "page_no": None,
          "page_width": None,
          "page_height": None

      }

  if doc_type == "utility_bill":
    if "supplier_address" in parser_entities_dict:
      if parser_entities_dict["supplier_address"][0] == "":
        if "receiver_address" in parser_entities_dict \
            and parser_entities_dict["receiver_address"][0] != "":
          entity_dict["reciever address"]["value"] = \
            parser_entities_dict["receiver_address"][0]
        else:
          if "service_address" in parser_entities_dict:
            entity_dict["reciever address"]["value"] = \
              parser_entities_dict["service_address"][0]
  return entity_dict


def name_entity_creation(entity_dict, name_list):
  """
    This function is to create name from Fname and Gname.
    Can be re-used if it helps
    Parameters
    ----------
    entity_dict: extracted entities dict
    name_list: list of varibles required to create name
    Returns : derived name entitity dict
    -------
  """
  name = ""
  confidence = 0

  # loop through all the name variables used for name creation
  for each_name in name_list:
    parser_extracted_name = entity_dict[each_name]["value"]
    if parser_extracted_name:
      name += parser_extracted_name
      confidence += entity_dict[each_name]["extraction_confidence"]

  if name.strip():
    name = name.strip()
    confidence = round(confidence / len(name_list), 2)
  else:
    name = None
    confidence = None

  name_dict = {
      "entity": "Name", "value": name,
      "extraction_confidence": confidence,
      "manual_extraction": False,
      "corrected_value": None}

  return name_dict


def derived_entities_extraction(parser_data, derived_entities):
  """
    This function extract/create derived entities based on config
    derived entity section
    Parameters
    ----------
    parser_data: text in which pattern is applied
    derived_entities: derived entities dict and pattern
    Returns: derived entities dict
    -------
  """

  derived_entities_extracted_dict = {}

  # loop through derived entities
  for key, val in derived_entities.items():
    pattern = val["rule"]
    pattern_op = pattern_based_entities(parser_data, pattern)
    pattern_op = strip_value(pattern_op)
    derived_entities_extracted_dict[key] = \
      {"entity": key, "value": pattern_op,
       "extraction_confidence": None,
       "manual_extraction": True,
       "corrected_value": None,
       "value_coordinates": None,
       "key_coordinates": None,
       "page_no": None,
       "page_width": None,
       "page_height": None
       }

  return derived_entities_extracted_dict


def entities_extraction(parser_data, required_entities, doc_type):
  """
    This function reads information of default and derived entities
    Parameters
    ----------
    parser_data: specialized parser result
    required_entities: required extracted entities
    doc_type: Document type
    Returns: Required entities dict
    -------
  """

  # Read the entities from the processor
  parser_entities = parser_data["entities"]
  print(f"parser_entities = {parser_entities}")
  default_entities = required_entities["default_entities"]
  print(f"default_entities={default_entities}")
  derived_entities = required_entities.get("derived_entities")
  print(f"derived_entities={derived_entities}")
  # Extract default entities
  entity_dict = default_entities_extraction(parser_data,
                                            default_entities, doc_type)
  Logger.info("Default entities created from Specialized parser response")
  # if any derived entities then extract them
  if derived_entities:
    # this function can be used for all docs, if derived entities
    # are extracted by using regex pattern
    derived_entities_extracted_dict = derived_entities_extraction \
      (parser_data, derived_entities)
    entity_dict.update(derived_entities_extracted_dict)
    Logger.info("Derived entities created from Specialized parser response")
  return entity_dict


def check_int(d):
  """
    This function check given string is integer
    Parameters
    ----------
    d: input string
    Returns: True/False
    -------
  """
  count = 0
  date_val = ""
  for i in d:
    if i and (i.strip()).isdigit():
      count = count + 1
      date_val += str(i.strip())

  flag = ((count >= 2) and (len(date_val) < 17))
  return flag


def consolidate_coordinates(d):
  """
    This function create co-ordinates for groupby entities
    Parameters
    ----------
    d: entity co-ordinates list

    Returns: List of co-ordinates
    -------
  """
  entities_cooridnates = []

  if len(d) > 1:
    for i in d:
      if i:
        entities_cooridnates.append(i)
    if entities_cooridnates:
      entity_coordinates = [entities_cooridnates[0][0],
                            entities_cooridnates[0][1],
                            entities_cooridnates[-1][6],
                            entities_cooridnates[0][1],
                            entities_cooridnates[0][0],
                            entities_cooridnates[-1][7],
                            entities_cooridnates[-1][6],
                            entities_cooridnates[-1][7]]
      final_coordinates = [float(i) for i in entity_coordinates]
    else:
      final_coordinates = None

    return final_coordinates
  else:
    if d.values[0]:
      return [float(i) for i in d.values[0]]
    else:
      return None


def standard_entity_mapping(desired_entities_list):
  """
    This function changes entity name to standard names and also
                create consolidated entities like name and date
    Parameters
    ----------
    desired_entities_list: List of default and derived entities

    Returns: Standard entities list
    -------
  """
  Logger.info(
      f"standard_entity_mapping called for desired_entities_list={desired_entities_list}")
  # Logger.info(f"desired_entities_list={desired_entities_list}")
  # convert extracted json to pandas dataframe
  df_json = pd.DataFrame.from_dict(desired_entities_list)
  # read entity standardization csv
  entity_standardization = os.path.join(
      os.path.dirname(__file__), ".", "entity-standardization.csv")
  entities_standardization_csv = pd.read_csv(entity_standardization)
  entities_standardization_csv.dropna(how="all", inplace=True)

  # Keep first record incase of duplicate entities
  entities_standardization_csv.drop_duplicates(subset=["entity"]
                                               , keep="first", inplace=True)
  entities_standardization_csv.reset_index(drop=True)

  # Create a dictionary from the look up dataframe/excel which has
  # the key col and the value col
  dict_lookup = dict(
      zip(entities_standardization_csv["entity"],
          entities_standardization_csv["standard_entity_name"]))
  # Get( all the entity (key column) from the json as a list
  key_list = list(df_json["entity"])
  # Replace the value by creating a list by looking up the value and assign
  # to json entity

  # Logger.info(f"df_json={df_json}, dict_lookup={dict_lookup}")
  for index, item in enumerate(key_list):
    # print(f"item={item}")
    if item in dict_lookup:
      # print(f"index={index}, item={dict_lookup[item]}")
      df_json["entity"][index] = dict_lookup[item]
    # TODO no dropping, keys are not normalized yet
    # else:
    #   df_json = df_json.drop(index)
    #   df_json.reset_index(inplace=True, drop=True)
  # convert datatype from object to int for column "extraction_confidence"
  df_json["extraction_confidence"] = pd.to_numeric \
    (df_json["extraction_confidence"], errors="coerce")
  group_by_columns = ["value", "extraction_confidence", "manual_extraction",
                      "corrected_value", "page_no",
                      "page_width", "page_height", "key_coordinates",
                      "value_coordinates"]
  df_conc = df_json.groupby("entity")[group_by_columns[0]].apply(
      lambda x: "/".join([v.strip() for v in x if v]) if check_int(x)
      else " ".join([v.strip() for v in x if v])).reset_index()

  df_av = df_json.groupby(["entity"])[group_by_columns[1]].mean(). \
    reset_index().round(2)
  # taking mode for categorical variables
  df_manual_extraction = df_json.groupby(["entity"])[group_by_columns[2]] \
    .agg(pd.Series.mode).reset_index()
  df_corrected_value = df_json.groupby(["entity"])[group_by_columns[3]] \
    .mean().reset_index().round(2)
  # if parser_name == "FormParser":
  df_page_no = df_json.groupby(["entity"])[group_by_columns[4]].mean() \
    .reset_index().round(2)
  df_page_width = df_json.groupby(["entity"])[group_by_columns[5]].mean() \
    .reset_index().round(2)
  df_page_height = df_json.groupby(["entity"])[group_by_columns[6]].mean() \
    .reset_index().round(2)
  # co-ordinate consolidation
  df_key_coordinates = df_json.groupby("entity")[group_by_columns[7]].apply(
      consolidate_coordinates).reset_index()
  df_value_coordinates = df_json.groupby("entity")[group_by_columns[8]].apply(
      consolidate_coordinates).reset_index()
  dfs = [df_conc, df_av, df_manual_extraction, df_corrected_value,
         df_page_no, df_page_width, df_page_height,
         df_key_coordinates, df_value_coordinates]
  # else:
  #   dfs = [df_conc, df_av, df_manual_extraction, df_corrected_value]

  df_final = reduce(lambda left, right: pd.merge(left, right, on="entity"), dfs)
  df_final = df_final.replace(r"^\s*$", np.nan, regex=True)
  df_final = df_final.replace({np.nan: None})
  extracted_entities_final_json = df_final.to_dict("records")
  Logger.info("Entities standardization completed")
  return extracted_entities_final_json


def form_parser_entities_mapping(form_parser_entity_list, mapping_dict,
    form_parser_text, json_folder):
  """
    Form parser entity mapping function

    Parameters
    ----------
    form_parser_entity_list: Extracted form parser entities before mapping
    mapping_dict: Mapping dictionary have info of default, derived entities
            along with desired keys

    Returns: required entities - list of dicts having entity, value, confidence
            and manual_extraction information
    -------
  """
  # extract entities information from config files
  default_entities = mapping_dict.get("default_entities")
  derived_entities = mapping_dict.get("derived_entities")
  table_entities = mapping_dict.get("table_entities")
  flag = check_duplicate_keys(default_entities, form_parser_entity_list)

  df = pd.DataFrame(form_parser_entity_list)
  print("....pandas.....")
  print(df)
  required_entities_list = []
  # loop through one by one default entities mentioned in the config file
  for each_ocr_key, each_ocr_val in default_entities.items():
    # print(f"each_ocr_key={each_ocr_key}, each_ocr_val={each_ocr_val}")
    try:
      # print(f'checking {df["key"]} == {each_ocr_key}')
      idx_list = df.index[df["key"] == each_ocr_key].tolist()
      # print(f"idx_list={idx_list}")
    except:  # pylint: disable=bare-except
      idx_list = []
      # print("idx_list is Empty")
    # loop for matched records of mapping dictionary
    for idx, each_val in enumerate(each_ocr_val):
      if idx_list:
        try:
          # creating response
          temp_dict = \
            {"entity": each_val, "value": df["value"][idx_list[idx]],
             "extraction_confidence": float(df["value_confidence"]
                                            [idx_list[idx]]),
             "manual_extraction": False,
             "corrected_value": None,
             "value_coordinates": [float(i) for i in
                                   df["value_coordinates"][idx_list[idx]]],
             "key_coordinates": [float(i) for i in
                                 df["key_coordinates"][idx_list[idx]]],
             "page_no": int(df["page_no"][idx_list[idx]]),
             "page_width": int(df["page_width"][idx_list[idx]]),
             "page_height": int(df["page_height"][idx_list[idx]])
             }

          print(f" ==> entity: {each_val}, value: {df['value'][idx_list[idx]]}")

        except:  # pylint: disable=bare-except
          Logger.info("Key not found in parser output,"
                      " so filling null value")

          temp_dict = {"entity": each_val, "value": None,
                       "extraction_confidence": None,
                       "manual_extraction": False,
                       "corrected_value": None,
                       "value_coordinates": None,
                       "key_coordinates": None,
                       "page_no": None,
                       "page_width": None,
                       "page_height": None
                       }

        required_entities_list.append(temp_dict)
      else:
        # filling null value if parser didn't extract
        temp_dict = {"entity": each_val, "value": None,
                     "extraction_confidence": None,
                     "manual_extraction": False,
                     "corrected_value": None,
                     "value_coordinates": None,
                     "key_coordinates": None,
                     "page_no": None,
                     "page_width": None,
                     "page_height": None
                     }
        required_entities_list.append(temp_dict)
  Logger.info("Default entities created from Form parser response")
  if derived_entities:
    # this function can be used for all docs, if derived entities
    # are extracted by using regex pattern
    parser_data = {}
    parser_data["text"] = form_parser_text
    derived_entities_op_dict = derived_entities_extraction(parser_data,
                                                           derived_entities)
    required_entities_list.extend(list(derived_entities_op_dict.values()))
    Logger.info("Derived entities created from Form parser response")

  if table_entities:
    table_response = None
    files = os.listdir(json_folder)
    for json_file in files:
      json_path = os.path.join(json_folder, json_file)
      table_extract_obj = TableExtractor(json_path)
      table_response = table_extract_obj.get_entities(table_entities)
      if table_response and isinstance(table_response, list):
        required_entities_list.extend(table_response)
        break
    if table_response is None:
      Logger.error("No table data found")

  # print("Extracted list required_entities_list")
  # print(required_entities_list)
  return required_entities_list, flag


def download_pdf_gcs(bucket_name=None, gcs_uri=None, file_to_download=None,
    output_filename=None) -> str:
  """
    Function takes a path of an object/file stored in GCS bucket and
            downloads the file in the current working directory

    Args:
        bucket_name (str): bucket name from where file to be downloaded
        gcs_uri (str): GCS object/file path
        output_filename (str): desired filename
        file_to_download (str): gcs file path excluding bucket name.
            Ex: if file is stored in X bucket under the folder Y with
            filename ABC.txt
            then file_to_download = Y/ABC.txt
    Return:
        pdf_path (str): pdf file path that is downloaded from the
                bucket and stored in local
  """
  if bucket_name is None:
    bucket_name = gcs_uri.split("/")[2]
  # if file to download is not provided it can be extracted from the GCS URI
  if file_to_download is None and gcs_uri is not None:
    file_to_download = "/".join(gcs_uri.split("/")[3:])
  storage_client = storage.Client()
  bucket = storage_client.get_bucket(bucket_name)
  blob = bucket.blob(file_to_download)
  # save file, if output path provided
  if output_filename:
    with open(output_filename, "wb") as file_obj:
      blob.download_to_file(file_obj)
  return blob


def clean_form_parser_keys(text):
  """
    Cleaning form parser keys
    Parameters
    ----------
    text: original text before noise removal - removed spaces, newlines
    Returns: text after noise removal
    -------
  """
  # removing special characters from beginning and end of a string
  try:
    if len(text):
      text = text.strip()
      text = text.replace("\n", " ")
      text = re.sub(r"^\W+", "", text)
      last_word = text[-1]
      text = re.sub(r"\W+$", "", text)
    if last_word in [")", "]"]:
      text += last_word

  except:  # pylint: disable=bare-except
    Logger.error("Exception occurred while cleaning keys")

  return text


def del_gcs_folder(bucket, folder):
  """
  This function is to delete folder from gcs bucket, this is used to
   delete temp folder from bucket
  Parameters
  ----------
  bucket: Bucket name
  folder: Folder name inside bucket
  Returns : None
  -------
  """

  storage_client = storage.Client()
  bucket = storage_client.get_bucket(bucket)
  blobs = bucket.list_blobs(prefix=folder)
  for blob in blobs:
    blob.delete()

  # print("Delete successful")


def strip_value(value):
  '''Function for default cleaning of values to remove space at end and begining
  and '\n' at end
  Input:
       value: Input string
  Output:
       corrected_value: corrected string without noise'''
  if value is None:
    corrected_value = value
  else:
    corrected_value = value.strip()
    corrected_value = corrected_value.replace("\n", " ")
  return corrected_value


def extract_form_fields(doc_element: dict, document: dict):
  """
   # Extract form fields from form parser raw json
    Parameters
    ----------
    doc_element: Entitiy
    document: Extracted OCR Text

    Returns: Entity name and Confidence
    -------
  """

  response = ""
  list_of_coordidnates = []
  # If a text segment spans several lines, it will
  # be stored in different text segments.
  for segment in doc_element.text_anchor.text_segments:
    start_index = (
        int(segment.start_index)
        if segment in doc_element.text_anchor.text_segments
        else 0
    )
    end_index = int(segment.end_index)
    response += document.text[start_index:end_index]
  confidence = doc_element.confidence
  coordinate = list([doc_element.bounding_poly.normalized_vertices])
  # print("coordinate", coordinate)
  # print("type", type(coordinate))

  for item in coordinate:
    # print("item", item)
    # print("type", type(item))
    for xy_coordinate in item:
      # print("xy_coordinate", xy_coordinate)
      # print("x", xy_coordinate.x)
      list_of_coordidnates.append(float(round(xy_coordinate.x, 4)))
      list_of_coordidnates.append(float(round(xy_coordinate.y, 4)))
  return response, confidence, list_of_coordidnates


def extraction_accuracy_calc(total_entities_list, flag=True):
  """
    This function is to calculate document extraction accuracy
    Parameters
    ----------
    total_entities_list: Total extracted list of dict
    Returns : Extraction score
    -------
  """
  # get fields extraction accuracy
  extraction_status = "single entities present"
  if flag is False:
    extraction_accuracy = 0.0
    extraction_field_min_score = 0
    extraction_status = "duplicate entities present"
    return extraction_accuracy, extraction_status, extraction_field_min_score
  entity_accuracy_list = [each_entity.get("extraction_confidence") if
                          each_entity.get("extraction_confidence") else 0
                          for each_entity in
                          total_entities_list if not each_entity.
                          get("manual_extraction")]

  extraction_field_min_score = min(entity_accuracy_list)
  extraction_accuracy = round(sum(entity_accuracy_list) /
                              len(entity_accuracy_list), 3)

  return extraction_accuracy, extraction_status, extraction_field_min_score
