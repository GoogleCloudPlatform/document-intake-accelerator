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
from typing import Dict
from typing import List
from models.process_task import ProcessTask
import os
import shutil
import json
import requests
from typing import Optional
import traceback
from fastapi import APIRouter, HTTPException

from common.utils.logging_handler import Logger
from common.config import get_document_type
from common.config import STATUS_SUCCESS, STATUS_ERROR, STATUS_SPLIT,\
  DOC_CLASS_SPLIT_DISPLAY_NAME, DOC_TYPE_SPLIT_DISPLAY_NAME
from utils.classification.split_and_classify import classify, DocumentConfig

router = APIRouter(prefix="/classification")

FAILED_RESPONSE = {"status": STATUS_ERROR}
CLASSIFICATION_UNDETECTABLE = "unclassified"


def predict_doc_type(configs: List[Dict]):
  """
    Fetches the model predictions and returns the output in dictionary format

      Args: case_id:str, uid:str, gcs_url:str

      Returns: case_id, uid, predicted_class, model_conf, model_endpoint_id
    """

  out_folder = os.path.join(os.path.dirname(__file__), "temp_files")
  if not os.path.exists(out_folder):
    os.mkdir(os.path.join(os.path.dirname(__file__), "temp_files"))

  doc_configs = []
  for config in configs:
    case_id = config.get("case_id")
    uid = config.get("uid")
    gcs_url = config.get("gcs_url")
    if not case_id.strip() or not uid.strip() or not gcs_url.strip():
      Logger.error("Classification failed parameters missing for "
                   "case_id={case_id}, uid={uid}, gcs_url={gcs_url}")
      update_classification_status(case_id, uid, STATUS_ERROR)
      continue

    if not gcs_url.endswith(".pdf") or not gcs_url.startswith("gs://"):
      Logger.error("Classification failed GCS path is invalid for "
                   "case_id={case_id}, uid={uid}, gcs_url={gcs_url}")
      update_classification_status(case_id, uid, STATUS_ERROR)
      continue
    #
    # if case_id != gcs_url.split("/")[3] or uid != gcs_url.split("/")[4]:
    #   Logger.error("Classification failed parameters mismatched"
    #                "case_id={case_id}, uid={uid}, gcs_url={gcs_url}")
    #   update_classification_status(case_id, uid, STATUS_ERROR)
    #   continue

    doc_configs.append(DocumentConfig(case_id=case_id,
                                      uid=uid,
                                      gcs_url=gcs_url,
                                      out_folder=out_folder))

  doc_types = json.loads(classify(doc_configs))
  shutil.rmtree(out_folder)
  return doc_types


def update_classification_status(case_id: str,
    uid: str,
    status: str,
    document_class: Optional[str] = None,
    document_type: Optional[str] = None,
):
  """ Call status update api to update the classification output
    Args:
    case_id (str): Case id of the file ,
     uid (str): unique id for  each document
     status (str): status success/failure depending on the validation_score

    """
  base_url = "http://document-status-service/document_status_service" \
             "/v1/update_classification_status"

  if status in [STATUS_SUCCESS, STATUS_SPLIT]:
    req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
              f"&status={status}&document_class={document_class}" \
              f"&document_type={document_type}"
    response = requests.post(req_url)
    return response

  else:
    req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
              f"&status={status}"
    response = requests.post(req_url)
    return response


@router.post("/classification_api")
async def classification(payload: ProcessTask):
  """classifies the  input and updates the active status of document in
        the database
      Args:
          payload (ProcessTask): Consist of configs required to run the pipeline
      Returns:
          200 : PDF files are successfully classified and database updated
          400 : Improper parameters
          422 : Document classified as invalid
          500 : Internal Server Error if something fails
    """
  try:
    success_response = {"status": STATUS_SUCCESS}

    payload = payload.dict()
    configs = payload.get("configs")
    Logger.info(f"classification_api starting classification for configs={configs}")
    # Making prediction

    doc_prediction_results = predict_doc_type(configs)

    Logger.info(f"classification_api - doc_prediction_results = {doc_prediction_results}")
    for config in configs:
      case_id = config.get("case_id")
      uid = config.get("uid")
      gcs_url = config.get("gcs_url")

      if gcs_url not in doc_prediction_results.keys():
        Logger.error(f"Classification did not return results for gcs_url={gcs_url}, "
                     f"case_id={case_id}, uid={uid}")
        update_classification_status(case_id, uid, STATUS_ERROR)
        continue

      prediction = doc_prediction_results[gcs_url]

      Logger.info(f"classification_api - handling config for case_id={case_id} "
                  f"uid={uid}, gcs_url={gcs_url}, "
                  f"prediction={prediction}")

      if len(prediction) > 1:
        Logger.info(f"classification_api - document has been split for "
                    f"case_id={case_id} "
                    f"uid={uid} gcs_url={gcs_url} ")
        # Document was split, need to update status of the original document,
        # since it will not be sent for extraction
        update_classification_status(case_id, uid, STATUS_SPLIT,
                                     document_class=DOC_CLASS_SPLIT_DISPLAY_NAME,
                                     document_type=DOC_TYPE_SPLIT_DISPLAY_NAME)

      for doc_prediction_result in prediction:

        if doc_prediction_result["predicted_class"] is not None:
          classification_score = doc_prediction_result["model_conf"]
          predicated_class = doc_prediction_result["predicted_class"]
          Logger.info(f"classification_api - Classification confidence for "
                      f"gcs_url={gcs_url} is {predicated_class} with "
                      f"{classification_score}")

          if predicated_class.lower(
          ) == CLASSIFICATION_UNDETECTABLE.lower():
            # DocumentStatus api call
            response = update_classification_status(case_id, uid,
                                                    "unclassified")
            Logger.error("Document unclassified")

            if response.status_code != 200:
              Logger.error("Document status update failed")
              # DocumentStatus api call
              update_classification_status(case_id, uid, STATUS_ERROR)
              raise HTTPException(
                  status_code=500, detail="Failed to update document status")
            raise HTTPException(status_code=422, detail="Invalid Document")

          gcs_url = doc_prediction_result["gcs_url"]
          doc_type = get_document_type(predicated_class)

          uid = doc_prediction_result["uid"]
          document = {"case_id": doc_prediction_result["case_id"],
                      "uid": uid,
                      "doc_type": doc_type,
                      "doc_class": predicated_class,
                      "gcs_url": gcs_url,
                      }
          if "results" not in success_response.keys():
            success_response["results"] = []
          success_response["results"].append(document)
          Logger.info(f"classification_api - Appending document {uid} {document} ")
          # DocumentStatus api call
          response = update_classification_status(
              case_id,
              uid,
              STATUS_SUCCESS,
              document_class=predicated_class,
              document_type=doc_type)
          Logger.debug(response)
          if response.status_code != 200:
            Logger.error(
              f"Document status update failed for {case_id} and {uid}")
            # DocumentStatus api call
            update_classification_status(case_id, uid, STATUS_ERROR)
            # raise HTTPException(
            #     status_code=500, detail="Document status update failed")
        else:
          Logger.error(f"classification_api - Prediction result cannot be parsed for "
                      f"gcs_url={gcs_url}:  {doc_prediction_result}")

    Logger.info(f"classification_api  response: {success_response}")
    return success_response

  # except HTTPException as e:
  #   Logger.error(f"{e} while classification {case_id} and {uid}")
  #   err = traceback.format_exc().replace("\n", " ")
  #   Logger.error(err)
  #   raise e

  except Exception as e:
    Logger.error(f"{e} while classification ")
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    # DocumentStatus api call
    # update_classification_status(case_id, uid, STATUS_ERROR)
    raise HTTPException(status_code=500, detail=FAILED_RESPONSE) from e