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
import requests
import traceback
from fastapi import HTTPException
from common.utils.logging_handler import Logger

from utils.autoapproval import get_autoapproval_status
from typing import List, Dict
from common.config import STATUS_IN_PROGRESS, STATUS_SUCCESS, STATUS_ERROR, \
  CLASSIFICATION_UNDETECTABLE


def sort_per_doc_class(docs):
  document_class_list = set([doc["document_class"] for doc in docs])
  doc_sorted_dic = {}
  for doc_class in document_class_list:
    doc_sorted_dic[doc_class] = [doc for doc in docs if doc["document_class"]
                                 == doc_class]

  Logger.info(f"sort_per_doc_class doc_sorted_dic={doc_sorted_dic} ")
  return doc_sorted_dic


def run_pipeline(payload: List[Dict], is_hitl: bool, is_reassign: bool):
  """Runs the entire pipeline
    Args:
    payload (ProcessTask): Consist of configs required to run the pipeline
    is_hitl : It is used to run the pipeline for unclassified documents
    is_reassign : It is used to run the pipeline for reassigned document
  """
  applications = []
  supporting_docs = []

  # For unclassified or reassigned documents set the doc_class
  if is_hitl or is_reassign:
    result = get_documents(payload)
    applications = result[0]
    supporting_docs = result[1]
  # for other cases like normal flow classify the documents
  elif not is_reassign:
    result = classify_documents(payload.get("configs"))
    applications = result[0]
    supporting_docs = result[1]

  Logger.info(f"run_pipeline with applications = {applications}, "
              f"supporting_docs = {supporting_docs}")

  # for normal flow and for hitl run the extraction of documents
  if is_hitl or applications or supporting_docs:
      # extract the application first
      if applications:
        applications_dict = sort_per_doc_class(applications)
        for document_class in applications_dict:
          # get a list of uid to send
          docs_list = applications_dict[document_class]
          try:
            Logger.info(f"run_pipeline for document_class={document_class}, "
                        f"applications_dict={applications_dict}")
            extract_documents(docs=docs_list,
                              document_class=document_class,
                              document_type="application_form")
          except Exception as e:
            Logger.error(e)
            err = traceback.format_exc().replace("\n", " ")
            Logger.error(err)

      # extract,validate and match supporting documents
      if supporting_docs:
        if not is_reassign:
          supporting_docs_dict = sort_per_doc_class(supporting_docs)
          Logger.info(f"run_pipeline with  {len(supporting_docs_dict)} documents")
          for document_class in supporting_docs_dict:
            # get a list of uid to send
            docs_list = supporting_docs_dict[document_class]
            try:
              Logger.info(f"run_pipeline for document_class={document_class}, "
                          f"supporting_docs_dict={supporting_docs_dict}")
              extract_documents(docs=docs_list,
                                document_class=document_class,
                                document_type="supporting_documents")
            except Exception as e:
              Logger.error(f"Error while handling {document_class}: {e}")
              err = traceback.format_exc().replace("\n", " ")
              Logger.error(err)

        else:             # In case of reassign extraction is not required
          for doc in supporting_docs:
            Logger.info(f"Executing pipeline for reassign scenario "
                        f"{doc}")
            extraction_score = doc["extraction_score"]
            extraction_entities = doc["extraction_entities"]
            extraction_field_min_score = None  # Todo calculate the field value
            validate_match_approve(doc["case_id"], doc["uid"], extraction_score,
                                   extraction_field_min_score,
                                   extraction_entities, doc["document_class"])


def get_classification(configs: List[Dict]):
  """Call the classification API and get the type and class of
  the document"""
  base_url = "http://classification-service/classification_service/v1/" \
             "classification/classification_api"
  payload = {"configs": configs}
  Logger.info(f"get_classification sending to {base_url} with payload={payload}")
  response = requests.post(base_url, json=payload)
  Logger.info(f"get_classification response {response}")
  return response


def get_extraction_score(configs: List[Dict], doc_class):
  """Call the Extraction API and get the extraction score"""
  base_url = "http://extraction-service/extraction_service/v1/extraction_api"
  uids = []
  Logger.info(f"get_extraction_score - Received  {len(configs)} configs.")
  for config in configs:
    uids.append(config["uid"])
  uids = sorted(set(uids))
  configs_new = []
  Logger.info(f"get_extraction_score with uids = {uids}, doc_class = {doc_class}")
  for uid in uids:
    config = {"uid": uid}
    configs_new.append(config)
  payload = {"configs": configs_new, "doc_class": doc_class}
  Logger.info(f"get_extraction_score sending to base_url={base_url}, payload={payload}")
  response = requests.post(base_url, json=payload)
  Logger.info(f"get_extraction_score response {response}")
  return response


def get_validation_score(case_id: str, uid: str, document_class: str,
    extraction_entities: List[Dict]):
  """Call the validation API and get the validation score"""
  base_url = "http://validation-service/validation_service/v1/validation/" \
             "validation_api"
  req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
            f"&doc_class={document_class}"
  response = requests.post(req_url, json=extraction_entities)
  return response


def get_matching_score(case_id: str, uid: str):
  """Call the matching API and get the matching score"""
  base_url = "http://matching-service/matching_service/v1/" \
             "match_document"
  req_url = f"{base_url}?case_id={case_id}&uid={uid}"
  response = requests.post(req_url)
  return response


def update_autoapproval_status(case_id: str, uid: str, a_status: str,
    autoapproved_status: str, is_autoapproved: str):
  """Update auto approval status"""
  base_url = "http://document-status-service/document_status_service" \
             "/v1/update_autoapproved_status"
  req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
            f"&status={a_status}&autoapproved_status={autoapproved_status}" \
            f"&is_autoapproved={is_autoapproved}"
  response = requests.post(req_url)
  return response


def classify_documents(configs: List[Dict]):
  """Filter the supporting documents and application form"""
  print(f"classify_documents with configs = {configs}")

  supporting_docs = []
  application_form = []

  cl_result = get_classification(configs)
  Logger.info(
      f"classify_documents - status_code={cl_result.status_code}, "
      f"json={cl_result.json()}")

  # for config in configs:
  #   case_id = config.get("case_id")
  #   uid = config.get("uid")
  #   gcs_url = config.get("gcs_url")
  #
  #   Logger.info(
  #     f"classify_documents - Processing classification results for document with uid={uid}, "
  #     f"gcs_url={gcs_url}, "
  #     f"case_id={case_id}")

  if cl_result.status_code == 200:
    results = cl_result.json().get("results")
    Logger.info(f"classify_documents - results={results}")
    for result in results:
      case_id = result.get("case_id")
      document_type = result.get("doc_type")
      document_class = result.get("doc_class")
      document_uid = result.get("uid")
      document_url = result.get("gcs_url")
      doc = {"case_id": case_id,
             "uid": document_uid,
             "document_class": document_class,
             "context": "california", #TODO
             "gcs_url": document_url,
             }
      Logger.info(
          f"classify_documents: Classification returned {doc}.")

      if document_class == CLASSIFICATION_UNDETECTABLE:
        Logger.warning(
          f"classify_documents: Skipping extraction for unclassified document  {document_uid} ")
        continue

      if document_type == "application_form":
        application_form.append(doc)
      elif document_type == "supporting_documents":
        supporting_docs.append(doc)
  else:
    Logger.error(
      f"classify_documents: Classification FAILED")
  Logger.info(
      f"classify_documents:  Application form={application_form} and "
      f"supporting_docs={supporting_docs}")
  return application_form, supporting_docs


def extract_documents(docs: List[Dict], document_class, document_type):
  """Perform extraction for application or supporting documents"""
  extraction_score = None
  extraction_entities = None
  extraction_field_min_score = None
  Logger.info(f"extract_documents with {len(docs)}  documents docs={docs}, "
              f"document_class={document_class}, document_type={document_type}")
  extr_result = get_extraction_score(docs, document_class)

  if extr_result.status_code == 200:
    results = extr_result.json().get("results")
    for result in results:
      Logger.info(f"extract_documents: Handling result={result}")
      document_type = result.get("doc_type")
      document_class = result.get("doc_class")
      uid = result.get("uid")
      extraction_score = result.get("score")
      case_id = result.get("case_id")
      extraction_field_min_score = result.get(
          "extraction_field_min_score")
      extraction_entities = result.get("entities")
      doc = {

      }
      # if document is application form then update autoapproval status
      if document_type == "application_form":
        autoapproval_status = get_autoapproval_status(None, extraction_score,
                                                      extraction_field_min_score,
                                                      None, document_class,
                                                      document_type)
        Logger.info(f"autoapproval_status for application:{autoapproval_status}")
        if autoapproval_status is not None:
          update_autoapproval_status(case_id, uid, STATUS_SUCCESS,
                                     autoapproval_status[0], "yes")
      elif document_type == "supporting_documents":
        Logger.info(f" Executing pipeline for normal scenario {doc}")
        if extraction_score is not None:
          Logger.info(f"extraction score is {extraction_score}, {doc}")
          validate_match_approve(case_id, uid, extraction_score,
                                 extraction_field_min_score,
                                 extraction_entities, document_class)

  else:
    Logger.error(
      f"extraction failed for"
      f"document_type={document_type} document_class={document_class}")
  # extraction_score = None
  return extraction_score, extraction_field_min_score, extraction_entities


def validate_match_approve(case_id, uid, extraction_score,
    min_extraction_score_per_field,
    extraction_entities, document_class):
  """Perform validation, matching and autoapproval for supporting documents"""
  validation_score = None
  matching_score = None
  document_type = "supporting_documents"
  validation_res = get_validation_score(case_id, uid, document_class,
                                        extraction_entities)
  if validation_res.status_code == 200:
    print("====Validation successful==========")
    Logger.info(f"Validation successful for case_id: {case_id} uid:{uid}.")
    validation_score = validation_res.json().get("score")
    matching_res = get_matching_score(case_id, uid)
    if matching_res.status_code == 200:
      print("====Matching successful==========")
      Logger.info(f"Matching successful for case_id: {case_id} uid:{uid}.")
      matching_score = matching_res.json().get("score")
      update_autoapproval(document_class, document_type, case_id, uid,
                          validation_score, extraction_score,
                          min_extraction_score_per_field, matching_score)
    else:
      Logger.error(f"Matching FAILED for case_id: {case_id} uid:{uid}")
  else:
    Logger.error(f"Validation FAILED for case_id: {case_id} uid:{uid}")
  return validation_score, matching_score


def update_autoapproval(document_class,
    document_type,
    case_id,
    uid,
    validation_score=None,
    extraction_score=None,
    min_extraction_score_per_field=None,
    matching_score=None):
  """Get the autoapproval status and update."""
  autoapproval_status = get_autoapproval_status(validation_score,
                                                extraction_score,
                                                min_extraction_score_per_field,
                                                matching_score, document_class,
                                                document_type)
  Logger.info(f"autoapproval_status for application:{autoapproval_status}\
      for case_id: {case_id} uid:{uid}")
  update_autoapproval_status(case_id, uid, STATUS_SUCCESS,
                             autoapproval_status[0], "yes")


def get_documents(payload: List[Dict]):
  """Filter documents for unclassified or reassigned case"""
  applications = []
  supporting_docs = []
  document_type = payload.get("configs")[0].get("document_type")
  if document_type == "application_form":
    apps = payload.get("configs")[0]
    applications.append(apps)
  elif document_type == "supporting_documents":
    supporting_docs.append(payload.get("configs")[0])
  print(f"Unclassified/Reassigned flow: Application form: {applications}\
       and supporting_docs:{supporting_docs}")
  Logger.info(f"Unclassified/Reassigned flow: Application form:{applications}\
       and supporting_docs:{supporting_docs}")

  return applications, supporting_docs
