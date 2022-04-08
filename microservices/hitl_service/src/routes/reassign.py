""" hitl endpoints """
from fastapi import APIRouter, HTTPException, Response , UploadFile, File,status
from typing import Optional, List
from typing import Optional
from common.models import Document
from common.db_client import bq_client
from common.utils.format_data_for_bq import format_data_for_bq
from common.utils.stream_to_bq import stream_document_to_bigquery
from common.utils.logging_handler import Logger
from common.config import BUCKET_NAME
# disabling for linting to pass
# pylint: disable = broad-except
import re
from google.cloud import storage
from models.reassign import Reassign

router = APIRouter()


@router.post("/reassign_case_id")
# async def reassign_case_id(reassign : Reassign ,files: List[UploadFile] = File(...)):
async def reassign_case_id(reassign: Reassign, response : Response):

  """ reports all data to user
            the database
          Returns:
              200 : fetches all the data from database
    """
  # try:
  reassign_dict = reassign.dict()
  print(reassign)
  print("=========Reassign=========",type(reassign))
  print(reassign_dict)
  # uid = "ssss"
  uid = reassign_dict.get("uid")
  old_case_id = reassign_dict.get("old_case_id")
  new_case_id =  reassign_dict.get("new_case_id")
  document = Document.find_by_uid(uid)
  if document == None :
    response.status_code =  status.HTTP_404_NOT_FOUND
    response.body = f"document to be reassigned with case_id {old_case_id} " \
                    f"and uid {uid} does not exist in database"
    return response
  if document.document_type == "application_form":
    response.status_code =  status.HTTP_406_NOT_ACCEPTABLE
    response.body =f"The application form cannot reassigned"
    return response
  client = bq_client()
  gcs_source_url =  document.url
  document_class = document.document_class
  document_type =  document.document_type
  entities =  document.entities
  storage_client = storage.Client()
  source_bucket = storage_client.bucket(BUCKET_NAME)
  blob_name = re.sub("gs://document-upload-test/","",gcs_source_url,1)
  print("++++++++++++++++++++++++++++++" , blob_name)
  source_blob = source_bucket.blob(blob_name)
  destination_bucket = storage_client.bucket(BUCKET_NAME)
  destination_blob_name = re.sub(old_case_id ,new_case_id,blob_name,1)
  print("+++++++++++++++++++++++++++++",destination_blob_name)
  blob_copy = source_bucket.copy_blob(
    source_blob, destination_bucket, destination_blob_name
  )
  print(
    "Blob {} in bucket {} copied to blob {} in bucket {}.".format(
      source_blob.name,
      source_bucket.name,
      blob_copy.name,
      destination_bucket.name,
    )
  )
  document.case_id =  new_case_id
  document.update()
  entities_for_bq =  format_data_for_bq(entities)
  update_bq = stream_document_to_bigquery(client, new_case_id, uid,document_class, document_type,entities_for_bq)
  print("This is old case_id",old_case_id)
  if update_bq == []:
    return {"status":"success", "url": document.url }
  else:
    return {"status":"Cannot update bigquery"}
  # except Exception as e:
  #   print(e)
  #   Logger.error(e)
  #   raise HTTPException(
  #       status_code=500, detail="Error in fetching documents") from e
  #



