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
import logging
import time
from typing import Any
from typing import Dict

import pandas as pd

import common.config
from common.utils.helper import get_processor_location

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
from .utils_functions import entities_extraction, download_pdf_gcs, \
  extract_form_fields, del_gcs_folder, \
  form_parser_entities_mapping, extraction_accuracy_calc, \
  clean_form_parser_keys, standard_entity_mapping, strip_value
from common.extraction_config import DOCAI_OUTPUT_BUCKET_NAME, \
  DOCAI_ATTRIBUTES_TO_IGNORE
from common.config import get_parser_config, get_docai_entity_mapping, get_document_types_config
from common.utils.logging_handler import Logger
import warnings
from google.cloud import storage
from google.api_core.exceptions import InternalServerError
from google.api_core.exceptions import RetryError
warnings.simplefilter(action="ignore")
from google.cloud import documentai_v1beta3

MIME_TYPE = "application/pdf"

# Handling Nested labels for CDE processor
def get_key_values_dic(entity: documentai.Document.Entity,
    document_entities: Dict[str, Any],
    parent_key: str = None
) -> None:

  # Fields detected. For a full list of fields for each processor see
  # the processor documentation:
  # https://cloud.google.com/document-ai/docs/processors-list

  entity_key = entity.type_.replace("/", "_")
  confidence = entity.confidence
  normalized_value = getattr(entity, "normalized_value", None)

  if parent_key is not None and parent_key in document_entities.keys():
    key = parent_key
    new_entity_value = (
        entity_key,
        normalized_value.text if normalized_value else entity.mention_text,
        confidence,

    )
  else:
    key = entity_key
    new_entity_value = (
        normalized_value.text if normalized_value else entity.mention_text,
        confidence,
    )

  existing_entity = document_entities.get(key)
  if not existing_entity:
    document_entities[key] = []
    existing_entity = document_entities.get(key)

  if len(entity.properties) > 0:
    # Sub-labels (only down one level)
    for prop in entity.properties:
      get_key_values_dic(prop, document_entities, entity_key)
  else:
    existing_entity.append(new_entity_value)


def specialized_parser_extraction(processor, dai_client, gcs_doc_path: str,
    doc_class: str, context: str):
  """
    This is specialized parser extraction main function.
    It will send request to parser and retrieve response and call
        default and derived entities functions

    Parameters
    ----------
    parser_details: It has parser info like parser id, name, location, and etc
    gcs_doc_path: Document gcs path
    doc_class: Document class

    Returns: Specialized parser response - list of dicts having entity,
     value, confidence and manual_extraction information.
    -------
  """

  blob = download_pdf_gcs(gcs_uri=gcs_doc_path)

  document = {
      "content": blob.download_as_bytes(),
      "mime_type": "application/pdf"
  }
  # Configure the process request
  request = {"name": processor.name, "raw_document": document}

  Logger.info(f"Calling Specialized parser extraction api for processor with name={processor.name} type={processor.type_}")
  start = time.time()
  # send request to parser
  result = dai_client.process_document(request=request)
  elapsed ="{:.0f}".format(time.time() - start)
  Logger.info(f"Elapsed time for operation {elapsed} seconds")

  parser_doc_data = result.document
  # convert to json
  json_string = proto.Message.to_json(parser_doc_data)
  # print("*********** Extracted data:")
  # print(json.dumps(parser_doc_data.entities, indent=4))
  # print("***********")
  data = json.loads(json_string)
  # remove unnecessary entities from parser
  for each_attr in DOCAI_ATTRIBUTES_TO_IGNORE:
    if "." in each_attr:
      parent_attr, child_attr = each_attr.split(".")
      for idx in range(len(data.get(parent_attr, 0))):
        data[parent_attr][idx].pop(child_attr, None)
    else:
      data.pop(each_attr, None)

  document_entities: Dict[str, Any] = {}
  for entity in parser_doc_data.entities:
    get_key_values_dic(entity, document_entities)

  names = []
  values = []
  value_confidence = []
  default_mappings = {}
  print("Extracted Entities:")
  for key in document_entities.keys():
    for val in document_entities[key]:
      if len(val) >= 3:  # There are Parent Key labels without values
        key_name = val[0]
        value = val[1]
        names.append(key_name)
        values.append(value)
        value_confidence.append(val[2])
        default_mappings[key_name] = [key_name, ]
        print(f"Field Name = {key_name}, Value = {value}, Confidence = {val[2]}")
  df = pd.DataFrame(
      {
          "Field Name": names,
          "Field Value": values,
          "Value Confidence": value_confidence,
      }
  )

  print(df)

  # Get corresponding mapping dict, for specific context or fallback to "all" or generate new one on the fly
  docai_entity_mapping = get_docai_entity_mapping()
  docai_entity_mapping_by_context = docai_entity_mapping.get(context)
  print(f"context = {context}, {docai_entity_mapping_by_context}, {doc_class not in docai_entity_mapping['all']}")
  if docai_entity_mapping_by_context is None:
    if doc_class not in docai_entity_mapping["all"]:
      Logger.info(f"No mapping found for context={context} and doc_class={doc_class}, generating default mapping on the fly")
      # Generate mapping on the fly
      mapping_dict = {"default_entities": default_mappings}
    else:
      mapping_dict = docai_entity_mapping["all"][doc_class]
  else:
    mapping_dict = docai_entity_mapping_by_context.get(doc_class)

  # extract dl entities
  extracted_entity_dict = entities_extraction(data, mapping_dict, doc_class)

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


def form_parser_extraction(processor, dai_client, gcs_doc_path: str,
    doc_class: str, context: str, timeout: int = 300):
  """
  This is form parser extraction main function. It will send
  request to parser and retrieve response and call
    default and derived entities functions

  Parameters
    ----------
    parser_details: It has parser info like parser id, name, location, and etc
    gcs_doc_path: Document gcs path
    doc_class: Document Class
    context: context name
    timeout: Max time given for extraction entities using async form parser API

  Returns: Form parser response - list of dicts having entity, value,
    confidence and manual_extraction information.
    -------
  """

  gcs_documents = documentai.GcsDocuments(documents=[{
      "gcs_uri": gcs_doc_path,
      "mime_type": "application/pdf"
  }])
  input_config = documentai.BatchDocumentsInputConfig \
    (gcs_documents=gcs_documents)

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

  # Temp op folder location
  output_config = documentai.DocumentOutputConfig(
      gcs_output_config={"gcs_uri": destination_uri})

  Logger.info(f"input_config = {input_config}")
  Logger.info(f"output_config = {output_config}")
  Logger.info(f"processor_name = {processor.display_name}")

  Logger.info(f"Calling Form parser extraction api for processor with name={processor.name} type={processor.type_}, path={processor.display_name}")
  start = time.time()

  # request for Doc AI
  request = documentai.types.document_processor_service.BatchProcessRequest(
      name="projects/prior-auth-poc/locations/us/processors/79b2c1fa8b5b2e8a",
      input_documents=input_config,
      document_output_config=output_config,
  )
  operation = dai_client.batch_process_documents(request)

  # Continually polls the operation until it is complete.
  # This could take some time for larger files
  # Format: projects/PROJECT_NUMBER/locations/LOCATION/operations/OPERATION_ID
  try:
    Logger.info(f"Waiting for operation {operation.operation.name} to complete...")
    operation.result(timeout=timeout)
  # Catch exception when operation doesn't finish before timeout
  except (RetryError, InternalServerError) as e:
    Logger.error(e.message)
    Logger.error("Failed to process documents")
    return [], False

  elapsed ="{:.0f}".format(time.time() - start)
  Logger.info(f"Elapsed time for operation {elapsed} seconds")

  # Once the operation is complete,
  # get output document information from operation metadata
  metadata = documentai.BatchProcessMetadata(operation.metadata)
  if metadata.state != documentai.BatchProcessMetadata.State.SUCCEEDED:
    raise ValueError(f"Batch Process Failed: {metadata.state_message}")

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
    Logger.info(f"Output directory used for extraction locally: {temp_folder}")
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
        Logger.info(f"Copying blob {blob.name} as {parser_json_fname}")
        blob.download_to_file(file_obj)

      document = documentai.types.Document.from_json(blob_as_bytes)
      # print(f"Fetched file {i + 1}")
      form_parser_text += document.text
      # Read the text recognition output from the processor
      keys = []
      values = []
      value_confidences = []
      key_confidences = []
      for page in document.pages:
        for form_field in page.form_fields:
          field_name, field_name_confidence, field_coordinates = \
            extract_form_fields(form_field.field_name, document)
          field_value, field_value_confidence, value_coordinates = \
            extract_form_fields(form_field.field_value, document)
          # noise removal from keys and values
          field_name = clean_form_parser_keys(field_name)
          field_value = strip_value(field_value)
          value_confidence = round(field_value_confidence, 2)
          key_confidence = round(field_name_confidence, 2)
          temp_dict = {
              "key": field_name,
              "key_coordinates": field_coordinates,
              "value": field_value,
              "value_coordinates": value_coordinates,
              "key_confidence": key_confidence,
              "value_confidence": value_confidence,
              "page_no": int(page.page_number),
              "page_width": int(page.dimension.width),
              "page_height": int(page.dimension.height)
          }

          keys.append(field_name)
          values.append(field_value)
          value_confidences.append(value_confidence)
          key_confidences.append(key_confidence)
          extracted_entity_list.append(temp_dict)

      df = pd.DataFrame(
          {
              "Field Name": keys,
              "Key Value Confidence": key_confidences,
              "Field Value": values,
              "Field Value Confidence": value_confidences,
          }
      )
      print(df)

      Logger.info(f"Extraction completed for {gcs_doc_path}")
    else:
      Logger.info(f"Skipping non-supported file type {blob.name}")

  docai_entity_mapping = get_docai_entity_mapping()
  docai_entity_mapping_by_context = docai_entity_mapping.get(context)
  #if mapping not specified, skip
  if docai_entity_mapping_by_context is None:
    if doc_class not in docai_entity_mapping["all"]:
      Logger.info(f"No mapping found for context={context} and doc_class={doc_class}, generating default mapping on the fly")
      # Generate mapping on the fly
      mapping_dict = {}
      temp_dict = {}
      for entity_dic in extracted_entity_list:
        field_name = entity_dic.get("key")
        temp_dict[field_name] = [field_name]
      mapping_dict["default_entities"] = temp_dict
      # "default_entities": {
      #     "Date": ["date"],
      #     "Name": ["name"],
      #     "Occupation": ["occupation"],
      #     "Emergency Contact": ["emergency_contact"],
      #     "Referred By": ["referred_by"],
    else:
      mapping_dict = docai_entity_mapping["all"][doc_class]
  else:
    mapping_dict = docai_entity_mapping_by_context.get(doc_class)

  Logger.info(f"context={context}, doc_type={doc_class}, mapping_dict={mapping_dict}")

  # Extract desired entities from form parser
  try:
    form_parser_entities_list, flag = form_parser_entities_mapping(
        extracted_entity_list, mapping_dict, form_parser_text, temp_folder)
    Logger.info(f"form_parser_entities_list={form_parser_entities_list}, flag={flag}")
    # delete temp folder
    if os.path.exists(temp_folder):
      shutil.rmtree(temp_folder)
    del_gcs_folder(gcs_output_uri.split("//")[1], gcs_output_uri_prefix)
    Logger.info("Required entities created from Form parser response")
    return form_parser_entities_list, flag
  except Exception as e:
    Logger.error(e)
    if os.path.exists(temp_folder):
      shutil.rmtree(temp_folder)


def extract_entities(gcs_doc_path: str, doc_class: str, context: str):
  """
  This function calls specialized parser or form parser depends on document type

  Parameters
  ----------
  gcs_doc_path: Document gcs path
  doc_class: Type of documents. Ex: unemployment_form, driver_license, and etc
  context: context

  Returns
  -------
    List of dicts having entity, value, confidence and
           manual_extraction information.
    Extraction accuracy
  """
  Logger.info(f"extract_entities with gcs_doc_path={gcs_doc_path}, "
              f"doc_class={doc_class}, context={context}")
  # read parser details from configuration json file
  parser_details = common.config.get_parser_by_doc_class(doc_class)

  if parser_details:
    processor_path = parser_details["processor_id"]

    location = parser_details.get("location", get_processor_location(processor_path))
    if not location:
      Logger.error(f"Unidentified location for parser {processor_path}")
      return

    opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}

    dai_client = documentai.DocumentProcessorServiceClient(client_options=opts)
    processor = dai_client.get_processor(name=processor_path)

    print(f"parser_type={processor.type_}, parser_name={processor.display_name}")
    # Todo Refactor to extract based on selected strategy (to be configured) and not per parser type.
    if processor.type_ == "CUSTOM_EXTRACTION_PROCESSOR":
      Logger.info(f"Specialized parser extraction "
                  f"started for this document doc_class={doc_class}")
      flag = True
      desired_entities_list = specialized_parser_extraction(
          processor, dai_client, gcs_doc_path, doc_class, context)
    else:
      Logger.info(f"Form parser extraction started for"
                  f" document doc_class={doc_class}")
      desired_entities_list, flag = form_parser_extraction(
          processor, dai_client, gcs_doc_path, doc_class, context)

    # calling standard entity mapping function to standardize the entities
    final_extracted_entities = standard_entity_mapping(desired_entities_list)
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
    document_extraction_confidence, extraction_status, extraction_field_min_score = \
      extraction_accuracy_calc(final_extracted_entities, flag)
    # print(final_extracted_entities)
    # print(document_extraction_confidence)
    Logger.info(f"Extraction completed for {doc_class} {gcs_doc_path}:  "
                f"document_extraction_confidence={document_extraction_confidence},"
                f" extraction_status={extraction_status}, "
                f"extraction_field_min_score={extraction_field_min_score}")

    return final_extracted_entities, \
           document_extraction_confidence, extraction_status, extraction_field_min_score
  else:
    # Parser not available
    Logger.error(f"Parser not available for this document: {doc_class}")
    # print("parser not available for this document")
    return None
