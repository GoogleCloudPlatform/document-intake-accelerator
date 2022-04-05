"""
This script has all the common and re-usable functions required for extraction framework

"""

import os
import re
import json
import pandas as pd
import numpy as np
from functools import reduce
from google.cloud import storage


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

    pattern = re.compile(r"{}".format(pattern), flags=re.DOTALL)

    # match as per pattern
    matched_text = re.search(pattern, text)

    if matched_text:
        op = matched_text.group(1)
    else:
        op = None
    return op


def default_entities_extraction(parser_entities, default_entities):
    """
    This function extracted default entities

    Parameters
    ----------
    parser_entities: Specialized parser entities
    default_entities: Default entites that need to extract from parser entities

    Returns : Default entites dict
    -------

    """

    parser_entities_dict = {}

    # retrieve parser given entities
    for each_entity in parser_entities:
        key, val, confidence = each_entity.get("type", ""), each_entity.get("mentionText", ""), round(
            each_entity.get("confidence", 0), 2)

        parser_entities_dict[key] = [val, confidence]

    entity_dict = {}

    # create default entities
    for key in default_entities.keys():
        if key in parser_entities_dict.keys():
            entity_dict[default_entities[key][0]] = {"entity": default_entities[key][0],
                                                     "value": parser_entities_dict[key][0],
                                                     "extraction_confidence": parser_entities_dict[key][1],
                                                     "manual_extraction": False,
                                                     "corrected_value": None}
        else:
            entity_dict[default_entities[key][0]] = {"entity": default_entities[key][0], "value": None,
                                                     "extraction_confidence": None,
                                                     "manual_extraction": False,
                                                     "corrected_value": None}

    return entity_dict


def name_entity_creation(entity_dict, name_list):
    """
    This function is to create name from Fname and Gname. Can be re-used if it helps
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

    name_dict = {"entity": "Name", "value": name,
                 "extraction_confidence": confidence,
                 "manual_extraction": False,
                 "corrected_value": None}

    return name_dict


def derived_entities_extraction(parser_data, derived_entities):
    """

    This function extract/create derived entities based on config derived entity section

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

        derived_entities_extracted_dict[key] = {"entity": key, "value": pattern_op,
                                                "extraction_confidence": None,
                                                "manual_extraction": True,
                                                "corrected_value": None}

    return derived_entities_extracted_dict


def entities_extraction(parser_data, required_entities, doc_type):
    """
    This function reads information of default and derived entities

    Parameters
    ----------
    parser_data: specialzed parser result
    required_entities: required extracted entities
    doc_type: Document type

    Returns: Required entities dict
    -------

    """

    # Read the entities from the processor

    parser_entities = parser_data["entities"]
    default_entities = required_entities["default_entities"]
    derived_entities = required_entities.get("derived_entities")

    # Extract default entities
    entity_dict = default_entities_extraction(parser_entities, default_entities)

    # if any derived entities then extract them
    if derived_entities:
        # this function can be used for all docs, if derived entities are extracted by using regex pattern
        derived_entities_extracted_dict = derived_entities_extraction(parser_data, derived_entities)
        entity_dict.update(derived_entities_extracted_dict)

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

    for i in d:
        if i and i.isdigit():
            count = count + 1
    if count >= 2:
        return True
    else:
        return False

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

    # convert extracted json to pandas dataframe
    df_json = pd.DataFrame.from_dict(desired_entities_list)

    # read entity standardization csv
    entity_standardization = os.path.join(
        os.path.dirname(__file__), ".", "entity-standardization.csv")
    entities_standardization_csv = pd.read_csv(entity_standardization)
    entities_standardization_csv.dropna(how='all', inplace=True)

    # Keep first record incase of duplicate entities

    entities_standardization_csv.drop_duplicates(subset=['entity'], keep="first", inplace=True)

    entities_standardization_csv.reset_index(drop=True)

    # # filter records based on doc and state
    # entities_standardization_csv = entities_standardization_csv[entities_standardization_csv["document_type"]==doc_state]

    # Create a dictionary from the look up dataframe/excel which has the key col and the value col
    dict_lookup = dict(
        zip(entities_standardization_csv['entity'], entities_standardization_csv['standard_entity_name']))
    # Get( all the entity (key column) from the json as a list
    key_list = list(df_json['entity'])
    # Replace the value by creating a list by looking up the value and assign to json entity
    df_json['entity'] = [dict_lookup[item] for item in key_list]
    # convert datatype from object to int for column 'extraction_confidence'
    df_json['extraction_confidence'] = pd.to_numeric(df_json['extraction_confidence'], errors='coerce')

    group_by_columns = ['value', 'extraction_confidence', 'manual_extraction', 'corrected_value']
    df_conc = df_json.groupby('entity')[group_by_columns[0]].apply(
        lambda x: '/'.join([v for v in x if v]) if check_int(x) else ' '.join(v for v in x if v)).reset_index()


    df_av = df_json.groupby(['entity'])[group_by_columns[1]].mean().reset_index().round(2)

    # taking mode for categorical variables
    df_manual_extraction = df_json.groupby(['entity'])[group_by_columns[2]].agg(pd.Series.mode).reset_index()
    print("======================================")
    print(df_json)
    df_corrected_value = df_json.groupby(['entity'])[group_by_columns[3]].mean().reset_index().round(2)

    dfs = [df_conc, df_av, df_manual_extraction, df_corrected_value]

    df_final = reduce(lambda left, right: pd.merge(left, right, on='entity'), dfs)

    df_final = df_final.replace(r'^\s*$', np.nan, regex=True)

    df_final = df_final.replace({np.nan: None})

    extracted_entities_final_json = df_final.to_dict("records")

    return extracted_entities_final_json


def form_parser_entities_mapping(form_parser_entity_list, mapping_dict, form_parser_text):
    """
    Form parser entity mapping function

    Parameters
    ----------
    form_parser_entity_list: Extracted form parser entities before mapping
    mapping_dict: Mapping dictionary have info of default, derived entities along with desired keys

    Returns: required entities - list of dicts having entity, value, confidence and manual_extraction information
    -------

    """

    # extract entities information from config files
    default_entities = mapping_dict.get("default_entities")

    derived_entities = mapping_dict.get("derived_entities")

    df = pd.DataFrame(form_parser_entity_list)

    required_entities_list = []

    # loop through one by one deafult entities mentioned in the config file
    for each_ocr_key, each_ocr_val in default_entities.items():

        idx_list = df.index[df['key'] == each_ocr_key].tolist()

        # loop for matched records of mapping dictionary
        for idx, each_val in enumerate(each_ocr_val):

            if idx_list:
                try:
                    # creating response
                    temp_dict = {"entity": each_val, "value": df['value'][idx_list[idx]],
                                 "extraction_confidence": df['value_confidence'][idx_list[idx]],
                                 "manual_extraction": False,
                                 "corrected_value": None}
                except Exception as e:
                    print('Key not found in parser output')
                    temp_dict = {"entity": each_val, "value": None,
                                 "extraction_confidence": None,
                                 "manual_extraction": False,
                                 "corrected_value": None}

                required_entities_list.append(temp_dict)
            else:
                # filling null value if parser didn't extract

                temp_dict = {"entity": each_val, "value": None,
                             "extraction_confidence": None,
                             "manual_extraction": False,
                             "corrected_value": None}
                required_entities_list.append(temp_dict)

    if derived_entities:
        # this function can be used for all docs, if derived entities are extracted by using regex pattern
        parser_data = {}
        parser_data["text"] = form_parser_text
        derived_entities_op_dict = derived_entities_extraction(parser_data, derived_entities)
        required_entities_list.extend(list(derived_entities_op_dict.values()))

    return required_entities_list


def download_pdf_gcs(bucket_name=None, gcs_uri=None, file_to_download=None, output_filename=None) -> str:
    """
    Function takes a path of an object/file stored in GCS bucket and downloads
    the file in the current working directory

    Args:
        bucket_name (str): bucket name from where file to be downloaded
        gcs_uri (str): GCS object/file path
        output_filename (str): desired filename
        file_to_download (str): gcs file path excluding bucket name.
            Ex: if file is stored in X bucket under the folder Y with filename ABC.txt
            then file_to_download = Y/ABC.txt
    Return:
        pdf_path (str): pdf file path that is downloaded from the bucket and stored in local
    """

    if bucket_name is None:
        bucket_name = gcs_uri.split('/')[2]

    # if file to download is not provided it can be extracted from the GCS URI
    if file_to_download is None and gcs_uri is not None:
        file_to_download = '/'.join(gcs_uri.split('/')[3:])

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
            text = text.replace("\n", ' ')
            text = re.sub(r"^\W+", "", text)
            last_word = text[-1]
            text = re.sub(r"\W+$", "", text)
        if last_word in [")", "]"]:
            text += last_word
    except:
        pass
    return text


def del_gcs_folder(bucket, folder):
    """
    This function is to delete folder from gcs bucket, this is used to delete temp folder from bucket

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

    print("Delete successful")


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
    return response, confidence


def extraction_accuracy_calc(total_entities_list):
    """

    This function is to calculate document extraction accuracy
    Parameters
    ----------
    total_entities_list: Total extracted list of dict

    Returns : Extraction score
    -------

    """

    # get fields extraction accuracy
    entity_accuracy_list = [each_entity.get("extraction_confidence") if each_entity.get("extraction_confidence") else 0
                            for each_entity in
                            total_entities_list if not each_entity.get("manual_extraction")]

    extraction_accuracy = round(sum(entity_accuracy_list) / len(entity_accuracy_list), 3)

    return extraction_accuracy


if __name__ == "__main__":

    # these variables are used to run in local environment

    parser_json = "utility-docs/parser-json/without-noisy"
    extracted_entities = "utility-docs/extracted-entities/without-noisy"

    required_entities = {
        "default_entities": ["Family Name", "Given Names", "Document Id", "Expiration Date", "Date Of Birth",
                             "Issue Date",
                             "Address"],
        "derived_entities": {"Name": {"rule": ["Given Names", "Family Name"]}, "Sex": {"rule": "pattern"}}
    }

    required_entities = {
        "default_entities": ["invoice_id", "invoice_date", "due_date", "receiver_name", "service_address",
                             "total_tax_amount",
                             "supplier_account_number"]
    }

    json_files = os.listdir(parser_json)

    for each_json in json_files:
        with open(os.path.join(parser_json, each_json), 'r') as j:
            data = json.loads(j.read())
            print(each_json)

            entity_dict = entities_extraction(data, required_entities)

            # save extracted entities json
            with open("{}.json".format(os.path.join(extracted_entities, each_json.split('.')[0])), "w") as outfile:
                json.dump(entity_dict, outfile, indent=4)

    download_pdf_gcs(
        gcs_uri='gs://async_form_parser/input/arizona-driver-form-13.pdf'
    )

    total_entities_list = [
        {
            "entity": "Social Security Number",
            "value": None,
            "extraction_confidence": 1,
            "manual_extraction": False,
            "corrected_value": None
        },
        {
            "entity": "Date",
            "value": None,
            "extraction_confidence": None,
            "manual_extraction": False,
            "corrected_value": None
        }
    ]

    extraction_accuracy_calc(total_entities_list)
