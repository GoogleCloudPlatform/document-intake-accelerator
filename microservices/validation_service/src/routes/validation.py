""" Validation endpoints """
import requests
from fastapi import APIRouter, HTTPException
from common.models import Document
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
  status = "Failed"
  doc = Document.collection.filter("uid", "==", uid).filter(
    "case_id", "==", case_id).get()
  if not doc:
    Logger.error("uid or cid not found")
    update_validation_status(case_id, uid, None,status)
    raise HTTPException(status_code=404, detail="uid or cid not found")
  try:
    validation_score = get_values(doc_class, case_id, uid)
    if validation_score:
      status = "Success"
    update_validation_status(case_id, uid, validation_score,status)
    Logger.info(
      f"Validation Score for cid:{case_id}, uid: {uid}, doc_class:{doc_class} is {validation_score}")
    return {
      "status": status,
      "score": f"{validation_score}"
    }
  except Exception as error:
    Logger.error(error)
    update_validation_status(case_id, uid, None,status)
    raise HTTPException(
      status_code=500, detail="Failed to update validation score") from error


def update_validation_status(case_id: str, uid: str, validation_score: float, status: str):
  """ Call status update api to update the validation score
    Args:
      case_id (str): Case id of the file ,
       uid (str): unique id for  each document
       validation_score (float): validation score calculated by validation api
       status (str): status success/failure depending on the validation_score
    """
  base_url = "http://document-status-service/document_status_service/v1/update_validation_status"
  req_url = f"{base_url}?case_id={case_id}&uid={uid}&validation_score={validation_score}&status={status}"
  requests.post(req_url)
