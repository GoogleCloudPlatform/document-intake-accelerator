""" Document status endpoints """
from common.config import BUCKET_NAME
from common.models import Document
from common.utils.logging_handler import Logger
import fireo
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
import datetime
import traceback

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
       200 : PDF files are successfully saved in db
       500 : If something fails
     """
  try:
    document = Document()
    document.case_id = case_id
    document.upload_timestamp = str(datetime.datetime.utcnow())
    document.context = context
    document.uid = document.save().id
    document.active = "active"
    document.save()
    return {"status": "Success", "uid": document.uid}
  except Exception as e:
    Logger.error(f"Error in create document for case_id {case_id} "
                 f"and {filename}")
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=500,
        detail=f"Error in creating documents for case_id {case_id}") from e


@router.post("/update_classification_status")
async def update_classification_status(
    case_id: str,
    uid: str,
    status: str,
    is_hitl: Optional[bool] = False,
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
       200 : PDF files are successfully saved in db
       500 :Internal Server Error if something fails
       """
  try:
    document = Document.find_by_uid(uid)
    if status == "success":
      #update  the document type and document class
      document.document_class = document_class
      document.document_type = document_type
      document.is_hitl_classified = is_hitl
      system_status = {
          "is_hitl" : is_hitl,
          "stage": "classification",
          "status": "success",
          "timestamp": str(datetime.datetime.utcnow())
      }
      document.system_status = fireo.ListUnion([system_status])
      document.update()
      #Check if document with same case_id , document type and
      #document class already exists
      #in db if yes mark the old documents as inactive
      documents = Document.collection.filter(case_id=case_id).filter(
          document_type=document_type).filter(
              document_class=document_class).fetch()
      documents_list = list(documents)
      for i in documents_list:
        if i.uid == uid:
          i.active = "active"
          i.update()
        else:
          i.active = "inactive"
          i.update()
    else:
      system_status = {
          "stage": "classification",
          "status": status,
          "timestamp": str(datetime.datetime.utcnow())
      }
      document.system_status = fireo.ListUnion([system_status])
      document.update()
    return {"status": "Success", "case_id": case_id, "uid": uid}
  except Exception as e:
    Logger.error(f"Error in updating classification status for "
                 f"case_id {case_id} and uid {uid}")
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=500,
        detail="Error in updating classification status") from e


@router.post("/update_extraction_status")
async def update_extraction_status(case_id: str,
                                   uid: str,
                                   status: str,
                                   entity: Optional[List[Dict]] = None,
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
           200 : Database updated successfully
           """
  try:
    document = Document.find_by_uid(uid)
    if status == "success":
      system_status = {
          "stage": "extraction",
          "status": "success",
          "timestamp": str(datetime.datetime.utcnow())
      }
      document.system_status = fireo.ListUnion([system_status])
      document.entities = entity
      document.extraction_score = extraction_score
      document.update()
    else:
      system_status = {
          "stage": "extraction",
          "status": "fail",
          "timestamp": str(datetime.datetime.utcnow())
      }
      document.system_status = fireo.ListUnion([system_status])
      document.update()
    return {"status": "Success", "case_id": case_id, "uid": uid}
  except Exception as e:
    Logger.error(f"Error in updating extraction status case_id {case_id} "
                 f"and uid {uid}")
    Logger.error(e)
    raise HTTPException(
        status_code=500, detail="Error in updating"
        " extraction status") from e


@router.post("/update_validation_status")
async def update_validation_status(case_id: str,
                                   uid: str,
                                   status: str,
                                   entities : List[Dict],
                                   validation_score: Optional[float] = None):
  """takes case_id , uid , validation status of validation
  service as input and updates in database

         Args:
           case_id (str): Case id of the files
           uid (str): uid for document
           validation_score:  validation score return
           status : status of validation service
         Returns:
           200 : Database updated successfully
           505 : If something fails
          """
  try:
    print("=====Inside validation document update======",type(validation_score))
    print("=====Inside validation document update entities======",type(entities))
    document = Document.find_by_uid(uid)
    if status == "success":
      document.validation_score = validation_score
      document.entities = entities
      print("Insiide documentt status",validation_score,entities)

      system_status = {
          "stage": "validation",
          "status": "success",
          "timestamp": str(datetime.datetime.utcnow())
      }
      document.system_status = fireo.ListUnion([system_status])
      document.update()
    else:
      system_status = {
          "stage": "validation",
          "status": "fail",
          "timestamp": str(datetime.datetime.utcnow())
      }
      document.system_status = fireo.ListUnion([system_status])
      document.update()
    return {"status": "Success", "case_id": case_id, "uid": uid}
  except Exception as e:
    Logger.error(f"Error in updating validation status"
                 f" for case_id {case_id} and uid {uid}")
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=500, detail="Error in updating"
        " validation status") from e


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
               200 : Database updated successfully
               404 :Document not found
               505 : If something fails
           """
  try:
    document = Document.find_by_uid(uid)
    if status == "success":
      system_status = {
        "stage": "matching",
        "status": "success",
        "timestamp": str(datetime.datetime.utcnow())
      }
      document.system_status = fireo.ListUnion([system_status])
      document.update()
      document.matching_score = matching_score
      document.entities = entity
      document.save()
    else:
      system_status = {
        "stage": "matching",
        "status": "fail",
        "timestamp": str(datetime.datetime.utcnow())
      }
      document.system_status = fireo.ListUnion([system_status])
      document.update()
    return {"status": "Success", "case_id": case_id, "uid": uid}
  except Exception as e:
    Logger.error(f"Error in updating matching status for"
                 f" case_id {case_id} and uid {uid}")
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=500, detail="Error in updating matching status") from e


@router.post("/update_autoapproved_status")
async def update_autoapproved(case_id: str, uid: str, status: str,
                              autoapproved_status: str, is_autoapproved: str):
  try:
    document = Document.find_by_uid(uid)
    if status == "success":
      document.auto_approval = autoapproved_status
      system_status = {
          "stage": "auto_approval",
          "status": "success",
          "timestamp": str(datetime.datetime.utcnow())
      }
      document.system_status = fireo.ListUnion([system_status])
      document.is_autoapproved = is_autoapproved
      document.update()
    else:
      system_status = {
          "stage": "auto_approval",
          "status": "fail",
          "timestamp": str(datetime.datetime.utcnow())
      }
      document.system_status = fireo.ListUnion([system_status])
      document.update()
    return {"status": "Success", "case_id": case_id, "uid": uid}
  except Exception as e:
    raise HTTPException(
        status_code=500, detail="Error in "
        "updating the autoapproval status") from e


@router.post("/create_documet_json_input")
async def create_documet_json_input(case_id: str, document_class: str,
                                    document_type: str, entity: List[dict],
                                    context: str):
  """takes case_id , uid , entity, status  of matching
   service as input and updates in database

  Args:
   case_id (str): Case id of the files
   uid (str): uid for document
   matching_score:  matching score return
   status : status of validation service
  Returns:
   200 : Database updated successfully """
  try:
    document = Document()
    document.case_id = case_id
    document.entities = entity
    document.upload_timestamp = str(datetime.datetime.utcnow())
    system_status = {
        "stage": "uploaded",
        "status": "success",
        "timestamp": str(datetime.datetime.utcnow())
    }
    document.system_status = fireo.ListUnion([system_status])
    document.active = "active"
    document.document_class = document_class
    document.document_type = document_type
    document.context = context
    document.uid = document.save().id
    gcs_base_url = f"gs://{BUCKET_NAME}"
    document.url = f"{gcs_base_url}/{case_id}/{document.uid}" \
                f"/input_data_{case_id}_{document.uid}.json"
    document.save()
    return {"status": "success", "uid": document.uid}
  except Exception as e:
    Logger.error("Error in  creating document")
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=500, detail="Error in"
        " creating the document") from e
