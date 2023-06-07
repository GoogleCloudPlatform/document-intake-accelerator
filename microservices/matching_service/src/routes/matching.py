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

""" Matching endpoints"""
from fastapi import APIRouter, HTTPException, status
import requests
from common.models import Document
from common.utils.logging_handler import Logger
from common.config import STATUS_IN_PROGRESS, STATUS_SUCCESS, STATUS_ERROR

from typing import Optional, List
from utils.json_matching.match_json import compare_json
# disabling for linting to pass
# pylint: disable = broad-except
import copy
import traceback

router = APIRouter()
SUCCESS_RESPONSE = {"status": STATUS_SUCCESS}
FAILED_RESPONSE = {"status": STATUS_ERROR}


def get_matching_score(af_dict: dict, sd_dict: dict):
  """
    Makes call to json matching function and returns the result

    Args: af_dict: Dictionary of Application form
          sd_dict: Dictionary of Supporting Document
    Returns: Updated supporting document entity and avg matching score
  """
  print("Application form: ", af_dict["entities"])
  print("Supporting document: ", sd_dict["entities"])
  matching = compare_json(af_dict["entities"], sd_dict["entities"],
                          sd_dict["document_class"], af_dict["document_class"],
                          af_dict["context"])
  Logger.info(matching)
  print("Matching Output: ", matching)
  if matching:  # TODO fix if matching not setup, just skip
    if len(matching) == 0:
      # Skipp Matching
      return 0
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
  if status == STATUS_SUCCESS:
    base_url = "http://document-status-service/document_status_service/"\
      "v1/update_matching_status"
    req_url = f"{base_url}?case_id={case_id}&uid={uid}&status={status}"\
    f"&entity={entity}&matching_score={matching_score}"

    return requests.post(req_url, json=entity)

  else:
    base_url = "http://document-status-service/document_status_service/"\
      "v1/update_matching_status"
    req_url = f"{base_url}?case_id={case_id}&uid={uid}&status={status}"
    return requests.post(req_url)


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

    # # Temp Disable Matching For Now
    # return {"status": STATUS_SUCCESS, "score": 0}
    #Get Application form data with the same caseid
    af_doc = Document.collection.filter(case_id=case_id).filter(
        active="active").filter(document_type="application_form").get()

    if af_doc and af_doc.entities is not None:
      Logger.info(f"Matching document with case_id {case_id}"
        f" and uid {uid} with the corresponding Application form")

      #Get Supporting Document data from DB
      sd_doc = Document.find_by_uid(uid)

      sd_dict = copy.deepcopy(sd_doc.to_dict())
      af_dict = copy.deepcopy(af_doc.to_dict())

      #getting json matching result
      matching_result = get_matching_score(af_dict, sd_dict)
      Logger.info(matching_result)
      print("matching_result:")
      print(matching_result)

      #If the matching result is not null update the status in DB
      if matching_result:
        updated_entity = matching_result[0]
        overall_score = matching_result[1]

        #Updating document status
        dsm_status = update_matching_status(
            case_id,
            uid,
            STATUS_SUCCESS,
            entity=updated_entity,
            matching_score=overall_score)

        print(f"dsm_status = {dsm_status}")

        if dsm_status.status_code == status.HTTP_200_OK:
          Logger.info(
              f"Matching document with case_id {case_id} and "
                f"uid {uid} was successful"
          )
          return {"status": STATUS_SUCCESS, "score": overall_score}
        else:
          Logger.error(
              f"Matching document with case_id {case_id} and "
                f"uid {uid} Failed. Doc status not updated"
          )
          raise HTTPException(
              status_code=500,
              detail="Document Matching failed.Status failed to update")

      else:
        # TODO Temp workaround
        return {"status": STATUS_SUCCESS, "score": 0}
        # Logger.error(f"Matching document with case_id {case_id} and uid {uid}"\
        #   f" Failed. Error in geting Matching score")
        # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Document Matching failed"\
        #   "Error in getting matching score")

    else:
      Logger.warning(f"Matching with case_id {case_id} and uid {uid}: "
          f"Application form with entities not found with given case_id: {case_id}")
      return {"status": STATUS_SUCCESS, "score": 0}
      # No matching => Nothing to match unless it is Configured!


  except HTTPException as e:
    dsm_status = update_matching_status(case_id, uid, STATUS_ERROR)
    Logger.error(
        f"HTTPException while matching document with case_id {case_id} and uid {uid}"
    )
    print(e)
    Logger.error(e)
    Logger.error(traceback.format_exc().replace("\n", " "))
    raise e

  except Exception as e:
    print("ERROR: match_document error:")

    dsm_status = update_matching_status(case_id, uid, STATUS_ERROR)
    Logger.error(
        f"Error while matching document with case_id {case_id} and uid {uid}")
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    print(err)

    raise HTTPException(status_code=500, detail=str(e)) from e
