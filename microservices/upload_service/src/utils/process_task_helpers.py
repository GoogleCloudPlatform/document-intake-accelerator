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
from common.config import STATUS_IN_PROGRESS, STATUS_SUCCESS, STATUS_ERROR, CLASSIFICATION_UNDETECTABLE


def run_pipeline(payload: List[Dict], is_hitl: bool, is_reassign: bool):
  """Runs the entire pipeline
    Args:
    payload (ProcessTask): Consist of configs required to run the pipeline
    is_hitl : It is used to run the pipeline for unclassified documents
    is_reassign : It is used to run the pipeline for reassigned document
  """
  Logger.info(f"Processing the documents: {payload}")
  print(f"Processing the documents: {payload}")

  extraction_score = None
  applications = []
  supporting_docs = []

  # For unclassified or reassigned documents set the doc_class
  if is_hitl or is_reassign:
    result = get_documents(payload)
    applications = result[0]
    supporting_docs = result[1]
  # for other cases like normal flow classify the documents
  elif not is_reassign:
    result = filter_documents(payload.get("configs"))
    applications = result[0]
    supporting_docs = result[1]

  Logger.info(f"run_pipeline with applications = {applications}")
  Logger.info(f"run_pipeline with supporting_docs = {supporting_docs}")
  # for normal flow and for hitl run the extraction of documents
  if is_hitl or applications or supporting_docs:
    # extract the application first
    if applications:
      for doc in applications:
        try:
          extraction_score = extract_documents(
              doc, document_type="application_form")
        except Exception as e:
          Logger.error(e)
          err = traceback.format_exc().replace("\n", " ")
          Logger.error(err)

    # extract,validate and match supporting documents
    if supporting_docs:
      # Todo Extract in Batches
      for doc in supporting_docs:
        # In case of reassign extraction is not required
        try:
          if not is_reassign:
            extraction_output = extract_documents(
                doc, document_type="supporting_documents")
            extraction_score = extraction_output[0]
            extraction_field_min_score = extraction_output[1]
            extraction_entities = extraction_output[2]
            Logger.info(f" Executing pipeline for normal scenario {doc}")
            if extraction_score is not None and extraction_entities:
              Logger.info(f"extraction score is {extraction_score},{doc}")
              validate_match_approve(doc, extraction_score, extraction_field_min_score, extraction_entities)
          else:
            Logger.info(f" Executing pipeline for reassign scenario "
                        f"{doc}")
            extraction_score = doc["extraction_score"]
            extraction_entities = doc["extraction_entities"]
            extraction_field_min_score = None # Todo calculate the field value
            validate_match_approve(doc, extraction_score, extraction_field_min_score, extraction_entities)
        except Exception as e:
          Logger.error(e)
          err = traceback.format_exc().replace("\n", " ")
          Logger.error(err)
          # Not raising exception, because other documents in the batch might still suceed
          # raise HTTPException(status_code=500, detail=e) from e


def get_classification(case_id: str, uid: str, gcs_url: str):
  """Call the classification API and get the type and class of
  the document"""
  base_url = "http://classification-service/classification_service/v1/"\
    "classification/classification_api"
  req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
    f"&gcs_url={gcs_url}"
  response = requests.post(req_url)
  return response


def get_extraction_score(case_id: str, uid: str, document_class: str,
                         document_type: str, context: str, gcs_url: str):
  """Call the Extraction API and get the extraction score"""
  base_url = "http://extraction-service/extraction_service/v1/extraction_api"
  req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
    f"&doc_class={document_class}&document_type={document_type}" \
            f"&context={context}&gcs_url={gcs_url}"
  response = requests.post(req_url)
  return response


def get_validation_score(case_id: str, uid: str, document_class: str,
                         extraction_entities: List[Dict]):
  """Call the validation API and get the validation score"""
  base_url = "http://validation-service/validation_service/v1/validation/"\
    "validation_api"
  req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
    f"&doc_class={document_class}"
  response = requests.post(req_url, json=extraction_entities)
  return response


def get_matching_score(case_id: str, uid: str):
  """Call the matching API and get the matching score"""
  base_url = "http://matching-service/matching_service/v1/"\
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
    f"&status={a_status}&autoapproved_status={autoapproved_status}"\
    f"&is_autoapproved={is_autoapproved}"
  response = requests.post(req_url)
  return response


def filter_documents(configs: List[Dict]):
  """Filter the supporting documents and application form"""
  print("filter_documents")
  print(configs)

  supporting_docs = []
  application_form = []
  for config in configs:
    case_id = config.get("case_id")
    uid = config.get("uid")
    gcs_url = config.get("gcs_url")
    cl_result = get_classification(case_id, uid, gcs_url)
    print(f"Processing  document with uid={uid} gcs_url={gcs_url} case_id={case_id}")
    print(f"status_code={cl_result.status_code}, json={cl_result.json()}")
    if cl_result.status_code == 200:
      document_type = cl_result.json().get("doc_type")
      document_class = cl_result.json().get("doc_class")

      Logger.info(
          f"Classification for {uid}:document_type:{document_type},\
      document_class:{document_class}.")

      if document_class == CLASSIFICATION_UNDETECTABLE:
        Logger.warning(f"Skipping extraction for unclassified document  {uid} ")
        continue

      if document_type == "application_form":
        config["document_class"] = document_class
        application_form.append(config)
      elif document_type == "supporting_documents":
        config["document_class"] = document_class
        supporting_docs.append(config)
    else:
      Logger.error(f"Classification FAILED for document with uid={uid} gcs_url={gcs_url} case_id={case_id}")
  print(
      f"Application form:{application_form} and"\
      f" supporting_docs:{supporting_docs}")
  Logger.info(
      f"Application form:{application_form} and "\
        f"supporting_docs:{supporting_docs}")
  return application_form, supporting_docs


def extract_documents(doc: Dict, document_type):
  """Perform extraction for application or supporting documents"""
  extraction_score = None
  extraction_entities = None
  extraction_field_min_score = None
  case_id = doc.get("case_id")
  uid = doc.get("uid")
  document_class = doc.get("document_class")
  context = doc.get("context")
  gcs_url = doc.get("gcs_url")
  Logger.info(f"extract_documents with case_id={case_id}, uid={uid}, "
              f"document_class={document_class}, document_type={document_type}, "
              f"context={context}, gcs_url={gcs_url}")
  extract_res = get_extraction_score(case_id, uid, document_class,
                                     document_type, context, gcs_url)

  if extract_res.status_code == 200:
    Logger.info(f"Extraction successful for {document_type}\
       case_id: {case_id} uid:{uid}")
    extraction_score = extract_res.json().get("score")
    extraction_field_min_score = extract_res.json().get("extraction_field_min_score")
    extraction_entities = extract_res.json().get("entities")

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
  else:
    Logger.error(f"extraction failed for {document_type} {document_class} case_id={case_id} uid={uid}")
  # extraction_score = None
  return extraction_score, extraction_field_min_score, extraction_entities


def validate_match_approve(sup_doc: Dict, extraction_score, min_extraction_score_per_field,
                           extraction_entities):
  """Perform validation, matching and autoapproval for supporting documents"""
  validation_score = None
  matching_score = None
  case_id = sup_doc.get("case_id")
  uid = sup_doc.get("uid")
  document_class = sup_doc.get("document_class")
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
                          validation_score, extraction_score, min_extraction_score_per_field, matching_score)
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
