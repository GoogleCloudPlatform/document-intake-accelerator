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
import sys
import time
from os.path import basename
from typing import Dict
from typing import List

import requests
from google.api_core.exceptions import InternalServerError
from google.api_core.exceptions import RetryError
from google.cloud import documentai_v1 as documentai
from google.cloud import storage
from pikepdf import Pdf

from common.config import BUCKET_NAME
from common.config import CLASSIFIER
from common.config import DOCUMENT_STATUS_API_PATH
from common.config import PDF_MIME_TYPE
from common.config import STATUS_SUCCESS
from common.config import get_classification_confidence_threshold
from common.config import get_classification_default_class
from common.config import get_document_class_by_classifier_label
from common.config import get_parser_config
from common.extraction_config import DOCAI_OUTPUT_BUCKET_NAME
from common.models import Document
from common.utils import helper
from common.utils.helper import get_processor_location
from common.utils.iap import send_iap_request
from common.utils.logging_handler import Logger
from .download_pdf_gcs import download_pdf_gcs

PDF_EXTENSION = ".pdf"

storage_client = storage.Client()
CLASSIFICATION_UNDETECTABLE = "unclassified"


class DocumentConfig:
  def __init__(self, case_id, uid, gcs_url, out_folder,
      context="california") -> None:
    if not gcs_url.endswith('pdf'):
      Logger.error('Invalid input file. Require PDF file')
      sys.exit()

    self.case_id = case_id
    self.uid = uid
    self.context = context

    self.pdf_path = f'{out_folder}/{case_id}_{uid}_' + basename(gcs_url)
    self.gcs_url = gcs_url


def get_classification_predictions(gcs_input_uris, timeout: int = 400):
  Logger.info("get_classification_predictions started")
  # read parser details from configuration json file
  parsers_info = get_parser_config()
  parser_details = parsers_info.get(CLASSIFIER, None)
  result = {}  # Contains per processed document
  if not parser_details:
    default_class = get_classification_default_class()
    Logger.warning(f"No classification parser defined, exiting classification, "
                 f"using {default_class}")
    for uri in gcs_input_uris:
      result[uri] = [{'predicted_class': default_class,
                      'predicted_score': 100,
                      'pages': None}]
    return result

  processor_path = parser_details["processor_id"]
  location = parser_details.get("location",
                                get_processor_location(processor_path))

  if not location:
    Logger.error(f"Unidentified location for parser {processor_path}")
    return {}

  opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}

  client = documentai.DocumentProcessorServiceClient(client_options=opts)

  input_documents = []
  for doc in gcs_input_uris:
    # Cloud Storage URI for the Input Document
    input_documents.append(
        documentai.GcsDocument(
            gcs_uri=doc, mime_type=PDF_MIME_TYPE
        )
    )
  # Load GCS Input URI into a List of document files
  input_config = documentai.BatchDocumentsInputConfig(
      gcs_documents=documentai.GcsDocuments(documents=input_documents)
  )
  # Cloud Storage URI for the Output Directory
  # This must end with a trailing forward slash `/`
  gcs_output_uri = f"gs://{DOCAI_OUTPUT_BUCKET_NAME}"

  timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S-%f")
  gcs_output_uri_prefix = "classifier_out_" + timestamp
  # temp folder location
  destination_uri = f"{gcs_output_uri}/{gcs_output_uri_prefix}/"

  gcs_output_config = documentai.DocumentOutputConfig.GcsOutputConfig(
      gcs_uri=os.path.join(destination_uri, "json")
  )
  output_config = documentai.DocumentOutputConfig(
      gcs_output_config=gcs_output_config)
  processor = client.get_processor(name=processor_path)
  processor_type = processor.type_
  Logger.info(f"get_classification_predictions - input_config = {input_config}")
  Logger.info(f"get_classification_predictions - output_config = {output_config}")
  Logger.info(
      f"get_classification_predictions - Calling DocAI API for {len(input_documents)} documents "
      f" using {processor.display_name} processor"
      f"type={processor.type_}, path={processor.name}")
  start = time.time()

  request = documentai.BatchProcessRequest(
      name=processor_path,
      input_documents=input_config,
      document_output_config=output_config,
  )

  # BatchProcess returns a Long Running Operation (LRO)
  operation = client.batch_process_documents(request)

  # Continually polls the operation until it is complete.
  # This could take some time for larger files
  # Format: projects/PROJECT_NUMBER/locations/LOCATION/operations/OPERATION_ID
  try:
    Logger.info(f"get_classification_predictions - Waiting for operation {operation.operation.name} to complete...")
    operation.result(timeout=timeout)
  # Catch exception when operation doesn't finish before timeout
  except (RetryError, InternalServerError) as e:
    Logger.error(e.message)
    Logger.error("Classification Failed to process documents")
    return {}

  elapsed = "{:.0f}".format(time.time() - start)
  Logger.info(f"get_classification_predictions - Elapsed time for operation {elapsed} seconds")

  # NOTE: Can also use callbacks for asynchronous processing
  #
  # def my_callback(future):
  #   result = future.result()
  #
  # operation.add_done_callback(my_callback)

  # Once the operation is complete,
  # get output document information from operation metadata
  metadata = documentai.BatchProcessMetadata(operation.metadata)

  if metadata.state != documentai.BatchProcessMetadata.State.SUCCEEDED:
    raise ValueError(f"Batch Process Failed: {metadata.state_message}")

  # One process per Input Document
  for process in metadata.individual_process_statuses:
    # output_gcs_destination format: gs://BUCKET/PREFIX/OPERATION_NUMBER/INPUT_FILE_NUMBER/
    # The Cloud Storage API requires the bucket name and URI prefix separately
    matches = re.match(r"gs://(.*?)/(.*)", process.output_gcs_destination)
    if not matches:
      Logger.warning(
          f"Could not parse output GCS destination:[{process.output_gcs_destination}]")
      continue

    output_bucket, output_prefix = matches.groups()
    output_gcs_destination = process.output_gcs_destination
    input_gcs_source = process.input_gcs_source
    Logger.info(
        f"output_bucket = {output_bucket}, output_prefix={output_prefix}, input_gcs_source = {input_gcs_source}, output_gcs_destination = {output_gcs_destination}")
    # Get List of Document Objects from the Output Bucket
    output_blobs = storage_client.list_blobs(output_bucket,
                                             prefix=output_prefix + "/")

    # Document AI may output multiple JSON files per source file
    # Todo find out what kind of information split will be in these multiple JSON documents output
    documents = {}
    for blob in output_blobs:
      # Document AI should only output JSON files to GCS
      if ".json" not in blob.name:
        Logger.info(
            f"Skipping non-supported file: {blob.name} - Mimetype: {blob.content_type}"
        )
        continue

      # Download JSON File as bytes object and convert to Document Object
      Logger.info(f"Fetching gs://{output_bucket}/{blob.name}")
      document = documentai.Document.from_json(
          blob.download_as_bytes(), ignore_unknown_fields=True
      )
      dirs, file_name = helper.split_uri_2_path_filename(input_gcs_source)
      Logger.info(f"batch_process_document dirs = {dirs}, file_name = {file_name}")
      Logger.info(
          f"batch_process_document in_bucket = {dirs}, blob_name = {file_name}")

      entities = document.entities

      if input_gcs_source in documents.keys():
        labels = documents[input_gcs_source].get('labels')
        scores = documents[input_gcs_source].get('scores')
        pages = documents[input_gcs_source].get('pages')
      else:
        labels = []
        scores = []
        pages = []

      for index, entity in enumerate(entities):
        # If Classifier, then pages are not returned
        if len(entity.page_anchor.page_refs) > 0:
          start = int(entity.page_anchor.page_refs[0].page)
          end = int(entity.page_anchor.page_refs[-1].page)
        else:
          start = 0
          end = document.pages[-1].page_number

        score = float('%.2f' % entity.confidence)
        label = entity.type_.replace("/", "_")

        scores.append(score)
        labels.append(label)
        pages.append((start, end))

        Logger.info(
            f"Classification result for {input_gcs_source}: document_class={label}, confidence={score}, start={start}, end={end}")

      documents[input_gcs_source] = {'scores': scores, 'labels': labels,
                                     'pages': pages}

      prediction_result = documents[input_gcs_source]
      result[input_gcs_source] = []
      if processor_type == 'CUSTOM_CLASSIFICATION_PROCESSOR':
        predicted_score = -1.0
        predicted_class = None
        pages = None

        for index, label in enumerate(prediction_result["labels"]):
          if prediction_result["scores"][index] > predicted_score:
            predicted_score = prediction_result["scores"][index]
            pages = prediction_result["pages"][index]
            predicted_class = get_document_class_by_classifier_label(label)
        result[input_gcs_source] = [{'predicted_class': predicted_class,
                                     'predicted_score': predicted_score,
                                     'pages': pages}]
      elif processor_type == 'CUSTOM_SPLITTING_PROCESSOR':
        Logger.info(f"Total subdocuments: {len(entities)}")
        for index, label in enumerate(prediction_result["labels"]):
          predicted_score = prediction_result["scores"][index]
          pages = prediction_result["pages"][index]
          predicted_class = get_document_class_by_classifier_label(label)
          result[input_gcs_source].append({'predicted_class': predicted_class,
                                           'predicted_score': predicted_score,
                                           'pages': pages})

  Logger.info(f"get_classification_predictions completed with result={result}")
  # # Sample raw prediction_result
  # # {'scores': [0.0136728594, 0.0222843271, 0.908525527, 0.0222843271, 0.0332329459], 'labels': ['PayStub', 'Utility', 'UE', 'Claim', 'DL'],
  # 'key': '/opt/routes/temp_files/06_09_2022_01_59_10_temp_files\\7f2ec4ee-2d87-11ed-a71c-c2c2b7b788a8_7FvQ5G3dddti02sHbBhK_arizona-application-form_0.png'}
  # prediction = {'scores': scores, 'labels': labels}
  return result


def split_upload(documents: List[Dict], config: DocumentConfig):
  for doc in documents:
    local_path = split(doc, config)
    file_name = os.path.basename(local_path)
    Logger.info(
        f"split_upload using local_path={local_path}, case_id={config.case_id}")
    if local_path is None:
      Logger.error(f"Error, {local_path} is not set, exiting.")
      return

    # Create record in Firestore
    uid = create_document(config.case_id, file_name, config.context)
    if uid is None:
      Logger.error(f"split_upload: Failed to create document {file_name}")
      return
    else:
      Logger.info(f"split_upload: Succeeded to create document {file_name}")
      doc["uid"] = uid
      file_uri = f"{config.case_id}/{uid}/{file_name}"
      gsc_uri = f"gs://{BUCKET_NAME}/{file_uri}"
      doc["gcs_url"] = gsc_uri
      helper.upload_to_gcs(local_path, file_uri, BUCKET_NAME)
      Logger.info(
          f"split_upload:  File {file_name} with case_id {config.case_id} and uid {uid}"
          f" uploaded successfully in GCS bucket = {gsc_uri}")

      # remove the blob from local after prediction as it is of no use further
      os.remove(local_path)

      # Update the document upload as success in DB
      document = Document.find_by_uid(uid)
      if document is not None:
        document.url = gsc_uri
        system_status = {
            "stage": "uploaded",
            "status": STATUS_SUCCESS,
            "timestamp": datetime.datetime.utcnow(),
            "comment": "Created by Splitter"
        }
        document.system_status = [system_status]
        document.update()


      else:
        Logger.error(f"split_upload: Could not retrieve document by id {uid}")
        return


def split(doc_prediction: Dict, config: DocumentConfig):
  output_dir = os.path.join(os.path.dirname(__file__), "temp_files",
                            "splitter_out")
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)
  Logger.info(
      f"split using source file with file_path={config.gcs_url} and output_dir={output_dir}")

  # Split and save locally
  start, end = doc_prediction["pages"]
  subdoc_type = doc_prediction["predicted_class"]
  confidence = doc_prediction["predicted_score"]
  if start == end:
    page_range = f"pg{start + 1}"
  else:
    page_range = f"pg{start + 1}-{end + 1}"

  output_filename = os.path.join(
      output_dir,
      f"{page_range}_{subdoc_type}_{os.path.basename(config.gcs_url)}")

  Logger.info(f"start = {start}, end = {end}, subdoc_type={subdoc_type}, "
              f"page_range={page_range},"
              f" output_filename={output_filename}")

  try:
    Logger.info(f'Downloading from {config.gcs_url} to {config.pdf_path}')
    blob = download_pdf_gcs(gcs_uri=config.gcs_url, output_filename=config.pdf_path)
    with Pdf.open(config.pdf_path) as original_pdf:
      Logger.info(f"Creating: {output_filename} (confidence: {confidence})")
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
      return output_filename
  except Exception as e:
    Logger.error(f"Error while splitting document {config.pdf_path}")
    Logger.error(e)
    print(e)
    return None

  # Upload to GCS storage


def classify(configs: List[DocumentConfig]):
  """
  Run splitting and classification job

  Args:
  gcs_input_uris (list): Document uris to classify.

  Returns:
      JSON: json object
  """

  try:
    Logger.info(f"classify - Running Classification prediction using {configs}")
    classification_threshold = get_classification_confidence_threshold()

    gcs_input_uris = [config.gcs_url for config in configs]
    prediction_results = get_classification_predictions(gcs_input_uris)

    Logger.info(f"prediction_results = {prediction_results}")

    if prediction_results is None:
      return None

    result = {}
    for gcs_url in prediction_results.keys():
      prediction_result = prediction_results[gcs_url]
      config = next((x for x in configs if x.gcs_url == gcs_url), None)
      if config is None:
        print(
          f"Error, cannot find document config with {gcs_url} in the list of configs {configs}")
        continue

      Logger.info(f"Classification prediction for {gcs_url}: "
                  f"case_id={config.case_id}, "
                  f"uid={config.uid}  - {prediction_result}")

      # [{'predicted_class': predicted_class, 'model_conf': predicted_score, 'pages': pages}]
      # # Sample raw prediction_result
      # # {'scores': [0.0136728594, 0.0222843271, 0.908525527, 0.0222843271, 0.0332329459], 'labels': ['PayStub', 'Utility', 'UE', 'Claim', 'DL'], 'key': '/opt/routes/temp_files/06_09_2022_01_59_10_temp_files\\7f2ec4ee-2d87-11ed-a71c-c2c2b7b788a8_7FvQ5G3dddti02sHbBhK_arizona-application-form_0.png'}

      # If multiple documents => need to split and upload
      if len(prediction_result) > 1:
        split_upload(prediction_result, config)

      for predicted_doc in prediction_result:
        predicted_class = predicted_doc['predicted_class']
        predicted_score = predicted_doc['predicted_score']

        if predicted_score < classification_threshold:
          predicted_class = get_classification_default_class()
          Logger.warning(
              f"Classification prediction results: score={predicted_score} "
              f" does not pass classification threshold={classification_threshold}."
              f" Falling back on default type={predicted_class}")

        output = {
            'case_id': config.case_id,
            'uid': predicted_doc.get("uid", config.uid),
            'gcs_url': predicted_doc.get("gcs_url", config.gcs_url),
            'predicted_class': predicted_class,
            'model_conf': predicted_score
        }
        Logger.info(f"Classification prediction results for {gcs_url}: "
                    f"{output}")

        if gcs_url not in result.keys():
          result[gcs_url] = []

        result[gcs_url].append(output)

    Logger.info(
      f"classify - Classification prediction completed with {json.dumps(result)}")
    return json.dumps(result)

  except Exception as e:
    Logger.error(
        f"Error while getting predictions from classifier")
    Logger.error(e)
    print(e)
    return None


def create_document(case_id, filename, context, user=None):
  uid = None
  try:
    Logger.info(
        f"create_document: with case_id = {case_id} filename = {filename} context = {context}")
    req_url = f"document-status-service/{DOCUMENT_STATUS_API_PATH}/create_document".replace(
        "//", "/")
    url = f"http://{req_url}?case_id={case_id}&filename={filename}&context={context}&user={user}"
    Logger.info(f"create_document: posting request to {url}")
    response = send_iap_request(url, method="POST")
    response = response.json()
    uid = response.get("uid")
    Logger.info(f"create_document: Response received ={response}, uid={uid}")
  except requests.exceptions.RequestException as err:
    Logger.error(err)

  return uid
