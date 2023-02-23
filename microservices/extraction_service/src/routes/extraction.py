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

""" extraction endpoints """

from fastapi import APIRouter, HTTPException, status, Response
from fastapi.concurrency import run_in_threadpool
from common.db_client import bq_client
from common.utils.logging_handler import Logger
from common.utils.stream_to_bq import stream_document_to_bigquery
from common.utils.format_data_for_bq import format_data_for_bq
from common.config import STATUS_SUCCESS, STATUS_ERROR

from utils.extract_entities import extract_entities
import requests
import traceback

# disabling for linting to pass
# pylint: disable = broad-except
router = APIRouter()


@router.post("/extraction_api")
async def extraction(case_id: str, uid: str, doc_class: str, document_type: str,
                     context: str, gcs_url: str, response: Response):
  """extracts the document with given case id and uid
        Args:
            case_id (str): Case id of the file ,
             uid (str): unique id for  each document
             doc_class (str): class of document (processor is configured per document class)
             document_type (str): application_form vs supporting_documents
        Returns:
            200 : PDF files are successfully classified and database updated
            500  : HTTPException: 500 Internal Server Error if something fails
            404 : Parser not available for given document
      """
  try:
    Logger.info(f"Starting extraction for case_id={case_id}, uid={uid}, "
                f"doc_class={doc_class}, document_type={document_type}, "
                f"context={context}, gcs_url={gcs_url}")
    client = bq_client()
    # document = Document.find_by_uid(uid)
    # gcs_url = document.url
    #Call ML model to extract entities from document
    extraction_output = await run_in_threadpool(extract_entities, gcs_url,
                                                doc_class, context)
    #check if the output of extract entity function is
    #touple containing list of dictionaries and extraction score
    # extraction_output = list(extraction_output)
    # extraction_output.append("double key extraction")
    # extraction_output =  tuple(extraction_output)
    is_tuple = isinstance(extraction_output, tuple)
    Logger.info(f"extraction_api extraction_output={extraction_output}")
    if is_tuple and isinstance(extraction_output[0], list):
      #call the format_data_bq function to format data to be
      # inserted in Bigquery
      entities_for_bq = format_data_for_bq(extraction_output[0])
      Logger.info(f"Streaming data to BigQuery for case_id={case_id} document_type={document_type} doc_class={doc_class}")
      #stream_document_to_bigquery updates data to bigquery
      bq_update_status = stream_document_to_bigquery(client, case_id, uid,
                                                     doc_class, document_type,
                                                     entities_for_bq, gcs_url)
      if not bq_update_status:
        Logger.info(f"returned status {bq_update_status}")
      else:
        Logger.error(f"Failed streaming to BQ,  returned status {bq_update_status}")

      #update_extraction_status updates data to document collection
      db_update_status = update_extraction_status(case_id, uid, STATUS_SUCCESS,
                                                  extraction_output[0],
                                                  extraction_output[1],
                                                  extraction_output[2])
      #checking if both databases are updated successfully
      if db_update_status.status_code == 200 and bq_update_status == []:
        return {
            "status": STATUS_SUCCESS,
            "entities": extraction_output[0],
            "score": extraction_output[1],
            "extraction_status": extraction_output[2],
            "extraction_field_min_score": extraction_output[3],
            "message": f"document with case_id {case_id} ,uid_id {uid} "
                       f"successfully extracted"
        }
      else:
        Logger.error("Extraction database update failed")
        err = traceback.format_exc().replace("\n", " ")
        Logger.error(err)
        raise HTTPException(status_code=500)

    #check if  extract_entities returned None when parser not available
    elif extraction_output is None:
      update_extraction_status(case_id, uid, STATUS_ERROR, None, None, None)
      Logger.error(f"Parser not available for case_id {case_id} " 
                   f",uid {uid}, doc_class {doc_class}")
      response.status_code = status.HTTP_404_NOT_FOUND
      response.body = f"Parser not available for case_id {case_id}" \
                      f"uid {uid}, doc_class {doc_class}"
      return response
    #check if  extract_entities returned unexpected output
    else:
      raise HTTPException(status_code=500)
  except Exception as e:
    update_extraction_status(case_id, uid, STATUS_ERROR, None, None, None)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(f"Extraction failed for case_id {case_id} and uid {uid}")
    Logger.error(e)
    Logger.error(err)
    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    response.body = "Extraction failed for case_id {case_id} " \
                    "and uid {uid}"
    return response


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
