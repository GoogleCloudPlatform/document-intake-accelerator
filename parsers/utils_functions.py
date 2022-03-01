import os
import re
import json
from google.cloud import storage


# pattern need to read from config file - WIP

def pattern_based_entities(parser_data):

    text = parser_data["text"]

    pattern = re.compile(r"SEX.*?(?<!\w)(F|M)(?!\w)", flags=re.DOTALL)

    matched_text = re.search(pattern, text)

    if matched_text:
        # print(matched_text)
        sex = matched_text.group(1)
    else:
        sex = "T"
    return sex


def default_entities_extraction(entity_dict, parser_entities, default_entities):

    for each_entity in parser_entities:
        key, val, confidence = each_entity.get("type", ""), each_entity.get("mentionText", ""), round(each_entity.get("confidence", 0), 2)
        if key in default_entities:
            entity_dict[key] = {"text": val, "confidence": confidence}

    return entity_dict

# Generic function to create name from given name and first name
def name_entity_creation(entity_dict):

    name_text = (entity_dict["Given Names"]["text"] + " " + entity_dict["Family Name"]["text"]).strip()
    name_confidence = round((entity_dict["Given Names"]["confidence"] + entity_dict["Family Name"]["confidence"]) / 2,
                            2)
    name_dict = {"text": name_text, "confience": name_confidence}

    return name_dict


def dl_derived_entities_extraction(entity_dict, parser_data, derived_entities):

    name_dict = name_entity_creation(entity_dict)

    entity_dict["Name"] = name_dict

    sex = pattern_based_entities(parser_data)

    entity_dict["Sex"] = {"text": sex, "confidence": 1}

    return entity_dict

def entities_extraction(parser_data, required_entities, doc_type):

    # Read the entities from the processor

    parser_entities = parser_data["entities"]

    default_entities = required_entities["default_entities"]
    derived_entities = required_entities.get("derived_entities")

    temp_dict = {"text": "", "confidence": 0}

    entity_dict = {each_entity: temp_dict for each_entity in default_entities}

    default_entities_extraction(entity_dict, parser_entities, default_entities)

    # only for DL, make it add for new parsers
    if derived_entities:
        for k in derived_entities.keys():
            entity_dict.update({k: temp_dict})

        if doc_type == "driver_license":
            dl_derived_entities_extraction(entity_dict, parser_data, derived_entities)

    return entity_dict


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