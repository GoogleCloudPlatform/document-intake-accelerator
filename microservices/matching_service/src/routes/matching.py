""" Matching endpoints"""
import json
from fastapi import APIRouter, HTTPException
import requests
from common.models import Document
from common.utils.logging_handler import Logger
from typing import Optional, List, Dict
from utils.json_matching.match_json import compare_json
# disabling for linting to pass
# pylint: disable = broad-except
import copy
router = APIRouter()
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}

def get_matching_score(AF_dict:dict, SD_dict:dict):
  #ML script function Call
  #result = MLCALL()
  matching =  compare_json(AF_dict["entities"],SD_dict["entities"])
  print(matching)
  print("entities",matching[:len(matching)-1])
  print("matching score",matching[-1]["Matching Score"])
  if matching:
    return (matching[:len(matching)-1], matching[-1]["Matching Score"])
  else:
    return None
  result = {"status":"success"}
  return result


def update_matching_status(case_id: str,uid: str,status: str,entity: Optional[List[dict]] = None, matching_score: Optional[float] = None):
  Logger.info(f"Updating Matching status for case_id {case_id} and uid {uid}")
  response = None
  if status.lower() == "success":
    base_url = "http://document-status-service/document_status_service/v1/update_matching_status"
    req_url = f"{base_url}?case_id={case_id}&uid={uid}&status={status}&entity={entity}&matching_score={matching_score}"
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
    if AF_doc:
      Logger.info(f"Matching document with case_id {case_id} and uid {uid} with the corresponding Application form")
    
      #print(AF_doc.to_dict())
      
      SD_doc = Document.find_by_uid(uid)
      print("Before")
      print(SD_doc.to_dict()["entities"])

      SD_dict = copy.deepcopy(SD_doc.to_dict())
      AF_dict = copy.deepcopy(AF_doc.to_dict())
      #matching ml call
      matching_result = get_matching_score(AF_dict,SD_dict)
      print(matching_result)
      Logger.info(matching_result)
    
      if matching_result:
        updated_entity = matching_result[0]
        overall_score = matching_result[1]
        print("After")
        print(updated_entity)
        dsm_status = update_matching_status(case_id,uid,"success",entity = updated_entity, matching_score=overall_score)
        
        if dsm_status["status"].lower() == "success":
          Logger.info(f"Matching document with case_id {case_id} and uid {uid} was successful")
          return {"status":"success"}
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
  