""" Validation endpoints """
import traceback
import requests
from fastapi import APIRouter, HTTPException
from common.utils.logging_handler import Logger
from utils.validation import get_values
# disabling for linting to pass
# pylint: disable = broad-except

router = APIRouter(prefix="/validation")
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}


@router.post("/validation_api")
async def validation(case_id: str, uid: str, doc_class: str):
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
    validation_score = get_values(doc_class, case_id, uid)
    if validation_score:
      status = "success"
    update_validation_status(case_id, uid, validation_score, status)
    Logger.info(
      f"Validation Score for cid:{case_id}, uid: {uid},"
      f" doc_class:{doc_class} is {validation_score}")
    return {
      "status": status,
      "score": validation_score
    }
  except Exception as error:
    err = traceback.format_exc().replace('\n', ' ')
    Logger.error(err)
    update_validation_status(case_id, uid, None, status)
    raise HTTPException(
      status_code=500, detail="Failed to update validation score")from error


def update_validation_status(case_id: str, uid: str,
               validation_score: float, status: str):
  """ Call status update api to update the validation score
    Args:
    case_id (str): Case id of the file ,
     uid (str): unique id for  each document
     validation_score (float): validation score calculated by validation api
     status (str): status success/failure depending on the validation_score
    """
  base_url = "http://document-status-service/document_status_service" \
    "/v1/update_validation_status"
  if status == "success":
    req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
    f"&validation_score={validation_score}&status={status}"
  else:
    req_url = f"{base_url}?case_id={case_id}&uid={uid}&status={status}"
  response = requests.post(req_url)
  return response
