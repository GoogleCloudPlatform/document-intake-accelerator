""" Process task api endpoint """
import traceback
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from fastapi.concurrency import run_in_threadpool
from common.models import Document
import requests
# pylint: disable = ungrouped-imports
from common.utils.logging_handler import Logger
from common.utils.autoapproval import get_values
from typing import List, Dict

# pylint: disable = broad-except

router = APIRouter()
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}

def run_pipeline(payload: List[Dict], is_hitl: bool=False):
  validation_score = None
  extraction_score = None
  matching_score = None
  applications = []
  supporting_docs = []
  if is_hitl:
    document_type = payload.get("configs")[0].get("document_type")
    if document_type == "application_form":
      apps = payload.get("configs")[0]
      applications.append(apps)
    elif document_type == "supporting_documents":
      supporting_docs.append(payload.get("configs")[0])
    print(
      f"is_hitl: {is_hitl} Application form: {applications}\
         and supporting_docs:{supporting_docs}")
    Logger.info(
      f"Application form:{applications} and supporting_docs:{supporting_docs}")

  try:
    if not is_hitl:
      result = filter_documents(payload.get("configs"))
      applications = result[0]
      supporting_docs = result[1]
      print(
        f"Application form:{applications} and supporting_docs:{supporting_docs}")
      Logger.info(
        f"Application form:{applications} and supporting_docs:{supporting_docs}")

    if is_hitl or applications or supporting_docs:
      for app in applications:
        case_id = app.get("case_id")
        uid = app.get("uid")
        document_class = app.get("document_class")
        document_type = "application_form"
        extract_res = get_extraction_score(case_id, uid, document_class)
        Logger.info("Extraction successful for application_form.")
        extraction_score = extract_res.json().get("score")
        autoapproval_status = get_values(
          validation_score, extraction_score, matching_score,
          document_class, document_type)
        Logger.info(
          f"autoapproval_status for application:{autoapproval_status}")
        update_autoapproval_status(
          case_id, uid, "success", autoapproval_status[0], "yes")

      for sup_doc in supporting_docs:
        case_id = sup_doc.get("case_id")
        uid = sup_doc.get("uid")
        document_class = sup_doc.get("document_class")
        document_type = "supporting_documents"
        extract_res = get_extraction_score(case_id, uid, document_class)
        if extract_res.status_code == 200:
          Logger.info(
            "Extraction successful for supporting_documents.")
          extraction_score = extract_res.json().get("score")
          validation_res = get_validation_score(
            case_id, uid, document_class)
          if validation_res.status_code == 200:
            print("====Validation successful==========")
            Logger.info("Validation successful.")
            validation_score = validation_res.json().get("score")
            matching_res = get_matching_score(case_id, uid)
            if matching_res.status_code == 200:
              print("====Matching successful==========")
              Logger.info("Matching successful.")
              matching_score = matching_res.json().get("score")
              autoapproval_status = get_values(
                validation_score, extraction_score, matching_score,
                document_class, document_type)
              Logger.info(
                f"autoapproval_status:{autoapproval_status}")
              update_autoapproval_status(
                case_id, uid, "success", autoapproval_status[0], "yes")
            else:
              err = traceback.format_exc().replace("\n", " ")
              Logger.error(err)
              Logger.error(f"Matching FAILED for {uid}")
          else:
            err = traceback.format_exc().replace("\n", " ")
            Logger.error(err)
            Logger.error(f"Validation FAILED for {uid}")
        else:
          err = traceback.format_exc().replace("\n", " ")
          Logger.error(err)
          Logger.error(f"Extraction FAILED for {uid}")

      Logger.info("Process task executed SUCCESSFULLY.")
  except Exception as e:
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(status_code=500, detail=e) from e


def get_classification(case_id: str, uid: str, gcs_url: str):
  """Call the classification API and get the type and class of
  the document"""
  base_url = "http://classification-service/classification_service/v1/"\
    "classification/classification_api"
  req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
    f"&gcs_url={gcs_url}"
  response = requests.post(req_url)
  return response


def get_extraction_score(case_id: str, uid: str, document_class: str):
  """Call the Extraction API and get the extraction score"""
  base_url = "http://extraction-service/extraction_service/v1/extraction_api"
  req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
    f"&doc_class={document_class}"
  response = requests.post(req_url)
  return response


def get_validation_score(case_id: str, uid: str, document_class: str):
  """Call the validation API and get the validation score"""
  base_url = "http://validation-service/validation_service/v1/validation/"\
    "validation_api"
  req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
    f"&doc_class={document_class}"
  response = requests.post(req_url)
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


def get_document(case_id: str, uid: str):
  """Get the document with given uid and case_id"""
  doc = Document.collection.filter(
    "case_id", "==", case_id).filter("uid", "==", uid).get()
  return doc


def filter_documents(configs: List[Dict]):
  """Filters the supporting documents and application form"""
  supporting_docs = []
  application_form = []
  for config in configs:
    case_id = config.get("case_id")
    uid = config.get("uid")
    gcs_url = config.get("gcs_url")
    cl_result = get_classification(case_id, uid, gcs_url)
    if cl_result.status_code == 200:
      document_type = cl_result.json().get("doc_type")
      document_class = cl_result.json().get("doc_class")
      Logger.info(
        f"Classification successful for {uid}:document_type:{document_type},\
      document_class:{document_class}.")

      if document_type == "application_form":
        config["document_class"] = document_class
        application_form.append(config)
      elif document_type == "supporting_documents":
        config["document_class"] = document_class
        supporting_docs.append(config)
    else:
      err = traceback.format_exc().replace("\n", " ")
      Logger.error(err)
      Logger.error(f"Validation FAILED for {uid}")
  return application_form, supporting_docs
