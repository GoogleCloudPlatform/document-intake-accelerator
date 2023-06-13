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
import re
import traceback
import warnings
from typing import Any
from typing import Dict
from typing import List
from common.models import Document
import proto
from google.cloud import documentai_v1 as documentai
from google.cloud import storage
from common.db_client import bq_client
from common.utils.stream_to_bq import stream_document_to_bigquery
from common.utils.format_data_for_bq import format_data_for_bq
import common.config
from common.utils import process_extraction_result_helper
from common.config import STATUS_SUCCESS, STATUS_ERROR
from common.config import DocumentWrapper
from common.config import PDF_MIME_TYPE
from common.config import get_docai_entity_mapping
from common.extraction_config import DOCAI_ATTRIBUTES_TO_IGNORE
from common.extraction_config import DOCAI_OUTPUT_BUCKET_NAME
from common.extraction_config import ExtractionOutput
from common.utils.helper import get_processor_location
from common.utils.helper import split_uri_2_path_filename
from common.utils.logging_handler import Logger
from . import utils_functions
from .change_json_format import correct_json_format_for_db
from .change_json_format import get_json_format_for_processing
from .correct_key_value import data_transformation
from .utils_functions import clean_form_parser_keys
from .utils_functions import extraction_accuracy_calc
from .utils_functions import form_parser_entities_mapping
from .utils_functions import strip_value

warnings.simplefilter(action="ignore")

storage_client = storage.Client()
bq = bq_client()


def handle_extraction_results(extraction_output: List[ExtractionOutput]):
  # Update status for all documents that were requested for extraction
  count = 0
  Logger.info(
      f"handle_extraction_results - Handling results for extraction_output={extraction_output}")

  # extraction_output

  for extraction_item in iter(extraction_output):
    Logger.info(f"handle_extraction_results - {extraction_item}")
    uid = extraction_item.uid
    document = Document.find_by_uid(uid)
    if not document:
      Logger.error(
          f"handle_extraction_results - Could not retrieve document by uid {uid}")
      continue
    case_id = document.case_id
    gcs_url = document.url
    document_type = document.document_type
    doc_class = document.document_class
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

    entities_for_bq = format_data_for_bq(extraction_item.extracted_entities)
    count += 1
    Logger.info(
        f"extraction_api - Streaming {count} data to BigQuery for {gcs_url} "
        f"case_id={case_id}, uid={uid}, "
        f"document_type={document_type}, "
        f"doc_class={doc_class}")
    # stream_document_to_bigquery updates data to bigquery
    bq_update_status = stream_document_to_bigquery(bq, case_id, uid,
                                                   doc_class, document_type,
                                                   entities_for_bq, gcs_url)
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

    # checking if both databases are updated successfully
    #   if db_update_status.status_code == 200 and bq_update_status == []:
    #     document = {"case_id": case_id,
    #                 "uid": uid,
    #                 "doc_type": document_type,
    #                 "doc_class": doc_class,
    #                 "gcs_url": gcs_url,
    #                 "entities": extraction_output[conf][0],
    #                 "score": extraction_output[conf][1],
    #                 "extraction_status": extraction_output[conf][2],
    #                 "extraction_field_min_score": extraction_output[conf][3],
    #                 "message": f"document with case_id {case_id} ,uid_id {uid} "
    #                            f"successfully extracted"
    #                 }
    #     if "results" not in success_response.keys():
    #       success_response["results"] = []
    #     success_response["results"].append(document)
    #   else:
    #     Logger.error(
    #       f"extraction_api - Extraction database update failed for {gcs_url},"
    #       f" uid={uid}")
    #     err = traceback.format_exc().replace("\n", " ")
    #     Logger.error(err)
    #     update_extraction_status(case_id, uid, STATUS_ERROR, None, None, None)
    # Logger.info(f"extraction_api - Successfully Completed for {count} documents!")

    # if document is application form then update autoapproval status
    if document_type == "application_form":
      autoapproval_status = process_extraction_result_helper.get_autoapproval_status(
          None, extraction_item.extraction_score,
          extraction_item.extraction_field_min_score,
          None, doc_class,
          document_type)
      Logger.info(f"autoapproval_status for application:{autoapproval_status}")
      if autoapproval_status is not None:
        process_extraction_result_helper.update_autoapproval_status(case_id,
                                                                    uid,
                                                                    STATUS_SUCCESS,
                                                                    autoapproval_status[
                                                                      0], "yes")
    elif document_type == "supporting_documents":
      if extraction_item.extraction_score is not None:
        Logger.info(
            f"extraction score is {extraction_item.extraction_score} for {uid}")
        process_extraction_result_helper.validate_match_approve(case_id, uid,
                                                                extraction_item.extraction_score,
                                                                extraction_item.extraction_field_min_score,
                                                                extraction_item.extracted_entities,
                                                                doc_class)


# Handling Nested labels for CDE processor
def get_key_values_dic(entity: documentai.Document.Entity,
    document_entities: Dict[str, Any],
    parent_key: str = None
) -> None:
  # Fields detected. For a full list of fields for each processor see
  # the processor documentation:
  # https://cloud.google.com/document-ai/docs/processors-list

  entity_key = entity.get("type", "").replace("/", "_")
  confidence = entity.get("confidence")
  normalized_value = entity.get("normalizedValue")

  if normalized_value:
    if isinstance(normalized_value,
                  dict) and "booleanValue" in normalized_value.keys():
      normalized_value = normalized_value.get("booleanValue")
    else:
      normalized_value = normalized_value.get("text")

  if parent_key is not None and parent_key in document_entities.keys():
    key = parent_key
    new_entity_value = (
        entity_key,
        normalized_value if normalized_value is not None else entity.get(
            "mentionText"),
        confidence,
    )
  else:
    key = entity_key
    new_entity_value = (
        normalized_value if normalized_value is not None else entity.get(
            "mentionText"),
        confidence,
    )

  existing_entity = document_entities.get(key)
  if not existing_entity:
    document_entities[key] = []
    existing_entity = document_entities.get(key)

  if len(entity.get("properties", [])) > 0:
    # Sub-labels (only down one level)
    for prop in entity.get("properties", []):
      get_key_values_dic(prop, document_entities, entity_key)
  else:
    existing_entity.append(new_entity_value)


def specialized_parser_extraction_from_json(data, doc_class: str, context: str):
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
  print("Extracted Entities:")
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
      print(
          f"Field Name = {key_name}, Value = {value}, Confidence = {confidence}")

  # Get corresponding mapping dict, for specific context or fallback to "all" or generate new one on the fly
  docai_entity_mapping = get_docai_entity_mapping()
  if context is None: context = "California"  # TODO context is not used
  docai_entity_mapping_by_context = docai_entity_mapping.get(context)
  print(
      f"context = {context}, {docai_entity_mapping_by_context}, {doc_class not in docai_entity_mapping['all']}")
  if docai_entity_mapping_by_context is None:
    if doc_class not in docai_entity_mapping["all"]:
      Logger.info(
          f"No mapping found for context={context} and doc_class={doc_class}, generating default mapping on the fly")
      # Generate mapping on the fly
      mapping_dict = {"default_entities": default_mappings}
    else:
      mapping_dict = docai_entity_mapping["all"][doc_class]
  else:
    mapping_dict = docai_entity_mapping_by_context.get(doc_class)

  # extract dl entities
  extracted_entity_dict = utils_functions.entities_extraction(data,
                                                              mapping_dict,
                                                              doc_class)

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
    configs: List[DocumentWrapper],
    doc_class: str, processed_documents, entities: List[ExtractionOutput]):
  """
    This is specialized parser extraction main function.
    It will send request to parser and retrieve response and call
        default and derived entities functions

    Parameters
    ----------
    processor: It has parser info like parser id, name, location, and etc
    configs:
    doc_class: Document class

    Returns: Specialized parser response - list of dicts having entity,
     value, confidence and manual_extraction information.
    -------
  """

  for input_gcs_source in processed_documents:
    config = get_config_by_uri(input_gcs_source, configs)
    if config is None:
      Logger.error(
          f"specialized_parser_extraction - Could not retrieve back config for {input_gcs_source}")
      continue
    Logger.info(f"specialized_parser_extraction - Handling results for "
                f"{input_gcs_source} with config={config}")

    for document in processed_documents[input_gcs_source]:
      try:
        # TODO handle sharding
        json_string = proto.Message.to_json(document)
        data = json.loads(json_string)
        specialized_parser_entities_list = specialized_parser_extraction_from_json(
            data, doc_class, config.context)
        entities.append(post_processing(config.uid,
                                      specialized_parser_entities_list, True))
      except Exception as e:
        Logger.error(
            f"specialized_parser_extraction - Error for {input_gcs_source}:  {e}")
        err = traceback.format_exc().replace("\n", " ")
        Logger.error(err)



def get_callback_fn(operation, processor_type: str, doc_class: str, configs):
  def post_process_extract(future):
    print(f"post_process_extract - Extraction Complete!")
    # print(f"operation.metadata={operation.metadata}")

    # Once the operation is complete,
    # get output document information from operation metadata
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
        print(
            f"post_process_extract - Could not parse output GCS destination:[{process.output_gcs_destination}]")
        continue

      output_bucket, output_prefix = matches.groups()
      output_gcs_destination = process.output_gcs_destination
      input_gcs_source = process.input_gcs_source
      print(
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
        Logger.info(
            f"post_process_extract - Adding {blob_count} gs://{output_bucket}/{blob.name}")
        document = documentai.Document.from_json(
            blob.download_as_bytes(), ignore_unknown_fields=True
        )
        if input_gcs_source not in documents.keys():
          documents[input_gcs_source] = []
        documents[input_gcs_source].append(document)

    Logger.info(
        f"post_process_extract - Loaded {sum([len(documents[x]) for x in documents if isinstance(documents[x], list)])} DocAI document objects retrieved from json. ")

    desired_entities_list = []
    if processor_type == "CUSTOM_EXTRACTION_PROCESSOR":
      Logger.info(f"post_process_extract - Specialized parser results handling"
                  f" document doc_class={doc_class} and {len(documents)} document(s).")
      specialized_parser_extraction(configs, doc_class, documents, desired_entities_list)
    elif processor_type == "FORM_PARSER_PROCESSOR":
      Logger.info(f"post_process_extract - Form parser results handling for"
                  f" document doc_class={doc_class} and {len(documents)} document(s).")
      form_parser_extraction(configs, doc_class, documents, desired_entities_list)

    handle_extraction_results(desired_entities_list)

  return post_process_extract


async def batch_extraction(processor, dai_client,
    configs: List[DocumentWrapper], doc_class: str):
  input_uris = sorted(set([config.gcs_url for config in configs]))
  Logger.info(f"batch_extraction - input_uris = {input_uris}")
  input_docs = [documentai.GcsDocument(gcs_uri=doc_uri,
                                       mime_type=PDF_MIME_TYPE)
                for doc_uri in list(input_uris)]
  gcs_documents = documentai.GcsDocuments(documents=input_docs)
  input_config = documentai.BatchDocumentsInputConfig \
    (gcs_documents=gcs_documents)

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
      f"batch_extraction - Calling DocAI API for {len(input_uris)} documents "
      f" using {processor.display_name} processor"
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
      get_callback_fn(operation=operation, processor_type=processor.type_,
                      configs=configs, doc_class=doc_class))
  Logger.info(
      f"batch_extraction - DocAI operation started in the background as LRO")


def get_config_by_uri(uri: str, configs: List[DocumentWrapper]):
  found = [config for config in configs if config.gcs_url == uri]
  if len(found) > 0:
    return found[0]
  return None


def form_parser_extraction(
    configs: List[DocumentWrapper],
    doc_class: str, processed_documents, entities: List[ExtractionOutput]):
  """
  This is form parser extraction main function. It will send
  request to parser and retrieve response and call
    default and derived entities functions

  Parameters
    ----------
    processor: It has parser info like parser id, name, location, and etc
    gcs_doc_path_uris: Document gcs path uris
    doc_class: Document Class
    timeout: Max time given for extraction entities using async form parser API

  Returns: Form parser response - list of dicts having entity, value,
    confidence and manual_extraction information.
    -------
  """

  def print_table_rows(
      table_rows, text: str
  ) -> None:
    for table_row in table_rows:
      row_text = ""
      for cell in table_row.cells:
        cell_text = layout_to_text(cell.layout, text)
        row_text += f"{repr(cell_text.strip())} | "
      print(row_text)

  def layout_to_text(layout: documentai.Document.Page.Layout, text: str) -> str:
    """
    Document AI identifies text in different parts of the document by their
    offsets in the entirety of the document's text. This function converts
    offsets to a string.
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in layout.text_anchor.text_segments:
      start_index = int(segment.start_index)
      end_index = int(segment.end_index)
      response += text[start_index:end_index]
    return response

  for input_gcs_source in processed_documents:
    extracted_entity_list = []
    form_parser_text = ""
    config = get_config_by_uri(input_gcs_source, configs)
    if config is None:
      Logger.error(
          f"form_parser_extraction - Could not retrieve back config for {input_gcs_source}")
      continue
    Logger.info(f"form_parser_extraction - Handling results for "
                f"{input_gcs_source} with config={config}")
    try:
      # json might be sharded
      Logger.info(f"form_parser_extraction - Handling results for "
                  f"{input_gcs_source} with config={config}")
      for document in processed_documents[input_gcs_source]:
        form_parser_text += document.text
        dirs, file_name = split_uri_2_path_filename(input_gcs_source)
        Logger.info(
            f"form_parser_extraction - handling results for {input_gcs_source}, "
            f"file_name = {file_name}, shard_count = {document.shard_info.shard_count}")
        text = document.text
        # Read the text recognition output from the processor
        for page in document.pages:
          for form_field in page.form_fields:
            field_name, field_name_confidence, field_coordinates = \
              utils_functions.extract_form_fields(form_field.field_name,
                                                  document)
            field_value, field_value_confidence, value_coordinates = \
              utils_functions.extract_form_fields(form_field.field_value,
                                                  document)
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
          print(f"\nFound {len(page.tables)} table(s):")
          for table in page.tables:
            num_collumns = len(table.header_rows[0].cells)
            num_rows = len(table.body_rows)
            print(f"Table with {num_collumns} columns and {num_rows} rows:")

            # Print header rows
            print("Columns:")
            print_table_rows(table.header_rows, text)
            # Print body rows
            print("Table body data:")
            print_table_rows(table.body_rows, text)

      docai_entity_mapping = get_docai_entity_mapping()
      docai_entity_mapping_by_context = docai_entity_mapping.get(config.context)
      # if mapping not specified, skip
      # TODO get rig of ALL ADP legacy logic - Clean all this up
      if docai_entity_mapping_by_context is None:
        if doc_class not in docai_entity_mapping["all"]:
          Logger.info(
              f"form_parser_extraction - No mapping found for context={config.context} and "
              f"doc_class={doc_class}, generating default mapping on the fly")
          # Generate mapping on the fly
          mapping_dict = {}
          temp_dict = {}
          for entity_dic in extracted_entity_list:
            field_name = entity_dic.get("key")
            temp_dict[field_name] = [field_name]
          mapping_dict["default_entities"] = temp_dict
        else:
          mapping_dict = docai_entity_mapping["all"][doc_class]
      else:
        mapping_dict = docai_entity_mapping_by_context.get(doc_class)

      Logger.info(
          f"form_parser_extraction - {input_gcs_source} context={config.context}, "
          f"doc_type={doc_class}, "
          f"mapping_dict={mapping_dict}")
      # Extract desired entities from form parser
      form_parser_entities_list, flag = form_parser_entities_mapping(
          extracted_entity_list, mapping_dict, form_parser_text)
      Logger.info(f"form_parser_extraction - {input_gcs_source} "
                  f"form_parser_entities_list={form_parser_entities_list}, "
                  f"flag={flag}")

      entities.append(
          post_processing(config.uid, form_parser_entities_list, flag))

    except Exception as e:
      Logger.error(f"form_parser_extraction - Extraction failed for "
                   f"{input_gcs_source} uid={config.uid}: "
                   f"{e}")

  # del_gcs_folder(gcs_output_uri.split("//")[1], gcs_output_uri_prefix)
  Logger.info(
      "form_parser_extraction - Required entities created from Form parser response - Complete!")


async def extract_entities(configs: List[DocumentWrapper], doc_class: str) -> \
    List[ExtractionOutput]:
  """
  This function calls specialized parser or form parser depends on document type

  Parameters
  ----------
  :param configs: Config for files to extract
  :param doc_class: Type of documents. Ex: unemployment_form, driver_license, and etc

  Returns
  -------
    List of dicts having entity, value, confidence and
           manual_extraction information.
    Extraction accuracy
  """
  Logger.info(f"extract_entities for {len(configs)} files, "
              f"doc_class={doc_class}")
  # read parser details from configuration json file
  parser_details = common.config.get_parser_by_doc_class(doc_class)

  if parser_details:
    processor_path = parser_details["processor_id"]

    location = parser_details.get("location",
                                  get_processor_location(processor_path))
    if not location:
      Logger.error(f"Unidentified location for parser {processor_path}")
      return []

    opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}

    dai_client = documentai.DocumentProcessorServiceClient(client_options=opts)
    processor = dai_client.get_processor(name=processor_path)
    # default_version = processor.default_processor_version
    # specific_version =  #TODO Add processor version info into Firestore and BigQuery for extracted data
    print(
        f"parser_type={processor.type_}, parser_name={processor.display_name}")

    await batch_extraction(processor, dai_client, configs, doc_class)

  else:
    # Parser not available
    Logger.error(f"Parser not available for this document: {doc_class}")
    # print("parser not available for this document")


def post_processing(uid, desired_entities_list, flag):
  # TODO remove all these magic legacy ADP conversions which break
  # calling standard entity mapping function to standardize the entities
  final_extracted_entities = desired_entities_list
  # final_extracted_entities = standard_entity_mapping(desired_entities_list) #Very unclear logic
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
                          extraction_score=extraction_score)
