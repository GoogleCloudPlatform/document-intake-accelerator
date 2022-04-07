""" hitl endpoints """
from fastapi import APIRouter, HTTPException, Response , UploadFile, File
from typing import Optional, List
from typing import Optional
from common.models import Document
from common.utils.logging_handler import Logger
from common.config import BUCKET_NAME
# disabling for linting to pass
# pylint: disable = broad-except
import datetime
from google.cloud import storage
from models.reassign import Reassign

router = APIRouter()


@router.post("/reassign_case_id")
# async def reassign_case_id(reassign : Reassign ,files: List[UploadFile] = File(...)):
async def reassign_case_id(reassign: Reassign):

  """ reports all data to user
            the database
          Returns:
              200 : fetches all the data from database
    """
  # try:
  # payload = payload.dict()
  # old_case_id = payload.get('old_case_id')
  # new_case_id = payload.get('new_case_id')
  # uid = payload.get('uid')
  reassign_dict = reassign.dict()
  # print(reassign)
  # print(type(reassign))
  print(reassign)
  print("=========Reassign=========",type(reassign))
  print(reassign_dict)
  # uid = "ssss"
  uid = reassign_dict.get("uid")
  old_case_id = reassign_dict.get("old_case_id")
  new_case_id =  reassign_dict.get("new_case_id")
  document = Document.find_by_uid(uid)
  storage_client = storage.Client()
  print("This is old case_id",old_case_id)
  source_blob_name = f"{old_case_id}/{uid}"
  source_bucket = storage_client.bucket("document-upload-test")
  source_blob = source_bucket.blob(source_blob_name)
  print("==sources bucket",source_bucket)
  print("source blob name", source_blob)
  destination_bucket = storage_client.bucket("document-upload-test")
  destination_blob_name = f"{new_case_id}/{uid}"
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
  if document.document_type == "application_form":
    print(document.url , document.document_type ,document.document_class)
  elif document.document_type == "supporting_documents":
    print("gg")
  return {"status":"success", "url": document.url }
  # except Exception as e:
  #   print(e)
  #   Logger.error(e)
  #   raise HTTPException(
  #       status_code=500, detail="Error in fetching documents") from e
  #



