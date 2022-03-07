import os
import re
import json
import pandas as pd
from google.cloud import storage



def pattern_based_entities(parser_data, pattern):

    text = parser_data["text"]

    print("pattern", r"{}".format(pattern))
    pattern = re.compile(r"{}".format(pattern), flags=re.DOTALL)

    matched_text = re.search(pattern, text)

    if matched_text:
        # print(matched_text)
        op = matched_text.group(1)
    else:
        op = None
    return op


def default_entities_extraction(parser_entities, default_entities):


    parser_entities_dict = {}
    for each_entity in parser_entities:

        key, val, confidence = each_entity.get("type", ""), each_entity.get("mentionText", ""), round(each_entity.get("confidence", 0), 2)

        parser_entities_dict[key] = [val,confidence]
        """
        if key in default_entities.keys():
            entity_dict[key] = {"entity": key, "value": val,
                                 "confidence": confidence,
                                 "manual_extraction": False}
        """
    entity_dict = {}
    for key in default_entities.keys():
        if key in parser_entities_dict.keys():
            entity_dict[default_entities[key][0]] = {"entity": default_entities[key][0], "value": parser_entities_dict[key][0],
                                 "confidence": parser_entities_dict[key][1],
                                 "manual_extraction": False}
        else:
            entity_dict[default_entities[key][0]] = {"entity": default_entities[key][0], "value": None,
                                "confidence": None,
                                "manual_extraction": False}

    return entity_dict

# Generic function to create name from given name and first name
def name_entity_creation(entity_dict, name_list):

    name = ""
    confidence = 0
    for each_name in name_list:
        parser_extracted_name = entity_dict[each_name]["value"]
        if parser_extracted_name:
            name += parser_extracted_name
            confidence += entity_dict[each_name]["confidence"]

    if name.strip():
        name = name.strip()
        confidence = round(confidence/len(name_list), 2)
    else:
        name = None
        confidence = None

    name_dict = {"entity": "Name", "value": name,
                     "confidence": confidence,
                     "manual_extraction": False}

    """
    name_text = (entity_dict["Given Names"]["value"] + " " + entity_dict["Family Name"]["value"]).strip()
    name_confidence = round((entity_dict["Given Names"]["confidence"] + entity_dict["Family Name"]["confidence"]) / 2,
                            2)
    name_dict = {"text": name_text, "confience": name_confidence}
    name_dict = {"entity": each_entity, "value": name_text,
                 "confidence": None,
                 "manual_extraction": False}
    """

    return name_dict



# dl specific derived function
def dl_derived_entities_extraction(entity_dict, parser_data, derived_entities):

    """
    name_list = derived_entities["Name"]["rule"]

    name_dict = name_entity_creation(entity_dict, name_list)

    entity_dict["Name"] = name_dict

    sex = pattern_based_entities(parser_data, DL_SEX_PATTERN)

    entity_dict["Sex"] = {"entity": "Sex", "value": sex,
                     "confidence": None,
                     "manual_extraction": True}
    """

    for key, val in derived_entities.items():
        pattern = val["rule"]
        pattern_op = pattern_based_entities(parser_data, pattern)

        entity_dict[key] = {"entity": key, "value": pattern_op,
                              "confidence": None,
                              "manual_extraction": True}

    return entity_dict

def entities_extraction(parser_data, required_entities, doc_type):

    # Read the entities from the processor

    parser_entities = parser_data["entities"]
    default_entities = required_entities["default_entities"]
    derived_entities = required_entities.get("derived_entities")

    """
    temp_dict = {"text": "", "confidence": 0}
    entity_dict = {each_entity: temp_dict for each_entity in default_entities}
    default_entities_extraction(entity_dict, parser_entities, default_entities)
    """

    """
    # create response structure for required entities
    entity_dict = {}

    for each_entity in default_entities.keys():
        temp_dict = {"entity": each_entity, "value": None,
                     "confidence": None,
                     "manual_extraction": False}

        entity_dict.update({each_entity: temp_dict})
    """

    entity_dict = default_entities_extraction(parser_entities, default_entities)

    if derived_entities:
        """
        for k in derived_entities.keys():
            temp_dict = {"entity": k, "value": None,
                         "confidence": None,
                         "manual_extraction": False}
            entity_dict.update({k: temp_dict})
        """

        # this function can be used for all docs, if derived entities are extracted by using regex pattern
        dl_derived_entities_extraction(entity_dict, parser_data, derived_entities)

    return entity_dict


def form_parser_entities_mapping(form_parser_entity_list, mapping_dict):
    # A --> B

    default_entities = mapping_dict["default_entities"]

    df = pd.DataFrame(form_parser_entity_list)

    required_entities_list = []

    for each_ocr_key, each_ocr_val in default_entities.items():

        idx_list = df.index[df['key'] == each_ocr_key].tolist()

        """
        if idx_list:
            for idx, each_val in enumerate(each_ocr_val):
                try:
                    temp_dict = {"entity": each_val, "value": df['value'][idx_list[idx]],
                                 "confidence": df['value_confidence'][idx_list[idx]],
                                 "manual_extraction": False}
                    required_entities_list.append(temp_dict)
                except Exception as e:
                    print('Key not found in parser output')
        else:
            # filling null value if parser didn't extract
            for each_val in each_ocr_val:
                temp_dict = {"entity": each_val, "value": None,
                             "confidence": None,
                             "manual_extraction": False}
                required_entities_list.append(temp_dict)
        """


        for idx, each_val in enumerate(each_ocr_val):

            if idx_list:
                try:
                    temp_dict = {"entity": each_val, "value": df['value'][idx_list[idx]],
                                 "confidence": df['value_confidence'][idx_list[idx]],
                                 "manual_extraction": False}
                except Exception as e:
                    print('Key not found in parser output')
                    temp_dict = {"entity": each_val, "value": None,
                                 "confidence": None,
                                 "manual_extraction": False}

                required_entities_list.append(temp_dict)
            else:
                # filling null value if parser didn't extract

                temp_dict = {"entity": each_val, "value": None,
                             "confidence": None,
                             "manual_extraction": False}
                required_entities_list.append(temp_dict)


    return required_entities_list



def download_pdf_gcs(bucket_name=None, gcs_uri=None, file_to_download=None, output_filename=None) -> str:
    """Function takes a path of an object/file stored in GCS bucket and downloads
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

    if output_filename:
        with open(output_filename, "wb") as file_obj:
            blob.download_to_file(file_obj)

    return blob

# to get gcs folder
def del_gcs_folder(bucket, folder):

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket)
    blobs = bucket.list_blobs(prefix=folder)
    for blob in blobs:
        blob.delete()

    print("Delete successful")


# Extract shards from the text field
def extract_form_fields(doc_element: dict, document: dict):
    """
    Document AI identifies form fields by their offsets
    in document text. This function converts offsets
    to text snippets.
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


if __name__=="__main__":
    parser_json = "utility-docs/parser-json/without-noisy"
    extracted_entities = "utility-docs/extracted-entities/without-noisy"

    required_entities =  {
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