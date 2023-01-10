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

# pylint: disable=broad-except
"""
This is the main file for extraction framework, based on \
    doc type specialized parser or
form parser functions will be called
"""

import json
import os
import re
import shutil
import proto
import random
import string
from google.cloud import documentai_v1 as documentai
from .change_json_format import get_json_format_for_processing, \
    correct_json_format_for_db
from .correct_key_value import data_transformation
from .utils_functions import entities_extraction, download_pdf_gcs,\
    extract_form_fields, del_gcs_folder, \
    form_parser_entities_mapping, extraction_accuracy_calc, \
    clean_form_parser_keys, standard_entity_mapping, strip_value
from common.config import PROJECT_ID, get_docai_entity_mapping
from common.extraction_config import DOCAI_OUTPUT_BUCKET_NAME, \
    DOCAI_ATTRIBUTES_TO_IGNORE
from common.config import get_parser_config, get_docai_entity_mapping
from common.utils.logging_handler import Logger
import warnings
from google.cloud import storage

warnings.simplefilter(action="ignore")


def specialized_parser_extraction(parser_details: dict, gcs_doc_path: str,
                                  doc_type: str, context: str):
  """
    This is specialized parser extraction main function.
    It will send request to parser and retrieve response and call
        default and derived entities functions

    Parameters
    ----------
    parser_details: It has parser info like parser id, name, location, and etc
    gcs_doc_path: Document gcs path
    doc_type: Document type

    Returns: Specialized parser response - list of dicts having entity,
     value, confidence and manual_extraction information.
    -------
  """

  # The full resource name of the processor, e.g.:
  # projects/project-id/locations/location/processor/processor-id

  location = parser_details["location"]
  processor_id = parser_details["processor_id"]
  #parser_name = parser_details["parser_name"]
  project_id = PROJECT_ID
  opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}

  client = documentai.DocumentProcessorServiceClient(client_options=opts)
  # parser api end point
  # name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
  name = processor_id
  blob = download_pdf_gcs(gcs_uri=gcs_doc_path)

  document = {
      "content": blob.download_as_bytes(),
      "mime_type": "application/pdf"
  }
  # Configure the process request
  request = {"name": name, "raw_document": document}
  Logger.info(f"Specialized parser extraction api called for processor {processor_id}")
  # send request to parser
  result = client.process_document(request=request)
  parser_doc_data = result.document
  # convert to json
  json_string = proto.Message.to_json(parser_doc_data)
  print("Extracted data:")
  print(json.dumps(json_string))
  data = json.loads(json_string)
  # remove unnecessary entities from parser
  for each_attr in DOCAI_ATTRIBUTES_TO_IGNORE:
    if "." in each_attr:
      parent_attr, child_attr = each_attr.split(".")
      for idx in range(len(data.get(parent_attr, 0))):
        data[parent_attr][idx].pop(child_attr, None)
    else:
      data.pop(each_attr, None)

  # Get corresponding mapping dict, for specific context or fallback to "all" TODO duplicate code with other parser
  docai_entity_mapping = get_docai_entity_mapping()

  print(f"context={context}")
  docai_entity_mapping_by_context = docai_entity_mapping.get(context)
  if docai_entity_mapping_by_context is None:
    mapping_dict = docai_entity_mapping["all"][doc_type]
  else:
    mapping_dict = docai_entity_mapping_by_context.get(
        doc_type) or docai_entity_mapping["all"][doc_type]


  # extract dl entities
  extracted_entity_dict = entities_extraction(data, mapping_dict, doc_type)
  # Create a list of entities dicts
  specialized_parser_entity_list = [v for k, v in extracted_entity_dict.items()]

  # this can be removed while integration
  # save extracted entities json
  # with open("{}.json".format(os.path.join(extracted_entities,
  #     gcs_doc_path.split('/')[-1][:-4])), "w") as outfile:
  #     json.dump(specialized_parser_entity_list, outfile, indent=4)
  Logger.info("Required entities created from Specialized parser response")
  return specialized_parser_entity_list


def write_config(bucket_name, blob_name, keys):
  storage_client = storage.Client()
  bucket = storage_client.bucket(bucket_name)
  blob = bucket.blob(blob_name)
  with blob.open("w") as f:
    f.write('"default_entities": {\n')
    for key in set(keys):
        f.write(f'  "{key}": ["{key.upper().replace(" ","_").replace("/", "_").replace(".", "_").replace("(", "").replace(")", "") }"],\n')
    f.write('}\n')


def form_parser_extraction(parser_details: dict, gcs_doc_path: str,
                           doc_type: str, context: str, timeout: int):
  """
  This is form parser extraction main function. It will send
  request to parser and retrieve response and call
    default and derived entities functions

  Parameters
    ----------
    parser_details: It has parser info like parser id, name, location, and etc
    gcs_doc_path: Document gcs path
    doc_type: Document Type
    context: context name
    timeout: Max time given for extraction entities using async form parser API

  Returns: Form parser response - list of dicts having entity, value,
    confidence and manual_extraction information.
    -------
  """

  location = parser_details["location"]
  processor_id = parser_details["processor_id"]
  opts = {}

  # Location can be 'us' or 'eu'
  if location == "eu":
    opts = {"api_endpoint": "eu-documentai.googleapis.com"}

  client = documentai.DocumentProcessorServiceClient(client_options=opts)
  # create a temp folder to store parser op, delete folder once processing done
  # call create gcs bucket function to create bucket,
  # folder will be created automatically not the bucket
  gcs_output_uri = f"gs://{DOCAI_OUTPUT_BUCKET_NAME}"
  letters = string.ascii_lowercase
  temp_folder = "".join(random.choice(letters) for i in range(10))
  gcs_output_uri_prefix = "temp_" + temp_folder
  # temp folder location
  destination_uri = f"{gcs_output_uri}/{gcs_output_uri_prefix}/"
  # delete temp folder
  # del_gcs_folder(gcs_output_uri.split("//")[1], gcs_output_uri_prefix)
  gcs_documents = documentai.GcsDocuments(documents=[{
      "gcs_uri": gcs_doc_path,
      "mime_type": "application/pdf"
  }])
  input_config = documentai.BatchDocumentsInputConfig\
      (gcs_documents=gcs_documents)
  # Temp op folder location
  output_config = documentai.DocumentOutputConfig(
      gcs_output_config={"gcs_uri": destination_uri})

  Logger.info(f"input_config = {input_config}")
  Logger.info(f"output_config = {output_config}")
  Logger.info(f"processor_id = {processor_id}")

  # parser api end point
  # name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
  Logger.info("Form parser extraction api called")

  # request for Doc AI
  request = documentai.types.document_processor_service.BatchProcessRequest(
      name=processor_id,
      input_documents=input_config,
      document_output_config=output_config,
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
  form_parser_text = ""
  # saving form parser json, this can be removed from pipeline
  if not os.path.exists(temp_folder):
    os.mkdir(temp_folder)
  # browse through output jsons
  for i, blob in enumerate(blob_list):
    # If JSON file, download the contents of this blob as a bytes object.
    if ".json" in blob.name:
      blob_as_bytes = blob.download_as_bytes()
      # saving the parser response to the folder, remove this while integration
      # parser_json_fname = "temp.json"
      parser_json_fname = \
          os.path.join(temp_folder, f"res_{i}.json")
      with open(parser_json_fname, "wb") as file_obj:
        blob.download_to_file(file_obj)

      document = documentai.types.Document.from_json(blob_as_bytes)
      # print(f"Fetched file {i + 1}")
      form_parser_text += document.text
      # Read the text recognition output from the processor
      keys = []
      for page in document.pages:
        for form_field in page.form_fields:
          field_name, field_name_confidence, field_coordinates = \
              extract_form_fields(form_field.field_name, document)
          field_value, field_value_confidence, value_coordinates = \
              extract_form_fields(form_field.field_value, document)
          # noise removal from keys and values
          field_name = clean_form_parser_keys(field_name)
          field_value = strip_value(field_value)
          temp_dict = {
              "key": field_name,
              "key_coordinates": field_coordinates,
              "value": field_value,
              "value_coordinates": value_coordinates,
              "key_confidence": round(field_name_confidence, 2),
              "value_confidence": round(field_value_confidence, 2),
              "page_no": int(page.page_number),
              "page_width": int(page.dimension.width),
              "page_height": int(page.dimension.height)
          }

          print(f"Extracted Entities: key={field_name}"
                f" value={field_value}, "
                f" key_confidence={round(field_name_confidence, 2)},"
                f" value_confidence={round(field_value_confidence, 2)}")
          keys.append(field_name)
          extracted_entity_list.append(temp_dict)

      print("Extraction completed")
    else:
      print(f"Skipping non-supported file type {blob.name}")

  # Get corresponding mapping dict, for specific context or fallback to "all"
  docai_entity_mapping = get_docai_entity_mapping()

  print(f"context={context}")
  docai_entity_mapping_by_context = docai_entity_mapping.get(context)
  if docai_entity_mapping_by_context is None:
    mapping_dict = docai_entity_mapping["all"][doc_type]
  else:
    mapping_dict = docai_entity_mapping_by_context.get(
        doc_type) or docai_entity_mapping["all"][doc_type]

  print(f"context = {context}")
  print(f"doc_type = {doc_type}")
  print(f"mapping_dict = {mapping_dict}")

  # Extract desired entites from form parser
  try:
    form_parser_entities_list, flag = form_parser_entities_mapping(
        extracted_entity_list, mapping_dict, form_parser_text, temp_folder)
    print(f"form_parser_entities_list={form_parser_entities_list}, flag={flag}")
    # delete temp folder
    # if os.path.exists(temp_folder):
    #   shutil.rmtree(temp_folder)
    # del_gcs_folder(gcs_output_uri.split("//")[1], gcs_output_uri_prefix)
    Logger.info("Required entities created from Form parser response")
    return form_parser_entities_list, flag
  except Exception as e:
    Logger.error(e)
    if os.path.exists(temp_folder):
      shutil.rmtree(temp_folder)


def extract_entities(gcs_doc_path: str, doc_type: str, context: str):
  """
  This function calls specialized parser or form parser depends on document type

  Parameters
  ----------
  gcs_doc_path: Document gcs path
  doc_type: Type of documents. Ex: unemployment_form, driver_license, and etc
  context: context

  Returns
  -------
    List of dicts having entity, value, confidence and
           manual_extraction information.
    Extraction accuracy
  """
  Logger.info(f"extract_entities with gcs_doc_path={gcs_doc_path}, "
              f"doc_type={doc_type}, context={context}")
  # read parser details from configuration json file
  parsers_info = get_parser_config()
  parser_information = parsers_info.get(doc_type)
  # if parser present then do extraction else update the status
  if parser_information:
    parser_name = parser_information["parser_name"]
    parser_type = parser_information["parser_type"]

    if parser_type == "FORM_PARSER_PROCESSOR":
      Logger.info(f"Form parser extraction started for"
                  f" this document:{doc_type}")
      desired_entities_list, flag = form_parser_extraction(
          parser_information, gcs_doc_path, doc_type, context, 300)
    else:
      Logger.info(f"Specialized parser extraction "
                  f"started for this document:{doc_type}")
      flag = True
      desired_entities_list = specialized_parser_extraction(
          parser_information, gcs_doc_path, doc_type, context)

    # calling standard entity mapping function to standardize the entities
    final_extracted_entities = standard_entity_mapping(desired_entities_list,
                                                       parser_name)
    # calling post processing utility function
    # input json is the extracted json file after your mapping script
    input_dict = get_json_format_for_processing(final_extracted_entities)
    input_dict, output_dict = data_transformation(input_dict)
    final_extracted_entities = correct_json_format_for_db(
        output_dict, final_extracted_entities)
    # with open("{}.json".format(os.path.join(mapped_extracted_entities,
    #         gcs_doc_path.split('/')[-1][:-4])),
    #           "w") as outfile:
    #     json.dump(final_extracted_entities, outfile, indent=4)

    # extraction accuracy calculation
    document_extraction_confidence, extraction_status = \
      extraction_accuracy_calc(final_extracted_entities, flag)
    # print(final_extracted_entities)
    # print(document_extraction_confidence)
    Logger.info(f"Extraction completed for this document:{doc_type}")
    return final_extracted_entities, \
          document_extraction_confidence, extraction_status
  else:
    # Parser not available
    Logger.error(f"Parser not available for this document:{doc_type}")
    # print("parser not available for this document")
    return None
