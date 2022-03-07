import json
import os
import re
import proto
import random
from google.cloud import documentai_v1 as documentai
from google.cloud import storage
from utils_functions import entities_extraction, download_pdf_gcs, extract_form_fields, del_gcs_folder, form_parser_entities_mapping
from config import *

def specialized_parser_extraction(parser_details: dict, gcs_doc_path: str, doc_type: str):
    """
    Parameters
    ----------
    parser_details: it has parser info like id, name, loc, and etc
    gcs_doc_path:
    doc_type: doc label

    Returns: Extracted json response coming from Parsers
    -------
    """

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processor/processor-id

    location = parser_details["location"]

    processor_id = parser_details["processor_id"]

    parser_name = parser_details["parser_name"]

    # required_entities = parser_details["required_entities"]

    required_entities = MAPPING_DICT[doc_type]

    project_id = PROJECT_NAME

    opts = {}

    if location == "eu":
        opts = {"api_endpoint": "eu-documentai.googleapis.com"}


    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

    blob = download_pdf_gcs(
        gcs_uri=gcs_doc_path
    )

    document = {"content": blob.download_as_bytes(), "mime_type": "application/pdf"}
    """
    # Read the file into memory
    with open(doc_path, "rb") as image:
        image_content = image.read()

    document = {"content": image_content, "mime_type": "application/pdf"}
    """

    # Configure the process request
    request = {"name": name, "raw_document": document}

    result = client.process_document(request=request)

    parser_doc_data = result.document

    # convert to json
    json_string = proto.Message.to_json(parser_doc_data)
    data = json.loads(json_string)

    for each_attr in NOT_REQUIRED_ATTRIBUTES_FROM_SPECIALIZED_PARSER_RESPONSE:
        if "." in each_attr:
            parent_attr, child_attr = each_attr.split(".")

            for idx in range(len(data.get(parent_attr, 0))):
                data[parent_attr][idx].pop(child_attr, None)
        else:
            data.pop(each_attr, None)

    # this can be removed while integration
    # save parser op output
    with open("{}.json".format(os.path.join(parser_op, gcs_doc_path.split('/')[-1])), "w") as outfile:
        json.dump(data, outfile)

    # extract dl entities
    extracted_entity_dict = entities_extraction(data, required_entities, doc_type)

    # Create a list of entities dicts

    specialized_parser_entity_list = [v for k, v in extracted_entity_dict.items()]

    # this can be removed while integration
    # save extracted entities json
    with open("{}.json".format(os.path.join(extracted_entities, gcs_doc_path.split('/')[-1])), "w") as outfile:
        json.dump(specialized_parser_entity_list, outfile, indent=4)

    print("process completed")

    return specialized_parser_entity_list

    # exit()

def form_parser_extraction(parser_details: dict, gcs_doc_path: str, doc_type: str, state: str, timeout: int):


    location = parser_details["location"]
    processor_id = parser_details["processor_id"]
    parser_name = parser_details["parser_name"]

    # These variables will be removed later
    project_id = PROJECT_NAME  # later read this variable from project config files

    opts = {}

    # Location can be 'us' or 'eu'
    if location == "eu":
        opts = {"api_endpoint": "eu-documentai.googleapis.com"}

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # create a temp folder to store parser op, delete folder once processing done
    # call create gcs bucket function to create bucket, folder will be created automatically
    gcs_output_uri = GCS_OP_URI
    gcs_output_uri_prefix = FORM_PARSER_OP_TEMP_FOLDER


    destination_uri = f"{gcs_output_uri}/{gcs_output_uri_prefix}/"
    # print(destination_uri)

    gcs_documents = documentai.GcsDocuments(
        documents=[{"gcs_uri": gcs_doc_path, "mime_type": "application/pdf"}]
    )

    # 'mime_type' can be 'application/pdf', 'image/tiff',
    # and 'image/gif', or 'application/json'
    input_config = documentai.BatchDocumentsInputConfig(gcs_documents=gcs_documents)

    # Where to write results
    output_config = documentai.DocumentOutputConfig(
        gcs_output_config={"gcs_uri": destination_uri}
    )

    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

    # request for Doc AI
    request = documentai.types.document_processor_service.BatchProcessRequest(
        name=name, input_documents=input_config, document_output_config=output_config,
    )

    operation = client.batch_process_documents(request)

    # Wait for the operation to finish
    operation.result(timeout=timeout)

    # Results are written to GCS. Use a regex to find
    # output files
    match = re.match(r"gs://([^/]+)/(.+)", destination_uri)
    output_bucket = match.group(1)
    prefix = match.group(2)

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(output_bucket)
    blob_list = list(bucket.list_blobs(prefix=prefix))

    extracted_entity_list = []

    mapping_dict = MAPPING_DICT[state]

    # saving form parser json
    parser_json_folder = "/home/venkatakrishna/Documents/Q/projects/doc-ai-test/application-arizona/async-parser-json/without-noisy"
    parser_json_folder = os.path.join(parser_json_folder, gcs_doc_path.split("/")[-1][:-4])
    if not os.path.exists(parser_json_folder):
        os.mkdir(parser_json_folder)

    # browse through output jsons
    for i, blob in enumerate(blob_list):
        # If JSON file, download the contents of this blob as a bytes object.
        if ".json" in blob.name:

            print('json file name', blob.name)

            blob_as_bytes = blob.download_as_bytes()

            # saving the parser response to the folder, remove while integration
            parser_json_fname = os.path.join(parser_json_folder, 'res_{}.json'.format(i))
            with open(parser_json_fname, "wb") as file_obj:
                blob.download_to_file(file_obj)

            document = documentai.types.Document.from_json(blob_as_bytes)
            print(f"Fetched file {i + 1}")

            # For a full list of Document object attributes, please reference this page:
            # https://cloud.google.com/document-ai/docs/reference/rpc/google.cloud.documentai.v1beta3#document

            # Read the text recognition output from the processor
            for page in document.pages:
                for form_field in page.form_fields:

                    field_name, field_name_confidence = extract_form_fields(form_field.field_name, document)
                    field_value, field_value_confidence = extract_form_fields(form_field.field_value, document)

                    temp_dict = {"key": field_name, "value": field_value,
                                 "key_confidence": round(field_name_confidence, 2),
                                 "value_confidence": round(field_value_confidence, 2)}

                    extracted_entity_list.append(temp_dict)

            print("Extraction completed")

            # Form parser mapping ocr --> desired names cleaning
            form_parser_entities_list = form_parser_entities_mapping(extracted_entity_list, mapping_dict)
            # stadardization of keys script should call here

        else:
            print(f"Skipping non-supported file type {blob.name}")

    # delete temp folder
    del_gcs_folder(gcs_output_uri.split("//")[1], gcs_output_uri_prefix)

    # save extracted entities json

    with open(
            "/home/venkatakrishna/Documents/Q/projects/doc-ai-test/application-arizona/async-parser-json/{}.json".format(
                    "Arizona2-latest"), "w") as outfile:
        json.dump(extracted_entity_list, outfile, indent=4)

    # Extract desired entities only

    with open(
            "/home/venkatakrishna/Documents/Q/projects/doc-ai-test/application-arizona/extracted-entities/without-noisy/{}.json".format(
                    "Arizona2-latest-desired"), "w") as outfile:
        json.dump(form_parser_entities_list, outfile, indent=4)

    return form_parser_entities_list

def extract_entities(gcs_doc_path, doc_type, state):

    parser_config_json = "parser_config.json"

    with open(parser_config_json, 'r') as j:

        parsers_info = json.loads(j.read())
        # for each_doc in inp_docs:
        parser_information = parsers_info.get(doc_type)

        if parser_information:
            parser_name = parser_information["parser_name"]
            # print('parser available')
            if parser_name == "FormParser":
                desired_entities_list = form_parser_extraction(parser_information, gcs_doc_path, doc_type, state, 300)
            else:
                desired_entities_list = specialized_parser_extraction(parser_information, gcs_doc_path, doc_type)
        else:
            # Parser not available
            print('parser not available for this document')

        # exit()

    return desired_entities_list

if __name__ == "__main__":


    parser_op = "/home/venkatakrishna/Documents/Q/projects/doc-ai-test/application-arizona/async-parser-json"

    extracted_entities = "/home/venkatakrishna/Documents/Q/projects/doc-ai-test/application-arizona/extracted-entities/without-noisy"

    gcs_doc_path = "gs://async_form_parser/input/arizona-driver-form-13.pdf"

    os.environ[
        'GOOGLE_APPLICATION_CREDENTIALS'] = "/home/venkatakrishna/Documents/Q/projects/doc-ai-test/claims-processing-dev-sa.json"

    # API Integration will start from here

    # Extract API Provides label and document
    doc_type = "unemployment_form"
    state = "arizona"
    gcs_doc_path = "gs://async_form_parser/input/Arizona2-latest.pdf"
    # gcs_doc_path = "gs://async_form_parser/input/arizona-driver-form-13.pdf"

    extract_entities(gcs_doc_path, doc_type, state)

    # use this code for looping in gcs folder

    """
    gcs_output_uri = "gs://async_form_parser"
    gcs_output_uri_prefix = "input"

    destination_uri = f"{gcs_output_uri}/{gcs_output_uri_prefix}/"

    match = re.match(r"gs://([^/]+)/(.+)", destination_uri)
    output_bucket = match.group(1)
    prefix = match.group(2)

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(output_bucket)
    blob_list = list(bucket.list_blobs(prefix=prefix))

    for i, blob in enumerate(blob_list):
        if ".pdf" in blob.name:
            gcs_doc_path = gcs_output_uri + '/' + blob.name
            extract_entities(gcs_doc_path, doc_type, state)
    """