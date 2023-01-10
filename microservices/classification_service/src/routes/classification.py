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

""" classification endpoints """
import os
import shutil
import json
import requests
from typing import Optional
import traceback
from fastapi import APIRouter, HTTPException

from common.utils.logging_handler import Logger
from common.config import DOC_CLASS_STANDARDISATION_MAP,\
  APPLICATION_FORMS,SUPPORTING_DOCS
from common.config import STATUS_IN_PROGRESS, STATUS_SUCCESS, STATUS_ERROR
from utils.classification.split_and_classify import DocClassifier

# disabling for linting to pass
# pylint: disable = broad-except

router = APIRouter(prefix="/classification")
SUCCESS_RESPONSE = {"status": STATUS_SUCCESS}
FAILED_RESPONSE = {"status": STATUS_ERROR}
CLASSIFICATION_UNDETECTABLE = "unclassified"


def predict_doc_type(case_id: str, uid: str, gcs_url: str):
  """
    Fetches the model predictions and returns the output in dictionary format

      Args: case_id:str, uid:str, gcs_url:str

      Returns: case_id, u_id, predicted_class, model_conf, model_endpoint_id
    """

  outfolder = os.path.join(os.path.dirname(__file__), "temp_files")
  if not os.path.exists(outfolder):
    os.mkdir(os.path.join(os.path.dirname(__file__), "temp_files"))

  classifier = DocClassifier(case_id, uid, gcs_url, outfolder)

  doc_type = json.loads(classifier.execute_job())
  shutil.rmtree(outfolder)
  return doc_type


def update_classification_status(case_id: str,
                                 uid: str,
                                 status: str,
                                 document_class: Optional[str] = None,
                                 document_type: Optional[str] = None):
  """ Call status update api to update the classification output
    Args:
    case_id (str): Case id of the file ,
     uid (str): unique id for  each document
     status (str): status success/failure depending on the validation_score

    """
  base_url = "http://document-status-service/document_status_service" \
  "/v1/update_classification_status"

  if status == STATUS_SUCCESS:
    req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
    f"&status={status}&document_class={document_class}"\
      f"&document_type={document_type}"
    response = requests.post(req_url)
    return response

  else:
    req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
    f"&status={status}"
    response = requests.post(req_url)
    return response


@router.post("/classification_api")
async def classifiction(case_id: str, uid: str, gcs_url: str):
  """classifies the  input and updates the active status of document in
        the database
      Args:
          case_id (str): Case id of the file ,
           uid (str): unique id for  each document
           gcs (str): gcs url of document
      Returns:
          200 : PDF files are successfully classified and database updated
          400 : Improper parameters
          422 : Document classified as invalid
          500 : Internal Server Error if something fails
    """
  if not case_id.strip() or not uid.strip() or not gcs_url.strip():
    Logger.error("Classification failed parameters missing")
    update_classification_status(case_id, uid, STATUS_ERROR)
    raise HTTPException(status_code=400, detail="Parameters Missing")

  if not gcs_url.endswith(".pdf") or not gcs_url.startswith("gs://"):
    Logger.error("Classification failed GCS path is invalid")
    update_classification_status(case_id, uid, STATUS_ERROR)
    raise HTTPException(status_code=400, detail="GCS pdf path is incorrect")

  if case_id != gcs_url.split("/")[3] or uid != gcs_url.split("/")[4]:
    Logger.error("Classification failed parameters mismatched")
    update_classification_status(case_id, uid, STATUS_ERROR)
    raise HTTPException(status_code=400, detail="Parameters Mismatched")

  try:

    Logger.info(f"Starting classification for {case_id} and {uid} with gcs_url {gcs_url}")

    # Making prediction
    doc_prediction_result = predict_doc_type(case_id, uid, gcs_url)

    if doc_prediction_result:
      classification_score = doc_prediction_result["model_conf"]
      Logger.info(f"Classification confidence for {case_id} and {uid} is"\
        f" {classification_score}")
      if doc_prediction_result["predicted_class"].lower(
      ) == CLASSIFICATION_UNDETECTABLE.lower():
        #DocumentStatus api call
        response = update_classification_status(case_id, uid, "unclassified")
        Logger.error("Document unclassified")

        if response.status_code != 200:
          Logger.error("Document status update failed")
          #DocumentStatus api call
          update_classification_status(case_id, uid, STATUS_ERROR)
          raise HTTPException(
              status_code=500, detail="Failed to update document status")
        raise HTTPException(status_code=422, detail="Invalid Document")

      doc_type = None
      if doc_prediction_result["predicted_class"] in DOC_CLASS_STANDARDISATION_MAP.keys():
        doc_class = DOC_CLASS_STANDARDISATION_MAP[
          doc_prediction_result["predicted_class"]]
      else:
        doc_class = doc_prediction_result["predicted_class"]

      if doc_class in APPLICATION_FORMS:
        doc_type = "application_form"
      elif doc_class in SUPPORTING_DOCS:
        doc_type = "supporting_documents"
      else:
        Logger.error(f"Doc class {doc_class} is not a valid doc class")
        update_classification_status(case_id, uid, STATUS_ERROR)
        raise HTTPException(
            status_code=422, detail="Unidentified document class found")

      SUCCESS_RESPONSE["case_id"] = doc_prediction_result["case_id"]
      SUCCESS_RESPONSE["uid"] = uid
      SUCCESS_RESPONSE["doc_type"] = doc_type
      SUCCESS_RESPONSE["doc_class"] = doc_class

      #DocumentStatus api call
      response = update_classification_status(
          case_id,
          uid,
          STATUS_SUCCESS,
          document_class=doc_class,
          document_type=doc_type)
      print(response)
      if response.status_code != 200:
        Logger.error(f"Document status update failed for {case_id} and {uid}")
        #DocumentStatus api call
        update_classification_status(case_id, uid, STATUS_ERROR)
        raise HTTPException(
            status_code=500, detail="Document status update failed")

      return SUCCESS_RESPONSE

    else:
      #DocumentStatus api call
      update_classification_status(case_id, uid, STATUS_ERROR)
      raise HTTPException(status_code=500, detail="Classification Failed")

  except HTTPException as e:
    print(e)
    Logger.error(f"{e} while classification {case_id} and {uid}")
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise e

  except Exception as e:
    print(f"{e} while classification {case_id} and {uid}")
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    #DocumentStatus api call
    update_classification_status(case_id, uid, STATUS_ERROR)
    raise HTTPException(status_code=500, detail="Classification Failed") from e
