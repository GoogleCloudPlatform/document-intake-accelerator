""" Matching endpoints"""
from fastapi import APIRouter, HTTPException
import requests
from common.models import Document
from common.utils.logging_handler import Logger
from typing import Optional, List, Dict
# disabling for linting to pass
# pylint: disable = broad-except

router = APIRouter()
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}

def get_matching_score(AF_doc:dict, SD_doc:dict):
  #ML script function Call
  #result = MLCALL()
  result = {"status":"success"}
  return result


def update_matching_status(case_id: str,uid: str,status: str,entity: Optional[List[dict]] = None, matching_score: Optional[float] = None):
  Logger.info(f"Updating Matching status for case_id {case_id} and uid {uid}")
  response = None
  if status.lower() == "success":
    base_url = "http://document-status-service/document_status_service/v1/update_matching_status"
    req_url = f"{base_url}?case_id={case_id}&uid={uid}&status={status}&matching_score=0.0"
    response = requests.post(req_url,json=entity)
    print("success")
    print(response)
    if response.status_code == 200:
    #return res
      return {"status":"success"}
    else:
      return {"status":"failed"}

  else:
    base_url = "http://document-status-service/document_status_service/v1/update_matching_status"
    req_url = f"{base_url}?case_id={case_id}&uid={uid}&status={status}"
    response = requests.post(req_url)
    print("fail")
    print(response)
    if response.status_code == 200:
    #return res
      return {"status":"success"}
    else:
      return {"status":"failed"}


@router.post("/match_document")
async def match_document(case_id: str, uid: str):
  """
        matching the document with case id , uid


            Args:
                case_id (str): Case id of the file ,
                 uid (str): unique id for  each document
            Returns:
                200 : Matching score successfully  updated
                404 : If Application form for the document is not found
                500 : HTTPException: 500 Internal Server Error if something fail
    """
  try:
    
    AF_doc = Document.collection.filter(case_id = case_id).filter(active = "active").filter(document_type = "AF").get()
    print(AF_doc)
    if AF_doc:
      Logger.info(f"Matching document with case_id {case_id} and uid {uid} with the corresponding Application form")
    
      print(AF_doc.to_dict())
      
      SD_doc = Document.find_by_uid(uid)
      print(SD_doc.to_dict())
      Logger.info(SD_doc)
    
      #matching ml call
      matching_result = get_matching_score(AF_doc,SD_doc)
      print(matching_result)
    
      if matching_result["status"].lower() == "success":
        dsm_status = update_matching_status(case_id,uid,matching_result["status"])
        
        if dsm_status["status"].lower() == "success":
          Logger.info(f"Matching document with case_id {case_id} and uid {uid} was successful")
          return matching_result
        else:
          Logger.error(f"Matching document with case_id {case_id} and uid {uid} Failed Doc status not updated")
          raise HTTPException(status_code=500,detail="Document Matching failed.Status failed to update")

      else:    
        Logger.error(f"Matching document with case_id {case_id} and uid {uid} Failed Error in geting Matching score")
        raise HTTPException(status_code=500,detail="Document Matching failed.Error in getting matching score")
    
    else:
      Logger.error(f"Error while matching document with case_id {case_id} and uid {uid}. Application form not found with given case_id : {case_id}")
      raise HTTPException(status_code=404,detail="No supporting Application found")
    
  except HTTPException as e:
    dsm_status = update_matching_status(case_id,uid,"failed")
    Logger.error(f"Error while matching document with case_id {case_id} and uid {uid}")
    Logger.error(e)
    raise e

  except Exception as e:
    dsm_status = update_matching_status(case_id,uid,"failed")
    Logger.error(f"Error while matching document with case_id {case_id} and uid {uid}")
    Logger.error(e)
    print(e)
    raise HTTPException(status_code=500,detail="Matching Failed.Something went wrong") from e
  