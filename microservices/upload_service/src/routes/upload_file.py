""" Upload and process task api endpoints """

import uuid
import requests
import traceback
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.concurrency import run_in_threadpool
from typing import Optional, List
from schemas.input_data import InputData
import utils.upload_file_gcs_bucket as ug
from common.utils.logging_handler import Logger
from common.models import Document
from common.utils.publisher import publish_document
from common.config import BUCKET_NAME
import datetime

# pylint: disable = broad-except ,literal-comparison
router = APIRouter()



@router.post("/upload_files")
async def upload_file(
    context: str,
    files: List[UploadFile] = File(...),
    case_id: Optional[str] = None,
    comment: Optional[str] = None,

):
  """Uploads files to the GCS bucket and Save the record in the database

  Args:
    case_id (str): Case id of the files it's optionl ,
    state (str) : state for which the application will be used
    list of files : to get the list of documents from user
  Returns:
    200 : PDF files are successfully uploaded
    422 : If file other than pdf is uploaded by user
    500 :Error in uploading documents
    """
  #checking if all uploaded files are pdf documents
  for file in files:
    if not file.filename.lower().endswith(".pdf"):
      Logger.error("Uploaded file is not a pdf document")
      raise HTTPException(
          status_code=422, detail="Please upload"
          " all pdf files")
    #generate a case_id if not provided by the user
  if case_id is None:
    case_id = str(uuid.uuid1())
  uid_list = []
  try:
    for file in files:
      #create a record in database for uploaded document
      output = create_document(case_id, file.filename, context)
      uid = output
      uid_list.append(uid)
      #Upload document in GCS bucket
      status = await run_in_threadpool(ug.upload_file, case_id, uid, file)
      #check the uploaded document status
      if status != "success":

        #Update the document upload in GCS as failed
        document = Document.find_by_uid(uid)
        system_status = {
            "stage": "upload",
            "status": "fail",
            "timestamp": str(datetime.datetime.utcnow()),
            "comment": comment
        }
        document.system_status = [system_status]
        document.update()
        raise HTTPException(
            status_code=500,
            detail="Error "
            "in uploading document in gcs bucket")
      Logger.info(f"File with case_id {case_id} and uid {uid}"
                  f" uploaded successfullly in GCS bucket")
      #Update the document upload as success in DB
      document = Document.find_by_uid(uid)
      print("uid is ",uid)
      print("Document is ",document)
      gcs_base_url = f"gs://{BUCKET_NAME}"
      document.url = f"{gcs_base_url}/{case_id}/{uid}/{file.filename}"
      system_status = {
          "stage": "uploaded",
          "status": "success",
          "timestamp": str(datetime.datetime.utcnow()),
          "comment": comment
      }
      document.system_status = [system_status]
      document.update()
      pubsub_msg = f"batch moved to bucket name{case_id}{uid}"
      message_dict = {"message": pubsub_msg,"gcs_url":
      document.url, "caseid": case_id ,"uid":uid ,"context":context}
      publish_document(message_dict)
    # background_tasks.add_task(run_pipeline,case_id,uid,document.url)
    # Logger.info(f"Files with case id {case_id} uploaded"
    #               f" successfully")
    Logger.info(f"Files with case id {case_id} uploaded"
                  f" successfully")
    return {
        "status": f"Files with case id {case_id} uploaded"
                  f"successfully, the document"
                  f" will be processed in sometime ",
        "case_id": case_id,
        "uid_list": uid_list,
    }
    # if response.status_code == 202:
    #   Logger.info(f"Files with case id {case_id} uploaded"
    #               f" successfully")
    #   return {
    #       "status": f"Files with case id {case_id} uploaded"
    #                 f"successfully, the document"
    #                 f" will be processed in sometime ",
    #       "case_id": case_id,
    #       "uid_list": uid_list,
    #   }
    # else:
    #   return {
    #     "status": f"Files with case id {case_id} uploaded"
    #               f"successfully,Error in calling process task ",
    #     "case_id": case_id,
    #     "uid_list": uid_list,
    #   }

  except Exception as e:
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=500, detail="Error "
        "in uploading document") from e


@router.post("/upload_json")
async def upload_data_json(input_data: InputData):
  """Uploads input  to the GCS bucket and Save the record in the database
    Args:
       input_data: input data schema for JSON
    Returns:
       200 : data successfully saved in system
       422 : incorrect data passed
       500 : if something fails
     """
  try:
    input_data = dict(input_data)
    entity = []
    document_class = input_data.pop("document_class")
    document_type = input_data.pop("document_type")
    context = input_data.pop("context")
    case_id = input_data.pop("case_id")
    #If case-id is none generate a new case_id
    if case_id is None:
      case_id = str(uuid.uuid1())
    #Converting Json to required format
    for key, value in input_data.items():
      entity.append({"entity": key, "value": value, "extraction_confidence": 1})
    uid = create_document_from_data(case_id, document_type, document_class,
                                    context, entity)

    status = ug.upload_json_file(case_id, uid, str(entity))
    return {"status": status, "input_data": input_data, "case_id": case_id}
  except Exception as e:
    Logger.error(e)
    raise HTTPException(status_code=500, detail="Error "
                                    "in uploading document")from e




def create_document_from_data(case_id, document_type, document_class, context,
                              entity):
  base_url = "http://document-status-service/document_status_service/v1/"
  req_url = f"{base_url}create_documet_json_input"
  response = requests.post(
      f"{req_url}?case_id={case_id}&document_class={document_class}"
      f"&document_type={document_type}&context={context}",
      json=entity)
  response = response.json()
  uid = response["uid"]
  return uid


def create_document(case_id, filename, context):
  base_url = "http://document-status-service/document_status_service/v1/"
  req_url = f"{base_url}create_document"
  response = requests.post(
      f"{req_url}?case_id={case_id}&filename={filename}&context={context}")
  response = response.json()
  uid = response["uid"]
  return uid
