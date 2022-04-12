""" extraction endpoints """

from fastapi import APIRouter, HTTPException, status, Response
from fastapi.concurrency import run_in_threadpool
from common.db_client import bq_client
from common.models import Document
from common.utils.logging_handler import Logger
from common.utils.stream_to_bq import stream_document_to_bigquery
from common.utils.format_data_for_bq import format_data_for_bq
from utils.extract_entities import extract_entities
import requests
import traceback

# disabling for linting to pass
# pylint: disable = broad-except
router = APIRouter()


@router.post("/extraction_api")
async def extraction(case_id: str, uid: str, doc_class: str,
                     response: Response):
  """extracts the document with given case id and uid
        Args:
            case_id (str): Case id of the file ,
             uid (str): unique id for  each document
             doc_class (str): class of document
        Returns:
            200 : PDF files are successfully classified and database updated
            500  : HTTPException: 500 Internal Server Error if something fails
            404 : Parser not available for given document
      """
  try:
    client = bq_client()
    document = Document.find_by_uid(uid)
    gcs_url = document.url
    context = document.context
    document_type = document.document_type
    #Call ML model to extract entities from document
    extraction_output = await run_in_threadpool(extract_entities,
                              gcs_url, doc_class, context)
    #check if the output of extract entity function is
    #touple containing list of dictionaries and extraction score
    is_tuple = isinstance(extraction_output, tuple)
    if is_tuple and isinstance(extraction_output[0], list):
      #call the format_data_bq function to format data to be
      # inserted in Bigquery
      entities_for_bq = format_data_for_bq(extraction_output[0])
      #stream_document_to_bigquery updates data to bigquery
      bq_update_status = stream_document_to_bigquery(client, case_id, uid,
                                                     doc_class, document_type,
                                                     entities_for_bq)
      #update_extraction_status updates data to document collection
      db_update_status = update_extraction_status(case_id, uid, "success",
                                                  extraction_output[0],
                                                  extraction_output[1])
      #checking if both databases are updated successfully
      if db_update_status.status_code == 200 and bq_update_status == []:
        return {
            "status": "success",
            "score": extraction_output[1],
            "message": f"document with case_id {case_id} ,uid_id {uid} "
                       f"successfully extracted"
        }
      else:
        Logger.error("Extraction database updation failed")
        err = traceback.format_exc().replace("\n", " ")
        Logger.error(err)
        raise HTTPException(status_code=500)

    #check if  extract_entities returned None when parser not available
    elif extraction_output is None:
      update_extraction_status(case_id, uid, "fail", None, None)
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
    update_extraction_status(case_id, uid, "fail", None, None)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(f"Extraction failed for case_id {case_id} and uid {uid}")
    Logger.error(e)
    Logger.error(err)
    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    response.body = "Extraction failed for case_id {case_id} " \
                    "and uid {uid}"
    return response


def update_extraction_status(case_id: str, uid: str, extraction_status: str,
                             entity: list, extraction_score: float):
  """
    This function calls the document status service
    to update the extraction status in Database
    Args :
     case_id (str)
     uid (str): unique id for  each document
     status (str): success or fail for extraction process
     entity (list):List of dictionary for entities and value
     extraction_score(float): Extraction score for doument
  """

  base_url = "http://document-status-service/document_status_service/v1/"
  req_url = f"{base_url}update_extraction_status"
  if extraction_status == "success":
    response = requests.post(
        f"{req_url}?case_id={case_id}"
        f"&uid={uid}&status={extraction_status}"
        f"&extraction_score={extraction_score}",
        json=entity)
  else:
    response = requests.post(f"{req_url}?case_id={case_id}"
                             f"&uid={uid}&status={extraction_status}")
  return response
