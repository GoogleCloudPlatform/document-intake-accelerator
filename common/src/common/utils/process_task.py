""" Process task api endpoint """
import traceback
import time
from urllib import response
from fastapi import APIRouter, HTTPException, BackgroundTasks, Response, status
from fastapi.concurrency import run_in_threadpool
from typing import Optional, List
from common.models import Document
import requests
from common.utils.logging_handler import Logger
from common.utils.autoapproval import get_values


# pylint: disable = broad-except
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}
def run_pipeline(case_id: str, uid: str, gcs_url: str, isHitl: bool = False
, document_class: str = "", document_type: str = ""):
  validation_score = None
  extraction_score = None
  matching_score = None
  try:
    if not isHitl:
      cl_result = get_classification(case_id, uid, gcs_url)
      print("====================classification_status===================",
          cl_result.json(), cl_result.status_code)
      if cl_result.status_code == 200:
        print(
          "===============classification successful======================", cl_result.json())
        Logger.info("Classification successful")
        document_type = cl_result.json().get('doc_type')
        document_class = cl_result.json().get('doc_class')
        Logger.info(
          f"Classification successful:document_type:{document_type},\
             document_class:{document_class}")

    if isHitl or cl_result.status_code == 200:
      print("===============Start Extraction for======================",
          document_type, document_class)
      extract_res = get_extraction_score(
        case_id, uid, gcs_url, document_class)
      print("===extract_res,extract_res.status_code,document_type====",
          extract_res, extract_res.status_code, document_type)
      if extract_res.status_code is 200 and document_type == "application_form":
        extraction_score = extract_res.json().get("score")
        autoapproval_status = get_values(
                validation_score, extraction_score, matching_score,
                document_class, document_type)
        Logger.info(
          f"autoapproval_status for application:{autoapproval_status}")
        print("===========autoapproval status===========",
            autoapproval_status)
        update_autoapproval_status(
          case_id, uid, "success", autoapproval_status[0],
            "yes")
        print(
          "===============Extraction successful for application_form======================")
      elif extract_res.status_code == 200 and document_type == "supporting_documents":
        extraction_score = extract_res.json().get("score")
        print("===============Extraction successful for supporting_document======================",
            extract_res, document_class)
        validation_res = get_validation_score(
          case_id, uid, document_class)
        print(
          "===============Start Validation======================", validation_res)
        if validation_res.status_code == 200:
          validation_score = validation_res.json().get("score")
          print(
            "===============Validation successful======================", validation_res.json())
          matching_res = get_matching_score(case_id, uid)
          print("============matching_res============",
              matching_res.json())
          if matching_res.status_code == 200:
            matching_score = matching_res.json().get("score")
            print(
              "===============Matching successful======================", matching_res)
            try:
              Logger.info(f"extraction_score:{extraction_score}")
              Logger.info(f"validation_score:{validation_score}")
              Logger.info(f"matching_score:{matching_score}")
              autoapproval_status = get_values(
                validation_score, extraction_score, matching_score,
                document_class, document_type)
              Logger.info(
                f"autoapproval_status:{autoapproval_status}")
              print("===========autoapproval status===========",
                  autoapproval_status)
              update_autoapproval_status(
                case_id, uid, "success", autoapproval_status[0],
                 "yes")
            except Exception as e:
              err = traceback.format_exc().replace('\n', ' ')
              Logger.error(f"Error in Autoapproval: {err}")
              update_autoapproval_status(
                case_id, uid, "fail", None, None)

            Logger.info("Process task executed SUCCESSFULLY.")
          else:
            err = traceback.format_exc().replace('\n', ' ')
            Logger.error(err)
            Logger.error("Matching FAILED")
        else:
          err = traceback.format_exc().replace('\n', ' ')
          Logger.error(err)
          Logger.error("Validation FAILED")

    else:
      Logger.error(f"Classification FAILED.")
    return SUCCESS_RESPONSE
  except Exception as e:
    err = traceback.format_exc().replace('\n', ' ')
    Logger.error(err)
    raise HTTPException(status_code=500, detail=e)


def get_classification(case_id: str, uid: str, gcs_url: str):
  """Call the classification API and get the type and class of 
  the document"""
  base_url = "http://classification-service/classification_service/v1/"\
    "classification/classification_api"
  req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
    f"&gcs_url={gcs_url}"
  response = requests.post(req_url)
  return response


def get_extraction_score(case_id: str, uid: str, gcs_url: str, document_class: str):
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


def update_autoapproval_status(case_id: str, uid: str, status: str,
                 autoapproved_status: str, is_autoapproved: str):
  """Update auto approval status"""
  base_url = "http://document-status-service/document_status_service" \
    "/v1/update_autoapproved_status"
  req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
    f"&status={status}&autoapproved_status={autoapproved_status}&is_autoapproved={is_autoapproved}"
  response = requests.post(req_url)
  return response


def get_document(case_id: str, uid: str):
  """Get the document with given uid and case_id"""
  doc = Document.collection.filter(
    "case_id", "==", case_id).filter("uid", "==", uid).get()
  return doc