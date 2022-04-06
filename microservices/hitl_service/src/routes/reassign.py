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
async def reassign_case_id(reassign : Reassign ,files: List[UploadFile] = File(...)):
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
  # reassign_dict = reassign.dict()
  # print(reassign)
  # print(type(reassign))
  print(reassign)
  uid = "ssss"
  document = Document.find_by_uid(uid)
  for file in files:
    print(files.filename)
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



