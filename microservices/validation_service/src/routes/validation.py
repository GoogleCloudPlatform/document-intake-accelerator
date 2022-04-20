""" Validation endpoints """
import traceback
import requests
from fastapi import APIRouter, HTTPException, status, Response
from typing import List, Dict
from common.utils.logging_handler import Logger
from utils.validation import get_values
# disabling for linting to pass
# pylint: disable = broad-except

router = APIRouter(prefix="/validation")
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}
entity=[]

@router.post("/validation_api")
async def validation(case_id: str, uid: str, doc_class: str,entities:List[Dict]):
  """ validates the document with case id , uid , doc_class
    Args:
    case_id (str): Case id of the file ,
     uid (str): unique id for  each document
     doc_class (str): class of document
    Returns:
    200 : validation score successfully  updated
    500  : HTTPException: 500 Internal Server Error if something fails
    """
  status = "fail"
  try:
    print("==========Inside validation API==new========================",entities)
    validation_output = get_values(doc_class, case_id, uid ,entities)
    validation_score = validation_output[0]
    validation_entities = validation_output[1]
    print("=====================validation output neww validation score ==============",validation_score)

    print("=====================validation output neww entities ==============",validation_entities)
    if validation_output is not None:
      status = "success"
      update_validation_status(case_id, uid, validation_score, status,validation_entities)
      Logger.info(
        f"Validation Score for cid:{case_id}, uid: {uid},"
        f" doc_class:{doc_class} is {validation_score}")
      return {
        "status": status,
        "score": validation_score
      }
    else:
      status = "fail"
      update_validation_status(case_id, uid,None , status,entities)
      Logger.error(
        f"Validation failed  for case_id:{case_id}, uid: {uid},"
        f" doc_class:{doc_class}")
      return {
        "status": status,
        "score": validation_score
      }
  except Exception as error:
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    update_validation_status(case_id, uid, None, status,entities)
    raise HTTPException(
      status_code=500, detail="Failed to update validation score")from error


def update_validation_status(case_id: str, uid: str,
               validation_score: float, status: str,validation_entities:List[Dict]):
  """ Call status update api to update the validation score
    Args:
    case_id (str): Case id of the file ,
     uid (str): unique id for  each document
     validation_score (float): validation score calculated by validation api
     status (str): status success/failure depending on the validation_score
    """
  print("==========Inside update validation status============",validation_score,validation_entities)
  base_url = "http://document-status-service/document_status_service" \
    "/v1/update_validation_status"
  if status == "success":
    req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
    f"&validation_score={validation_score}&status={status}"
  else:
    req_url = f"{base_url}?case_id={case_id}&uid={uid}&status={status}"
  response = requests.post(req_url,json=validation_entities)
  return response
