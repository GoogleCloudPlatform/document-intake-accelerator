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
import os.path
import re
import traceback
from typing import Dict
from typing import List

from google.cloud import documentai_v1 as documentai
from google.cloud import storage
from pikepdf import Pdf
from .api_calls import upload_document, update_classification_status
from common.utils.api_calls import extract_documents
import common.config
from common.config import get_classification_default_class, get_classification_confidence_threshold
from common.config import DOC_CLASS_SPLIT_DISPLAY_NAME
from common.config import PDF_MIME_TYPE
from common.config import STATUS_SPLIT
from common.config import STATUS_SUCCESS
from common.config import get_document_class_by_classifier_label
from common.docai_config import DOCAI_OUTPUT_BUCKET_NAME

from common.utils import helper
from common.utils.helper import get_id_from_file_path

from common.utils.logging_handler import Logger
from .download_pdf_gcs import download_pdf_gcs

PDF_EXTENSION = ".pdf"

storage_client = storage.Client()


async def batch_classification(processor: documentai.types.processor.Processor,
    dai_client, input_uris: List[str]):
  Logger.info(f"batch_classification - input_uris = {input_uris}")
  input_docs = [documentai.GcsDocument(gcs_uri=doc_uri, mime_type=PDF_MIME_TYPE)
                for doc_uri in list(input_uris)]
  gcs_documents = documentai.GcsDocuments(documents=input_docs)
  input_config = documentai.BatchDocumentsInputConfig(gcs_documents=gcs_documents)

  # create a temp folder to store parser op, delete folder once processing done
  # call create gcs bucket function to create bucket,
  # folder will be created automatically not the bucket
  gcs_output_uri = f"gs://{DOCAI_OUTPUT_BUCKET_NAME}"

  timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S-%f")
  gcs_output_uri_prefix = "classifier_out_" + timestamp
  # temp folder location
  destination_uri = f"{gcs_output_uri}/{gcs_output_uri_prefix}/"
  # delete temp folder
  # del_gcs_folder(gcs_output_uri.split("//")[1], gcs_output_uri_prefix)

  # Temp op folder location
  output_config = documentai.DocumentOutputConfig(
      gcs_output_config={"gcs_uri": destination_uri})

  Logger.info(f"batch_classification - input_config = {input_config}")
  Logger.info(f"batch_classification - output_config = {output_config}")
  Logger.info(
      f"batch_classification - Calling DocAI API for {len(input_uris)} document(s) "
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

  # operation.result()
  # metadata = documentai.BatchProcessMetadata(operation.metadata)
  operation.add_done_callback(
      get_callback_fn())
  Logger.info(
      f"batch_classification - DocAI extraction operation started in the background as LRO")


def get_callback_fn():
  def post_process_classify(future):
    print(f"post_process_classify - Classification Complete!")
    print(f"post_process_classify - operation.metadata={future.metadata}")

    metadata = documentai.BatchProcessMetadata(future.metadata)
    documents = {}

    if metadata.state != documentai.BatchProcessMetadata.State.SUCCEEDED:
      raise ValueError(f"Batch Process Failed: {metadata.state_message}")

    # One process per Input Document
    for process in metadata.individual_process_statuses:
      try:
        # output_gcs_destination format: gs://BUCKET/PREFIX/OPERATION_NUMBER/INPUT_FILE_NUMBER/
        # The Cloud Storage API requires the bucket name and URI prefix separately
        matches = re.match(r"gs://(.*?)/(.*)", process.output_gcs_destination)
        if not matches:
          Logger.warning(
              f"post_process_classify - "
              f"Could not parse output GCS destination:[{process.output_gcs_destination}]")
          Logger.warning(f"post_process_classify - {process.status}")
          continue

        output_bucket, output_prefix = matches.groups()
        output_gcs_destination = process.output_gcs_destination
        input_gcs_source = process.input_gcs_source
        Logger.info(
            f"post_process_classify - output_bucket = {output_bucket}, "
            f"output_prefix={output_prefix}, "
            f"input_gcs_source = {input_gcs_source}, "
            f"output_gcs_destination = {output_gcs_destination}")

        # Get List of Document Objects from the Output Bucket
        output_blobs = storage_client.list_blobs(output_bucket,
                                                 prefix=output_prefix + "/")

        # Document AI may output multiple JSON files per source file
        # Todo handle sharding

        for blob in output_blobs:
          # Document AI should only output JSON files to GCS
          if ".json" not in blob.name:
            Logger.info(
                f"post_process_classify - Skipping non-supported file: {blob.name} - Mimetype: {blob.content_type}"
            )
            continue

          # Download JSON File as bytes object and convert to Document Object
          Logger.info(f"Fetching gs://{output_bucket}/{blob.name}")
          document = documentai.Document.from_json(
              blob.download_as_bytes(), ignore_unknown_fields=True
          )
          dirs, file_name = helper.split_uri_2_path_filename(input_gcs_source)
          Logger.info(
              f"post_process_classify - dirs = {dirs}, file_name = {file_name}")

          entities = document.entities

          # For possible sharding across blobs
          if input_gcs_source in documents.keys():
            labels = documents[input_gcs_source].get('labels')
            scores = documents[input_gcs_source].get('scores')
            pages = documents[input_gcs_source].get('pages')
          else:
            labels = []
            scores = []
            pages = []

          for index, entity in enumerate(entities):
            # If Splitter, multiple pages present
            if len(entity.page_anchor.page_refs) > 0:
              start = int(entity.page_anchor.page_refs[0].page)
              end = int(entity.page_anchor.page_refs[-1].page)
            # If Classifier, then pages are not returned
            else:
              start = 0
              end = document.pages[-1].page_number

            score = float('%.2f' % entity.confidence)
            label = entity.type_.replace("/", "_")

            scores.append(score)
            labels.append(label)
            pages.append((start, end))

            Logger.info(
                f"post_process_classify - Classification result for {input_gcs_source}: "
                f"document_class={label}, confidence={score}, "
                f"start={start}, end={end}")

          documents[input_gcs_source] = {'scores': scores,
                                         'labels': labels,
                                         'pages': pages}

      except Exception as ex:
        Logger.error(ex)
        err = traceback.format_exc().replace("\n", " ")
        Logger.error(err)

    # Classification
    classification_dic = {}
    # Contains per processed document - a list of identified pages with scores and document_class
    handle_classification_results(documents, classification_dic)

    # Prepare for extraction
    extraction_dic = {}
    # dictionary per processor name - list of uris to extract
    get_documents_for_extraction(classification_dic, extraction_dic)

    for parser in extraction_dic:
      extract_documents(extraction_dic[parser], parser)

    print("post_process_classify - Done!")

  return post_process_classify


def get_documents_for_extraction(classification_dic, extraction_dic):
  def add_extraction_item(doc_class, dic, uuid):
    parser_name = common.config.get_parser_name_by_doc_class(doc_class)
    if parser_name is None:
      Logger.error(
          f"Parser is unknown for document_class = {predicted_class}")
    if parser_name not in dic:
      dic[parser_name] = []
    dic[parser_name].append(uuid)

  # Get extraction Lists
  # Sample predictions Pages-based for single document with multiple pages that needs splitting:
  # {
  #   (1, 1): {'predicted_class': 'health_intake_form', 'predicted_score': 0.96},
  #   (3, 3): {'predicted_class': 'pa_form_cda', 'predicted_score': 0.99},
  #   (2, 2): {'predicted_class': 'pa_form_texas', 'predicted_score': 0.92},
  #   (0, 0): {'predicted_class': 'fax_cover_page', 'predicted_score': 0.91}
  #  }
  for uri in classification_dic:
    case_id, uid = get_id_from_file_path(uri)
    extraction_list = []
    # Splitting
    if len(classification_dic[uri]) > 1:
      # Document to be split according to the pages
      local_split_files = split_documents(classification_dic[uri], uri)
      for (f_local, predicted_class, predicted_score) in local_split_files:
        f_uid = upload_document(f_local, case_id)
        if f_uid is not None:
          update_classification_status(case_id=case_id, uid=f_uid,
                                       status=STATUS_SUCCESS,
                                       document_class=predicted_class,
                                       classification_score=predicted_score)
          add_extraction_item(predicted_class, extraction_dic, f_uid)

      update_classification_status(case_id, uid, STATUS_SPLIT,
                                   document_class=DOC_CLASS_SPLIT_DISPLAY_NAME,
                                   classification_score=0)
    elif len(classification_dic[uri]) == 1:
      predicted_class = \
        classification_dic[uri][list(classification_dic[uri].keys())[0]][
          "predicted_class"]
      predicted_score = \
        classification_dic[uri][list(classification_dic[uri].keys())[0]][
          "predicted_score"]
      update_classification_status(case_id=case_id, uid=uid,
                                   status=STATUS_SUCCESS,
                                   document_class=predicted_class,
                                   classification_score=predicted_score)

      add_extraction_item(predicted_class, extraction_dic, uid)


def handle_classification_results(documents, result):
  classification_confidence_threshold = get_classification_confidence_threshold()
  for uri in documents:
    # For each document get classification output -> the highest classified score
    result[uri] = {}

    # page-based approach => For each page find what is the highest predictions core for which class
    pages_set = set(documents[uri]["pages"])
    for unique_page in list(pages_set):
      if unique_page not in result[uri]:
        result[uri][unique_page] = {'predicted_class': None,
                                    'predicted_score': -1.0}
      for index, pages in enumerate(documents[uri]["pages"]):
        if pages == unique_page:
          if documents[uri]["scores"][index] > result[uri][unique_page]['predicted_score']:
            score = documents[uri]["scores"][index]
            result[uri][unique_page]['predicted_score'] = documents[uri]["scores"][index]
            predicted_label = documents[uri]["labels"][index]
            if score < classification_confidence_threshold:
                predicted_class = get_classification_default_class()
            else:
                predicted_class = get_document_class_by_classifier_label(predicted_label)
            result[uri][unique_page]['predicted_class'] = predicted_class



    # # Sample raw prediction_result for document that needs to be split:
    # { 'gs://ek-cda-engine-001-document-upload/7ce08d84-1086-11ee-9f25-b66184e8964f/JVkbJf7wLXqLrExC6oq1/Package-combined.pdf':
    #   {(1, 1): {'predicted_class': 'health_intake_form', 'predicted_score': 0.96 },
    #    (3, 3): {'predicted_class': 'pa_form_cda', 'predicted_score': 0.99 },
    #    (2, 2): {'predicted_class': 'pa_form_texas', 'predicted_score': 0.92 },
    #    (0, 0): {'predicted_class': 'fax_cover_page', 'predicted_score': 0.91 }}
    #  }

    # Classify -> no split required
    # { 'gs://ek-cda-engine-001-document-upload/12484e84-1087-11ee-aff9-b66184e8964f/dzJFf01wceSUqUokkYjf/pa-form-1.pdf':
    #    {(0, 4): {'predicted_class': 'pa_form_texas', 'predicted_score': 0.74}}
    #  }


def split_documents(document_info: Dict, gcs_url: str):
  output_dir = os.path.join(os.path.dirname(__file__), "temp_files",
                            "splitter_out")

  split_files = []

  pdf_path = os.path.join(output_dir, os.path.basename(gcs_url))
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)
  Logger.info(
      f"split using source file with file_path={gcs_url} and output_dir={output_dir}")

  # Split and save locally
  for pages in document_info:
    start, end = pages
    predicted_class = document_info[pages]["predicted_class"]
    predicted_score = document_info[pages]["predicted_score"]

    if start == end:
      page_range = f"pg{start + 1}"
    else:
      page_range = f"pg{start + 1}-{end + 1}"

    output_filename = os.path.join(
        output_dir,
        f"{page_range}_{predicted_class}_{os.path.basename(gcs_url)}")

    Logger.info(f"start = {start}, end = {end}, subdoc_type={predicted_class}, "
                f"page_range={page_range},"
                f" output_filename={output_filename}")

    try:
      Logger.info(f'Downloading from {gcs_url} to {pdf_path}')
      download_pdf_gcs(gcs_uri=gcs_url,
                       output_filename=pdf_path)
      with Pdf.open(pdf_path) as original_pdf:
        Logger.info(
            f"Creating: {output_filename} (confidence: {predicted_score})")
        Logger.info(f"original_pdf.pages={original_pdf.pages}")
        subdoc = Pdf.new()
        for page_num in range(start, end + 1):
          subdoc.pages.append(original_pdf.pages[page_num])

        if not os.path.exists(output_dir):
          os.mkdir(output_dir)

        subdoc.save(
            output_filename,
            min_version=original_pdf.pdf_version,
        )
        split_files.append((output_filename, predicted_class, predicted_score))

    except Exception as e:
      Logger.error(f"Error while splitting document {pdf_path}")
      Logger.error(e)
      print(e)

  return split_files
  # Upload to GCS storage
