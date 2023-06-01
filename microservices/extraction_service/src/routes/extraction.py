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
from common.models import Document

""" extraction endpoints """

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from common.db_client import bq_client
from common.utils.logging_handler import Logger
from common.utils.stream_to_bq import stream_document_to_bigquery
from common.utils.format_data_for_bq import format_data_for_bq
from common.config import STATUS_SUCCESS, STATUS_ERROR, DocumentWrapper
from models.process_task import ProcessTask
from utils.extract_entities import extract_entities
import requests
import traceback

# disabling for linting to pass
# pylint: disable = broad-except
router = APIRouter()
SUCCESS_RESPONSE = {"status": STATUS_SUCCESS}
FAILED_RESPONSE = {"status": STATUS_ERROR}

@router.post("/extraction_api")
async def extraction(payload: ProcessTask):
  """extracts the document with given case id and uid
        Args:
             payload (ProcessTask): Consist of configs required to run the pipeline
                    uid (str): unique id for  each document
                    doc_class (str): class of document (processor is configured per document class)
        Returns:
            200 : PDF files are successfully classified and database updated
            500  : HTTPException: 500 Internal Server Error if something fails
            404 : Parser not available for given document
      """
  try:
    payload = payload.dict()
    Logger.info(f"extraction_api - payload received {payload}")
    configs = payload.get("configs")
    doc_class = payload.get("doc_class")
    Logger.info(f"extraction_api - Starting extraction for configs={configs},"
                f"doc_class={doc_class}")

    doc_configs = []
    for config in configs:
      uid = config.get("uid")
      document = Document.find_by_uid(uid)
      if not document:
        Logger.error(f"extraction_api - Could not retrieve document by uid {uid}")
        continue

      case_id = document.case_id
      gcs_url = document.url
      context = document.context
      document_type = document.document_type
      doc_configs.append(DocumentWrapper(case_id=case_id,
                                        uid=uid,
                                        gcs_url=gcs_url,
                                        document_type=document_type,
                                        context=context,
                                        ))

    client = bq_client()
    extraction_output = await run_in_threadpool(extract_entities,
                                                doc_configs,
                                                doc_class)

    if extraction_output is None:
      # check if  extract_entities returned None when parser not available
      raise HTTPException(status_code=404)

    #Update status for all documents that were requested for extraction
    Logger.info(f"extraction_api - Handling results for {len(configs)} input documents")
    for config in configs:
      uid = config.get("uid")
      document = Document.find_by_uid(uid)
      if not document:
        Logger.error(f"extraction_api - Could not retrieve document by uid {uid}")
        continue
      case_id = document.case_id
      gcs_url = document.url
      document_type = document.document_type
      #find corresponding result in extraction_output
      extraction_result_keys = [key for key in extraction_output if uid == key.uid]
      if len(extraction_result_keys) == 0:
        Logger.error(
          f"extraction_api - No extraction result returned for {gcs_url} and"
          f" uid={uid}")
        update_extraction_status(case_id, uid, STATUS_ERROR, None, None, None)
        continue

      conf = extraction_result_keys[0]

      entities_for_bq = format_data_for_bq(extraction_output[conf][0])

      Logger.info(f"extraction_api - Streaming data to BigQuery for {gcs_url}, "
                  f"case_id={case_id}, uid={uid}, "
                  f"document_type={document_type}, "
                  f"doc_class={doc_class}")
      #stream_document_to_bigquery updates data to bigquery
      bq_update_status = stream_document_to_bigquery(client, case_id, uid,
                                                     doc_class, document_type,
                                                     entities_for_bq, gcs_url)
      if bq_update_status:
        Logger.error(f"extraction_api - Failed streaming to BQ, returned status {bq_update_status}")

      #update_extraction_status updates data to document collection
      db_update_status = update_extraction_status(case_id, uid, STATUS_SUCCESS,
                                                  extraction_output[conf][0],
                                                  extraction_output[conf][1],
                                                  extraction_output[conf][2])
      #checking if both databases are updated successfully
      if db_update_status.status_code == 200 and bq_update_status == []:
        document = {"case_id": case_id,
                    "uid": uid,
                    "doc_type": document_type,
                    "doc_class": doc_class,
                    "gcs_url": gcs_url,
                    "entities": extraction_output[conf][0],
                    "score": extraction_output[conf][1],
                    "extraction_status": extraction_output[conf][2],
                    "extraction_field_min_score": extraction_output[conf][3],
                    "message": f"document with case_id {case_id} ,uid_id {uid} "
                               f"successfully extracted"
                    }
        if "results" not in SUCCESS_RESPONSE.keys():
          SUCCESS_RESPONSE["results"] = []
        SUCCESS_RESPONSE["results"].append(document)
      else:
        Logger.error(f"extraction_api - Extraction database update failed for {gcs_url},"
                     f" uid={uid}")
        err = traceback.format_exc().replace("\n", " ")
        Logger.error(err)
        update_extraction_status(case_id, uid, STATUS_ERROR, None, None, None)
    Logger.info(f"extraction_api - Successfully Completed!")

    return SUCCESS_RESPONSE

  except Exception as e:
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(f"extraction_api - Extraction failed")
    Logger.error(e)
    Logger.error(err)
    raise HTTPException(status_code=500)


def update_extraction_status(case_id: str, uid: str, extraction_status: str,
    entity: list, extraction_score: float,
    extraction_type: str):
  """
    This function calls the document status service
    to update the extraction status in Database
    Args :
     case_id (str)
     uid (str): unique id for  each document
     status (str): success or fail for extraction process
     entity (list):List of dictionary for entities and value
     extraction_score(float): Extraction score for doument
     extraction_type(str): It's the extraction status if
     like duplicate keys present or not
  """

  base_url = "http://document-status-service/document_status_service/v1/"
  req_url = f"{base_url}update_extraction_status"
  if extraction_status == STATUS_SUCCESS:
    response = requests.post(
        f"{req_url}?case_id={case_id}"
        f"&uid={uid}&status={extraction_status}"
        f"&extraction_score={extraction_score}&"
        f"extraction_status={extraction_type}",
        json=entity)
  else:
    response = requests.post(f"{req_url}?case_id={case_id}"
                             f"&uid={uid}&status={extraction_status}")
  return response
