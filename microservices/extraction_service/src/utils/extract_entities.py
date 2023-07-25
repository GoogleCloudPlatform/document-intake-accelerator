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
import datetime
import json
import os.path
import re
import traceback
import warnings
from typing import Any
from typing import Dict
from typing import List

import proto
from google.api_core.operation import Operation
from google.cloud import documentai_v1 as documentai
from google.cloud import storage

from common.utils.docai_warehouse_helper import process_document
from common.utils.document_ai_utils import get_key_values_dic
from common import models
from common.config import PDF_MIME_TYPE
from common.config import STATUS_ERROR
from common.config import STATUS_SUCCESS
from common.config import get_doc_type_by_doc_class
from common.config import get_docai_entity_mapping, get_docai_warehouse
from common.db_client import bq_client
from common.docai_config import DOCAI_ATTRIBUTES_TO_IGNORE
from common.docai_config import DOCAI_OUTPUT_BUCKET_NAME
from common.docai_config import ExtractionOutput
from common.utils import process_extraction_result_helper
from common.utils.format_data_for_bq import format_data_for_bq
from common.utils.helper import get_document_by_uri, split_uri_2_bucket_prefix
from common.utils.helper import split_uri_2_path_filename
from common.utils.logging_handler import Logger
from common.utils.stream_to_bq import stream_document_to_bigquery
from . import utils_functions
from .change_json_format import correct_json_format_for_db
from .change_json_format import get_json_format_for_processing
from .correct_key_value import data_transformation
from .utils_functions import clean_form_parser_keys
from .utils_functions import extraction_accuracy_calc
from .utils_functions import form_parser_entities_mapping
from .utils_functions import strip_value

warnings.simplefilter(action="ignore")

SERVICE_ACCOUNT_EMAIL_GKE = os.getenv("SERVICE_ACCOUNT_EMAIL_GKE")

storage_client = storage.Client()
bq = bq_client()


def find_document_type(doc_class: str, ocr_txt: str):
  doc_type = get_doc_type_by_doc_class(doc_class)
  default = doc_type.get("default", "")
  rules = doc_type.get("rules", [])
  for rule in rules:
    name = rule.get("name")
    ocr_text = rule.get("ocr_text")
    if ocr_text:
      if ocr_text.lower() in ocr_txt.lower():
        return name
    ocr_regex = rule.get("ocr_regex")
    if ocr_regex:
      if re.search(ocr_regex, ocr_txt):
        return name
  return default


def set_document_type(doc_class: str, ocr_txt: str, document: models.Document):
  doc_type = find_document_type(doc_class, ocr_txt)
  document.type = doc_type
  document.update()
  return doc_type


def handle_extraction_results(extraction_output: List[ExtractionOutput]):
  # Update status for all documents that were requested for extraction
  count = 0
  Logger.info(
      f"handle_extraction_results - Handling results for extraction_output={extraction_output}")

  # extraction_output

  for extraction_item in iter(extraction_output):
    Logger.info(f"handle_extraction_results - {extraction_item}")
    uid = extraction_item.uid
    document = models.Document.find_by_uid(uid)
    if not document:
      Logger.error(
          f"handle_extraction_results - Could not retrieve document by uid {uid}")
      continue
    case_id = document.case_id
    gcs_url = document.url
    doc_class = document.document_class

    document_type = set_document_type(doc_class, extraction_item.ocr_text, document)
    document.document_type = document_type
    document.ocr_text = extraction_item.ocr_text
    document.update()

    # find corresponding result in extraction_output
    extraction_result_keys = [key for key in extraction_output if
                              uid == key.uid]
    if len(extraction_result_keys) == 0:
      Logger.error(
          f"extraction_api - No extraction result returned for {gcs_url} and"
          f" uid={uid}")
      process_extraction_result_helper.update_extraction_status(case_id, uid,
                                                                STATUS_ERROR,
                                                                None, None,
                                                                None)
      continue

    # Stream Data to BQ
    entities_for_bq = format_data_for_bq(extraction_item.extracted_entities)
    count += 1
    Logger.info(
        f"extraction_api - Streaming {count} data to BigQuery for {gcs_url} "
        f"case_id={case_id}, uid={uid}, "
        f"doc_class={doc_class}")
    # stream_document_to_bigquery updates data to bigquery
    bq_update_status = stream_document_to_bigquery(bq, case_id, uid,
                                                   doc_class, document_type,
                                                   entities_for_bq, gcs_url,
                                                   document.ocr_text,
                                                   document.classification_score,
                                                   document.is_hitl_classified)
    if not bq_update_status:
      Logger.info(f"extraction_api - Successfully streamed {count} data to BQ ")
    else:
      Logger.error(
          f"extraction_api - Failed streaming to BQ, returned status {bq_update_status}")

    # update_extraction_status updates data to document collection
    db_update_status = process_extraction_result_helper.update_extraction_status(
        case_id, uid, STATUS_SUCCESS,
        extraction_item.extracted_entities,
        extraction_item.extraction_score,
        extraction_item.extraction_status)

    if extraction_item.extraction_score is not None:
      Logger.info(
          f"extraction score is {extraction_item.extraction_score} for {uid}")
      process_extraction_result_helper.validate_match_approve(case_id, uid,
                                                              extraction_item.extraction_score,
                                                              extraction_item.extraction_field_min_score,
                                                              extraction_item.extracted_entities,
                                                              doc_class)


def specialized_parser_extraction_from_json(data, db_document: models.Document):
  # remove unnecessary entities from parser
  for each_attr in DOCAI_ATTRIBUTES_TO_IGNORE:
    if "." in each_attr:
      parent_attr, child_attr = each_attr.split(".")
      for idx in range(len(data.get(parent_attr, 0))):
        data[parent_attr][idx].pop(child_attr, None)
    else:
      data.pop(each_attr, None)

  document_entities: Dict[str, Any] = {}
  for entity in data.get('entities'):
    get_key_values_dic(entity, document_entities)

  names = []
  values = []
  value_confidence = []
  default_mappings = {}
  Logger.debug("Extracted Entities:")
  for key in document_entities.keys():
    for val in document_entities[key]:
      if len(val) == 2:  # Flat Labels
        key_name = key
        value = val[0]
        confidence = val[1]
      elif len(val) == 3:  # Nested Labels
        key_name = val[0]
        value = val[1]
        confidence = val[2]
      else:
        continue

      names.append(key_name)
      values.append(value)
      value_confidence.append(confidence)
      default_mappings[key_name] = [key_name, ]
      Logger.debug(
          f"Field Name = {key_name}, Value = {value}, Confidence = {confidence}")

  # Get corresponding mapping dict, for specific context or fallback to "all" or generate new one on the fly
  docai_entity_mapping = get_docai_entity_mapping()
  docai_entity_mapping_by_context = docai_entity_mapping.get(
      db_document.context)
  # if mapping not specified, skip
  if docai_entity_mapping_by_context is None:
    if "all" not in docai_entity_mapping.keys() or db_document.document_class not in \
        docai_entity_mapping["all"]:
      Logger.info(
          f"No mapping found for context={db_document.context} and doc_class={db_document.document_class}, generating default mapping on the fly")
      # Generate mapping on the fly
      mapping_dict = {"default_entities": default_mappings}
    else:
      mapping_dict = docai_entity_mapping["all"][db_document.document_class]
  else:
    mapping_dict = docai_entity_mapping_by_context.get(
      db_document.document_class)

  # extract dl entities
  extracted_entity_dict = utils_functions.entities_extraction(data,
                                                              mapping_dict,
                                                              db_document.document_class)

  # Create a list of entities dicts
  specialized_parser_entity_list = [v for k, v in extracted_entity_dict.items()]

  # this can be removed while integration
  # save extracted entities json
  # with open("{}.json".format(os.path.join(extracted_entities,
  #     gcs_doc_path.split('/')[-1][:-4])), "w") as outfile:
  #     json.dump(specialized_parser_entity_list, outfile, indent=4)
  Logger.info("Required entities created from Specialized parser response")
  return specialized_parser_entity_list


def specialized_parser_extraction(
    processed_documents: Dict[str, List[documentai.Document]],
    entities: List[ExtractionOutput]):
  """
    This is specialized parser extraction main function.
    It will send request to parser and retrieve response and call
        default and derived entities functions

    Parameters
    ----------
    processed_documents:
    entities: List to be filled in

    -------
  """

  for input_gcs_source in processed_documents:
    db_document = get_document_by_uri(input_gcs_source)
    if not db_document:
      Logger.error(
          f"specialized_parser_extraction - Could not retrieve back matching document for {input_gcs_source}")
      continue

    Logger.info(f"specialized_parser_extraction - Handling results for "
                f"{input_gcs_source} with uid={db_document.uid}")

    for processed_doc in processed_documents[input_gcs_source]:
      try:
        # TODO handle sharding
        json_string = proto.Message.to_json(processed_doc)
        data = json.loads(json_string)
        specialized_parser_entities_list = specialized_parser_extraction_from_json(
            data, db_document)
        entities.append(post_processing(db_document.uid,
                                        specialized_parser_entities_list, data.get("text"), True))
      except Exception as e:
        Logger.error(
            f"specialized_parser_extraction - Error for {input_gcs_source}:  {e}")
        err = traceback.format_exc().replace("\n", " ")
        Logger.error(err)


def get_callback_fn(operation: Operation, processor_type: str):
  def post_process_extract(future):
    # Once the operation is complete,
    # get output document information from operation metadata
    try:
      metadata = documentai.BatchProcessMetadata(operation.metadata)
      if metadata.state != documentai.BatchProcessMetadata.State.SUCCEEDED:
        raise ValueError(
            f"post_process_extract - Batch Process Failed: {metadata.state_message}")

      documents = {}  # Contains per processed document, keys are path to original document

      # One process per Input Document
      blob_count = 0
      for process in metadata.individual_process_statuses:
        # output_gcs_destination format: gs://BUCKET/PREFIX/OPERATION_NUMBER/INPUT_FILE_NUMBER/
        # The Cloud Storage API requires the bucket name and URI prefix separately
        matches = re.match(r"gs://(.*?)/(.*)", process.output_gcs_destination)
        if not matches:
          Logger.warning(
              f"post_process_extract - Could not parse output GCS destination:[{process.output_gcs_destination}]")
          Logger.warning(f"post_process_extract - {process.status}")
          continue

        output_bucket, output_prefix = matches.groups()
        output_gcs_destination = process.output_gcs_destination
        input_gcs_source = process.input_gcs_source
        Logger.info(
            f"post_process_extract - Handling DocAI results for {input_gcs_source} using "
            f"process output {output_gcs_destination}")
        # Get List of Document Objects from the Output Bucket
        output_blobs = storage_client.list_blobs(output_bucket,
                                                 prefix=output_prefix + "/")

        # Document AI may output multiple JSON files per source file
        # Sharding happens when the output JSON File gets over a size threshold
        # (> 10MB, around 40 or 50 pages).
        for blob in output_blobs:
          # Document AI should only output JSON files to GCS
          if ".json" not in blob.name:
            Logger.warning(
                f"post_process_extract - Skipping non-supported file: {blob.name} - Mimetype: {blob.content_type}"
            )
            continue
          blob_count = blob_count + 1
          # Download JSON File as bytes object and convert to Document Object

          document = documentai.Document.from_json(
              blob.download_as_bytes(), ignore_unknown_fields=True
          )
          if input_gcs_source not in documents.keys():
            documents[input_gcs_source] = []
          documents[input_gcs_source].append(document)

          stream_data_to_documentai_warehouse(document, input_gcs_source)

      Logger.info(
          f"post_process_extract - Loaded {sum([len(documents[x]) for x in documents if isinstance(documents[x], list)])} DocAI document objects retrieved from json. ")

      desired_entities_list = []
      if processor_type == "CUSTOM_EXTRACTION_PROCESSOR":
        Logger.info(
            f"post_process_extract - Specialized parser results handling"
            f" for {len(documents)} document(s).")
        specialized_parser_extraction(documents,
                                      desired_entities_list)
      elif processor_type == "FORM_PARSER_PROCESSOR":
        Logger.info(f"post_process_extract - Form parser results handling for"
                    f" {len(documents)} document(s).")
        form_parser_extraction(documents,
                               desired_entities_list)
      handle_extraction_results(desired_entities_list)

    except Exception as ex:
      Logger.error(ex)
      err = traceback.format_exc().replace("\n", " ")
      Logger.error(err)

  return post_process_extract


def stream_data_to_documentai_warehouse(document_ai_output,
                                        uri: str):
  Logger.info(f"stream_data_to_documentai_warehouse - {uri}")
  document = get_document_by_uri(uri)
  if not document:
    return
  docai_warehouse_properties = get_docai_warehouse(document.document_class)
  bucket_name, document_path = split_uri_2_bucket_prefix(uri)
  display_name = os.path.basename(document_path)
  if docai_warehouse_properties:
    process_document(
        docai_warehouse_properties.get("project_number"),
        docai_warehouse_properties.get("api_location"),
        docai_warehouse_properties.get("folder_id"),
        display_name,
        docai_warehouse_properties.get("document_schema_id"),
        f"user:{SERVICE_ACCOUNT_EMAIL_GKE}",
        bucket_name, document_path, document_ai_output)


async def batch_extraction(processor: documentai.types.processor.Processor,
    dai_client, input_uris: List[str]):

  try:
    Logger.info(f"batch_extraction - input_uris = {input_uris}, "
                f"processor={processor.name}, {processor.type_}")
    input_docs = [documentai.GcsDocument(gcs_uri=doc_uri,
                                         mime_type=PDF_MIME_TYPE)
                  for doc_uri in list(input_uris)]
    gcs_documents = documentai.GcsDocuments(documents=input_docs)
    input_config = documentai.BatchDocumentsInputConfig \
      (gcs_documents=gcs_documents)

    # input_docs = [documentai.GcsDocument(gcs_uri=doc_uri,
    #                                      mime_type=PDF_MIME_TYPE)
    #               for doc_uri in list(input_uris)]
    # gcs_documents = documentai.GcsDocuments(documents=input_docs)
    # input_config = documentai.BatchDocumentsInputConfig \
    #   (gcs_documents=gcs_documents)

    # create a temp folder to store parser op, delete folder once processing done
    # call create gcs bucket function to create bucket,
    # folder will be created automatically not the bucket
    gcs_output_uri = f"gs://{DOCAI_OUTPUT_BUCKET_NAME}"

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S-%f")
    gcs_output_uri_prefix = "extractor_out_" + timestamp
    # temp folder location
    destination_uri = f"{gcs_output_uri}/{gcs_output_uri_prefix}/"
    # delete temp folder
    # del_gcs_folder(gcs_output_uri.split("//")[1], gcs_output_uri_prefix)

    # Temp op folder location
    output_config = documentai.DocumentOutputConfig(
        gcs_output_config={"gcs_uri": destination_uri})

    Logger.info(f"batch_extraction - input_config = {input_config}")
    Logger.info(f"batch_extraction - output_config = {output_config}")
    Logger.info(
        f"batch_extraction - Calling DocAI API for {len(input_uris)} document(s) "
        f" using {processor.display_name} processor "
        f"type={processor.type_}, path={processor.name}")

    # request for Doc AI
    request = documentai.types.document_processor_service.BatchProcessRequest(
        name=processor.name,
        input_documents=input_config,
        document_output_config=output_config,
    )
    operation = dai_client.batch_process_documents(request)
    # Continually polls the operation until it is complete.
    # This could take some time for larger files
    # Format: projects/PROJECT_NUMBER/locations/LOCATION/operations/OPERATION_ID
    operation.add_done_callback(
        get_callback_fn(operation=operation, processor_type=processor.type_))
    Logger.info(
        f"batch_extraction - DocAI extraction operation started in the background as LRO")
  except Exception as e:
    Logger.error(f"batch_extraction - Extraction failed for "
                 f"input_uris={input_uris}: "
                 f"{e}")
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)


def ocr_expression_match(text: str, regex):
  if text.lower().find(regex.lower()) != -1:
    return True
  return False


def form_parser_extraction(
    processed_documents: Dict[str, List[documentai.Document]],
    entities: List[ExtractionOutput]):
  """
  This is form parser extraction main function. It will send
  request to parser and retrieve response and call
    default and derived entities functions

  Parameters
    ----------
    processed_documents:
    entities: List having entity, value, confidence and manual_extraction information.
    -------
  """

  # def print_table_rows(
  #     table_rows, text: str
  # ) -> None:
  #   for table_row in table_rows:
  #     row_text = ""
  #     for cell in table_row.cells:
  #       cell_text = layout_to_text(cell.layout, text)
  #       row_text += f"{repr(cell_text.strip())} | "
  #     print(row_text)

  # def layout_to_text(layout: documentai.Document.Page.Layout, text: str) -> str:
  #   """
  #   Document AI identifies text in different parts of the document by their
  #   offsets in the entirety of the document's text. This function converts
  #   offsets to a string.
  #   """
  #   response = ""
  #   # If a text segment spans several lines, it will
  #   # be stored in different text segments.
  #   for segment in layout.text_anchor.text_segments:
  #     start_index = int(segment.start_index)
  #     end_index = int(segment.end_index)
  #     response += text[start_index:end_index]
  #   return response

  for input_gcs_source in processed_documents:
    db_document = get_document_by_uri(input_gcs_source)
    if not db_document:
      Logger.error(
          f"specialized_parser_extraction - Could not retrieve back matching document for {input_gcs_source}")
      continue

    extracted_entity_list = []
    form_parser_text = ""

    try:
      # json might be sharded
      Logger.info(f"form_parser_extraction - Handling results for "
                  f"{input_gcs_source} uid={db_document.uid}")
      for ai_document in processed_documents[input_gcs_source]:
        form_parser_text += ai_document.text
        dirs, file_name = split_uri_2_path_filename(input_gcs_source)
        Logger.info(
            f"form_parser_extraction - handling results for {input_gcs_source}, "
            f"file_name = {file_name}, shard_count = {ai_document.shard_info.shard_count}")

        # Read the text recognition output from the processor
        for page in ai_document.pages:
          for form_field in page.form_fields:
            field_name, field_name_confidence, field_coordinates = \
              utils_functions.extract_form_fields(form_field.field_name,
                                                  ai_document)
            field_value, field_value_confidence, value_coordinates = \
              utils_functions.extract_form_fields(form_field.field_value,
                                                  ai_document)
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
            extracted_entity_list.append(temp_dict)
            Logger.info(f"form_parser_extraction - Entities:  {temp_dict}")

          # TODO Add Table Extraction
          # print(f"\nFound {len(page.tables)} table(s):")
          # for table in page.tables:
          #   num_collumns = len(table.header_rows[0].cells)
          #   num_rows = len(table.body_rows)
          #   print(f"Table with {num_collumns} columns and {num_rows} rows:")
          #
          #   # Print header rows
          #   print("Columns:")
          #   print_table_rows(table.header_rows, text)
          #   # Print body rows
          #   print("Table body data:")
          #   print_table_rows(table.body_rows, text)

      docai_entity_mapping = get_docai_entity_mapping()
      docai_entity_mapping_by_context = docai_entity_mapping.get(
          db_document.context)
      # if mapping not specified, skip
      if docai_entity_mapping_by_context is None:
        if "all" not in docai_entity_mapping.keys() or db_document.document_class not in \
            docai_entity_mapping["all"]:
          Logger.info(
              f"form_parser_extraction - No mapping found for context={db_document.context} and "
              f"doc_class={db_document.document_class}, generating default mapping on the fly")
          # Generate mapping on the fly
          mapping_dict = {}
          temp_dict = {}
          for entity_dic in extracted_entity_list:
            field_name = entity_dic.get("key")
            temp_dict[field_name] = [field_name]
          mapping_dict["default_entities"] = temp_dict
        else:
          mapping_dict = docai_entity_mapping["all"][db_document.document_class]
      else:
        mapping_dict = docai_entity_mapping_by_context.get(
            db_document.document_class)

      Logger.info(
          f"form_parser_extraction - {input_gcs_source} context={db_document.context}, "
          f"doc_type={db_document.document_class}, "
          f"mapping_dict={mapping_dict}")
      # Extract desired entities from form parser
      form_parser_entities_list, flag = form_parser_entities_mapping(
          extracted_entity_list, mapping_dict, form_parser_text)
      Logger.info(f"form_parser_extraction - {input_gcs_source} "
                  f"form_parser_entities_list={form_parser_entities_list}, "
                  f"flag={flag}")

      entities.append(
          post_processing(db_document.uid, form_parser_entities_list,
                          form_parser_text, flag))

    except Exception as e:
      Logger.error(f"form_parser_extraction - Extraction failed for "
                   f"{input_gcs_source} uid={db_document.uid}: "
                   f"{e}")
      err = traceback.format_exc().replace("\n", " ")
      Logger.error(err)

  # del_gcs_folder(gcs_output_uri.split("//")[1], gcs_output_uri_prefix)
  Logger.info(
      "form_parser_extraction - Required entities created from Form parser response - Complete!")


async def extract_entities(processor: documentai.types.processor.Processor,
    dai_client, input_uris: List[str]):
  Logger.info(f"extract_entities - input_uris = {input_uris}, "
              f"parser_type={processor.type_}, "
              f"parser_name={processor.display_name}")
  await batch_extraction(processor, dai_client, input_uris)


def post_processing(uid, desired_entities_list, ocr_text, flag):
  final_extracted_entities = desired_entities_list

  input_dict = get_json_format_for_processing(final_extracted_entities)
  input_dict, output_dict = data_transformation(input_dict)
  final_extracted_entities = correct_json_format_for_db(
      output_dict, final_extracted_entities)
  # with open("{}.json".format(os.path.join(mapped_extracted_entities,
  #         gcs_doc_path.split('/')[-1][:-4])),
  #           "w") as outfile:
  #     json.dump(final_extracted_entities, outfile, indent=4)

  # extraction accuracy calculation
  extraction_score, extraction_status, extraction_field_min_score = \
    extraction_accuracy_calc(final_extracted_entities, flag)
  # print(final_extracted_entities)
  # print(document_extraction_confidence)
  Logger.info(f"Extraction completed for {uid}:  "
              f"extraction_score={extraction_score},"
              f" extraction_status={extraction_status}, "
              f"extraction_field_min_score={extraction_field_min_score}")

  return ExtractionOutput(uid=uid,
                          extracted_entities=final_extracted_entities,
                          extraction_status=extraction_status,
                          extraction_field_min_score=extraction_field_min_score,
                          extraction_score=extraction_score, ocr_text=ocr_text)
