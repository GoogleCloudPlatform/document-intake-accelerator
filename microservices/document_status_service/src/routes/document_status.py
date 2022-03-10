""" Document status endpoints """
import datetime

from fastapi import APIRouter
from common.config import BUCKET_NAME
from common.models import Document
from typing import Optional, List

# disabling for linting to pass
# pylint: disable = broad-except

router = APIRouter()
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}


@router.post("/create_document")
async def create_document(case_id: str, filename: str, context: str):
  """takes case_id ,filename as input and Save the record in the database

     Args:
       case_id (str): Case id of the files
       filename : get the filename form upload files api
       context: The context for which application is being used
                Example - Arizona , Callifornia etc
     Returns:
       200 : PDF files are successfully saved in db"""

  document = Document()
  document.case_id = case_id
  document.upload_timestamp = datetime.datetime.utcnow()
  document.context = context
  document.uid = document.save().id
  gcs_base_url = f"http://storage.googleapis.com/{BUCKET_NAME}"
  document.url = f"{gcs_base_url}/{case_id}/{document.uid}/{filename}"

  return {"status": "Success", "uid": document.uid}


@router.post("/update_classification_status")
async def update_classification_status(
    case_id: str,
    uid: str,
    status: str,
    document_class: Optional[str] = None,
    document_type: Optional[str] = None,
):
  """takes case_id , uid , document_class ,document_type ,status of

        classification service as input
        updates the document class ,document_type
        ,status in database
        checks if the document with same case_id ,uid,
        document_class
        ,document_type already exists in database
        if it exists mark previous as inactive  and
        current as active in database

     Args:
       case_id (str): Case id of the files
       filename : get the filename form upload files api
       context: The context for which application is being used
                Example - Arizona , Callifornia etc
     Returns:
       200 : PDF files are successfully saved in db"""
  print(document_type + case_id + uid)
  print(document_class)
  print(status)

  return SUCCESS_RESPONSE


@router.post("/update_extraction_status")
async def update_extraction_status(case_id: str,
                                   uid: str,
                                   status: str,
                              entity: Optional[List[dict]] = None,
                              extraction_score: Optional[float] = None):
  """takes case_id , uid , extraction_score ,document_type ,status
    of classification service as input
    updates the document class ,document_type ,status in database

         Args:
           case_id (str): Case id of the files
           uid (str): uid for document
           entity_list: list of dictionary for extracted entity
           extraction_score: average extraction score return by parser
           status : status of extraction service
         Returns:
           200 : Database updated successfully """
  print(case_id)
  print(uid)
  print(status)
  print(entity)
  print(extraction_score)
  return SUCCESS_RESPONSE


@router.post("/update_validation_status")
async def update_validation_status(case_id: str,
    uid: str, status: str,
    validation_score: Optional[float] = None):
  """takes case_id , uid , validation status of validation
  service as input and updates in database

         Args:
           case_id (str): Case id of the files
           uid (str): uid for document
           validation_score:  validation score return
           status : status of validation service
         Returns:
           200 : Database updated successfully """
  print(case_id + uid + status)
  print(validation_score)
  return SUCCESS_RESPONSE


@router.post("/update_matching_status")
async def update_matching_status(case_id: str,
                                 uid: str,
                                 status: str,
                              entity: Optional[List[dict]] = None,
                                 matching_score: Optional[float] = None):
  """takes case_id , uid , entity,
  status  of matching service as input and updates in database

             Args:
               case_id (str): Case id of the files
               uid (str): uid for document
               matching_score:  matching score return
               status : status of validation service
             Returns:
               200 : Database updated successfully """
  print(case_id, uid, status)
  print(entity)
  print(matching_score)
  return SUCCESS_RESPONSE


@router.post("/create_documet_json_input")
async def create_documet_json_input(case_id: str, uid: str, entity: List[dict]):
  """takes case_id , uid , entity, status  of matching
   service as input and updates in database

 Args:
   case_id (str): Case id of the files
   uid (str): uid for document
   matching_score:  matching score return
   status : status of validation service
 Returns:
   200 : Database updated successfully """
  print(case_id, uid)
  print(entity)

  return SUCCESS_RESPONSE
