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
entity = []


@router.post("/validation_api")
async def validation(case_id: str, uid: str, doc_class: str,
                     entities: List[Dict], response: Response):
  """ validates the document with case id , uid , doc_class
    Args:
    case_id (str): Case id of the file ,
     uid (str): unique id for  each document
     doc_class (str): class of document
    Returns:
    200 : validation score successfully  updated
    500  : HTTPException: 500 Internal Server Error if something fails
    """
  validation_status = "fail"
  try:
    validation_output = get_values(doc_class, case_id, uid, entities)
    #The output of get_values is a tuple if executed successfully
    #so taking valdation score and validation entities from output
    if validation_output is not None:
      validation_score = validation_output[0]
      validation_entities = validation_output[1]
      validation_status = "success"
      update_validation_status(case_id, uid, validation_score,
                               validation_status, validation_entities)
      Logger.info(f"Validation Score for cid:{case_id}, uid: {uid},"
                  f" doc_class:{doc_class} is {validation_score}")
      return {"status": validation_status, "score": validation_score}
    #Else condition works if the get_values function returns None
    else:
      validation_status = "fail"
      update_validation_status(case_id, uid, None, validation_status, entities)
      Logger.error(f"Validation failed for case_id:{case_id}, uid: {uid},"
                   f" doc_class:{doc_class}")
      response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
      response.body = f"Validation failed for case_id {case_id}" \
                      f"uid {uid}, doc_class {doc_class}"
      return response

  except Exception as error:
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    print(err)

    update_validation_status(case_id, uid, None, validation_status, entities)
    raise HTTPException(
        status_code=500, detail="Failed to update validation score") from error


def update_validation_status(case_id: str, uid: str, validation_score: float,
                             validation_status: str,
                             validation_entities: List[Dict]):
  """ Call status update api to update the validation score
    Args:
    case_id (str): Case id of the file ,
     uid (str): unique id for  each document
     validation_score (float): validation score calculated by validation api
     status (str): status success/failure depending on the validation_score
    """
  base_url = "http://document-status-service/document_status_service" \
    "/v1/update_validation_status"
  if validation_status == "success":
    req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
    f"&validation_score={validation_score}&status={validation_status}"
  else:
    req_url = f"{base_url}?case_id={case_id}&uid={uid}&" \
              f"status={validation_status}"
  response = requests.post(req_url, json=validation_entities)
  return response
