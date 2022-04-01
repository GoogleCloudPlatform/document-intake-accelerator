""" Matching endpoints"""
from fastapi import APIRouter, HTTPException
import requests
from common.models import Document
from common.utils.logging_handler import Logger
from typing import Optional, List
from utils.json_matching.match_json import compare_json
# disabling for linting to pass
# pylint: disable = broad-except
import copy

router = APIRouter()
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}


def get_matching_score(af_dict: dict, sd_dict: dict):
  """
    Makes call to json matching function and returns the result

    Args: af_dict: Dictionary of Application form
          sd_dict: Dictionary of Application form
    Returns: Updated supporting document entity and avg matching score
  """
  print("===============AF======",af_dict["entities"])
  print("===============SD======",sd_dict["entities"])
  matching = compare_json(af_dict["entities"], sd_dict["entities"],
                          sd_dict["document_class"], af_dict["document_class"],
                          af_dict["context"])
  Logger.info(matching)
  print("========Matching OP========",matching)
  if matching:
    return (matching[:len(matching) - 1], matching[-1]["Avg Matching Score"])
  else:
    return None


def update_matching_status(case_id: str,
                           uid: str,
                           status: str,
                           entity: Optional[List[dict]] = None,
                           matching_score: Optional[float] = None):
  """
    Makes api calls to DSM service to update document status for matching
  """
  Logger.info(f"Updating Matching status for case_id {case_id} and uid {uid}")
  response = None
  if status.lower() == "success":
    base_url = "http://document-status-service/document_status_service/"\
      "v1/update_matching_status"
    req_url = f"{base_url}?case_id={case_id}&uid={uid}&status={status}"\
    f"&entity={entity}&matching_score={matching_score}"

    response = requests.post(req_url, json=entity)
    if response.status_code == 200:
      return {"status": "success"}
    else:
      return {"status": "failed"}
  else:
    base_url = "http://document-status-service/document_status_service/"\
      "v1/update_matching_status"
    req_url = f"{base_url}?case_id={case_id}&uid={uid}&status={status}"
    response = requests.post(req_url)
    if response.status_code == 200:
      return {"status": "success"}
    else:
      return {"status": "failed"}


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
                500 : HTTPException: Internal Server Error if something fail
    """
  try:

    #Get Application form data with the same caseid
    af_doc = Document.collection.filter(case_id=case_id).filter(
        active="active").filter(document_type="application_form").get()

    if af_doc:
      Logger.info(f"Matching document with case_id {case_id}"\
        " and uid {uid} with the corresponding Application form")

      #Get Supporting Document data from DB
      sd_doc = Document.find_by_uid(uid)

      sd_dict = copy.deepcopy(sd_doc.to_dict())
      af_dict = copy.deepcopy(af_doc.to_dict())

      #getting json matching result
      matching_result = get_matching_score(af_dict, sd_dict)
      Logger.info(matching_result)

      #If the matching result is not null update the status in DB
      if matching_result:
        updated_entity = matching_result[0]
        overall_score = matching_result[1]

        #Updating document status
        dsm_status = update_matching_status(
            case_id,
            uid,
            "success",
            entity=updated_entity,
            matching_score=overall_score)

        if dsm_status["status"].lower() == "success":
          Logger.info(
              f"Matching document with case_id {case_id} and "\
                f"uid {uid} was successful"
          )
          return {"status": "success", "score": overall_score}
        else:
          Logger.error(
              f"Matching document with case_id {case_id} and "\
                f"uid {uid} Failed. Doc status not updated"
          )
          raise HTTPException(
              status_code=500,
              detail="Document Matching failed.Status failed to update")

      else:
        Logger.error(f"Matching document with case_id {case_id} and uid {uid}"\
          f" Failed. Error in geting Matching score")
        raise HTTPException(status_code=500,detail="Document Matching failed"\
          "Error in getting matching score")

    else:
      Logger.error(f"Error while matching document with case_id {case_id}"\
        f" and uid {uid}."\
          f" Application form not found with given case_id:{case_id}")
      raise HTTPException(
          status_code=404, detail="No supporting Application found")

  except HTTPException as e:
    dsm_status = update_matching_status(case_id, uid, "failed")
    Logger.error(
        f"Error while matching document with case_id {case_id} and uid {uid}")
    print(e)
    Logger.error(e)
    raise e

  except Exception as e:
    dsm_status = update_matching_status(case_id, uid, "failed")
    Logger.error(
        f"Error while matching document with case_id {case_id} and uid {uid}")
    Logger.error(e)
    print(e)
    raise HTTPException(
        status_code=500, detail="Matching Failed.Something went wrong") from e
