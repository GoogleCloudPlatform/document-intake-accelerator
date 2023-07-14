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

"""Helper functions to execute the pipeline"""
from typing import Dict
from typing import List

import requests

from common.config import get_parser_name_by_doc_class
from common.utils.api_calls import extract_documents
from common.utils.logging_handler import Logger


def sort_per_doc_class(docs):
  document_class_list = set([doc["document_class"] for doc in docs])
  doc_sorted_dic = {}
  for doc_class in document_class_list:
    doc_sorted_dic[doc_class] = [doc for doc in docs if doc["document_class"]
                                 == doc_class]

  Logger.info(f"sort_per_doc_class doc_sorted_dic={doc_sorted_dic} ")
  return doc_sorted_dic


def run_pipeline(payload: Dict, is_hitl: bool, is_reassign: bool):
  """Runs the entire pipeline
    Args:
    payload (ProcessTask): Consist of configs required to run the pipeline
    is_hitl : It is used to run the pipeline for unclassified documents
    is_reassign : It is used to run the pipeline for reassigned document
  """
  # For unclassified or reassigned documents set the doc_class
  if is_hitl:
    Logger.info(f"run_pipeline with payload = {payload}")
    documents = payload.get("configs")
    Logger.info(f"run_pipeline with documents = {documents}")
    for doc in documents:
      uid = doc.get("uid")
      doc_class = doc["document_class"]
      parser_name = get_parser_name_by_doc_class(doc_class)
      extract_documents([uid], parser_name)
  # for other cases like normal flow classify the documents
  elif is_reassign:
    documents = payload.get("configs")[0]
    Logger.info(f"run_pipeline with documents = {documents}")
    for doc in documents:
      Logger.info(f"Executing pipeline for reassign/hitl scenario "
                  f"{doc}")
      # Todo re-assign scenario is broken and not in use
      # extraction_score = doc["extraction_score"]
      # extraction_entities = doc["extraction_entities"]
      # extraction_field_min_score = None  # Todo calculate the field value
      # process_extraction_result_helper.validate_match_approve(doc["case_id"],
      #                                                         doc["uid"],
      #                                                         extraction_score,
      #                                                         extraction_field_min_score,
      #                                                         extraction_entities,
      #                                                         doc[
      #                                                           "document_class"])
  else:
    classify_documents(payload.get("configs"))


def send_classification_request(configs: List[Dict]):
  """Call the classification API and get the type and class of
  the document"""
  try:
    base_url = "http://classification-service/classification_service/v1/" \
               "classification/classification_api"
    payload = {"configs": configs}
    Logger.info(
      f"get_classification sending to {base_url} with payload={payload}")
    response = requests.post(base_url, json=payload)
    Logger.info(f"get_classification response {response}")
    return response
  except requests.exceptions.RequestException as err:
    Logger.error(err)


def classify_documents(configs: List[Dict]):
  Logger.info(f"classify_documents with configs = {configs}")

  cl_result = send_classification_request(configs)

  if cl_result and cl_result.status_code == 200:
    Logger.info(f"classify_documents - response received {cl_result}")
  else:
    Logger.error(
        f"classify_documents: Classification FAILED")
