""" reassign endpoints """
from fastapi import APIRouter, Response, status, HTTPException
from common.models import Document
from common.db_client import bq_client
from common.utils.format_data_for_bq import format_data_for_bq
from common.utils.stream_to_bq import stream_document_to_bigquery
from common.utils.copy_gcs_documents import copy_blob
from common.utils.logging_handler import Logger
from common.config import BUCKET_NAME
# disabling for linting to pass
# pylint: disable = broad-except
import re
import datetime
import requests
from models.reassign import Reassign
import fireo
import traceback

router = APIRouter()


@router.post("/reassign_case_id")
async def reassign_case_id(reassign: Reassign, response: Response):
  """
  Reassigns case_id of given document
    Args:
    old_case_id (str): Case id of the supporting
    document which need to be reassigned ,
    uid (str) : unique Id of the supportingdocument
    new_case_id :existing application form case_id
    user : username of person who is reassigning the document
    comment : comment put by user
    Returns:
      200 : Successfully reassigned the document
      404 :document to be reassigne is not found
      404 : new_case_id application not found
      400 : If old case_id and new_case_id is same
      406 : if given document with old case_id is
      application and cannot be reassigned
      500 :  Some unexpected error occured
    """
  try:
    reassign_dict = reassign.dict()
    uid = reassign_dict.get("uid")
    old_case_id = reassign_dict.get("old_case_id")
    new_case_id = reassign_dict.get("new_case_id")
    user = reassign_dict.get("user")
    comment = reassign_dict.get("comment")

    #Check if the old case_id and new_case_id is same
    #send bad request error
    if old_case_id == new_case_id:
      response.status_code = status.HTTP_400_BAD_REQUEST
      response.body = f"The  existing case_id {old_case_id}and new " \
                  f"case_id {new_case_id} is" \
                  f" same enter different case_id"
      return {"message":response.body}



    document = Document.find_by_uid(uid)
    #If document with given uid does not exist send 404
    # not found error
    if document is None:
      Logger.error(f"document to be reassigned with case_id {old_case_id}"
                   f" and uid {uid} does not exist in database")
      response.status_code = status.HTTP_404_NOT_FOUND
      response.body = f"document to be reassigned with case_id {old_case_id} " \
                      f"and uid {uid} does not exist in database"
      return {"message":response.body}

    #if given document with old case_id is application and cannot be
    # reassigned send user response that this file is not acceptable
    if document.document_type == "application_form":
      Logger.error(
          f"document to be reassigned with case_id {old_case_id}"
          f" and uid {uid} is application form and cannot be reassigned")
      response.status_code = status.HTTP_406_NOT_ACCEPTABLE
      response.body =f"document to be reassigned with case_id {old_case_id}" \
                  f" and uid {uid} is application form and cannot be reassigned"
      return {"message": response.body}
    new_case_id_document  = Document.collection.filter(case_id=new_case_id).\
      filter(document_type ="application_form").get()
    print("After new case_id check")
    print(new_case_id_document)
    #application with new case case_id does not exist in db
    #send 404 not found error
    if not new_case_id_document:
      Logger.error(
          f"Document with case_id {new_case_id} not found for reassign")
      response.status_code = status.HTTP_404_NOT_FOUND
      response.body = f"Application with case_id {new_case_id}" \
      f" does not exist in database to reassigne supporting doc " \
      f"{old_case_id} and uid {uid}"
      return {"message":response.body}

    client = bq_client()
    gcs_source_url = document.url
    document_class = document.document_class
    document_type = document.document_type
    entities = document.entities
    context = document.context
    extraction_score =  document.extraction_score

    #remove the prefix of bucket name from gcs_url to get blob name
    prefix_name = f"gs://{BUCKET_NAME}/"
    source_blob_name = re.sub(prefix_name, "", gcs_source_url, 1)

    #remove the prefix of old_case_id and give new case_id for
    # destination folder in gcs
    destination_blob_name = re.sub(old_case_id, new_case_id, source_blob_name,
                                   1)
    print("-----------destination blob name in api------",
          destination_blob_name)
    status_copy_blob = copy_blob(BUCKET_NAME, source_blob_name,
                                 destination_blob_name)

    # check if moving file in gcs is sucess
    if status_copy_blob != "success":
      response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
      response.body = f"Error in copying files in " \
     f"gcs bucket from source folder {old_case_id},destination" \
          f" {new_case_id} "
      return {"message": response.body}
    print("----------Updating firestore-----------")
    #Update Firestore databse
    document.case_id = new_case_id
    updated_url = prefix_name + destination_blob_name
    document.url = updated_url
    # Update HITL audit trail for reassigned action
    hitl_audit_trail = {
        "status": "reassigned",
        "timestamp": str(datetime.datetime.utcnow()),
        "user": user,
        "comment": comment,
        "action": f"reassigned from {old_case_id} to {new_case_id}"
    }
    document.hitl_status = fireo.ListUnion([hitl_audit_trail])
    document.update()
    print("updating bigquery")
    #Update Bigquery database
    entities_for_bq = format_data_for_bq(entities)
    update_bq = stream_document_to_bigquery(client, new_case_id, uid,
                                document_class, document_type,
                              entities_for_bq)
    print("--------firestore db ----------------")
    # status_process_task =
    response_process_task = call_process_task(new_case_id,uid,document_class,
    document_type,updated_url,context,extraction_score)
    if update_bq == [] and response_process_task.status_code == 202:
      Logger.info(
          f"ressign case_id from {old_case_id} to {new_case_id} is successfull")
      return {"status": "success", "url": document.url}
    else:
      print("inside else")
      response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
      response.body = "Error in updating bigquery database"
  except Exception as e:
    print("Inside except")
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=500, detail="Error "
        "in reassigning document") from e


def call_process_task(case_id: str, uid: str, document_class: str,
                      document_type: str, gcs_uri: str,context: str,extraction_score: float):
  """
    Starts the process task API after reassign
  """

  data = {
      "case_id": case_id,
      "uid": uid,
      "context":context,
      "gcs_url": gcs_uri,
      "document_class": document_class,
      "document_type": document_type,
      "extraction_score":extraction_score
  }
  payload = {"configs": [data]}
  base_url = "http://upload-service/upload_service" \
            "/v1/process_task?is_reassign=true"
  print("params for process task", base_url, payload)
  Logger.info(f"Params for process task {payload}")
  response = requests.post(base_url,json=payload)
  return response

