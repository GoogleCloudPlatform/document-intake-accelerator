""" hitl endpoints """
from io import BytesIO
import os
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional
from common.models import Document
from common.utils.logging_handler import Logger
# disabling for linting to pass
# pylint: disable = broad-except
import datetime
from google.cloud import storage
from common.config import BUCKET_NAME

router = APIRouter()
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}


@router.get("/report_data")
async def report_data():
  """ reports all data to user
            the database
          Returns:
              200 : fetches all the data from database
    """
  doc_list = []
  try:
    docs = Document.collection.filter("active", "==", "active").fetch()
    for d in docs:
      doc_list.append(d.to_dict())
    response = {"status": "Success"}
    response["data"] = doc_list
    return response

  except Exception as e:
    print(e)
    Logger.error(e)
    raise HTTPException(
        status_code=500, detail="Error in fetching documents") from e
  

@router.post("/get_document")
async def get_document(uid: str):
  """ Returns a single document to user using uid from the database
        Args : uid - Unique ID for every document
        Returns:
          200 : Fetches a single document from database
    """
  try:
    doc = Document.find_by_uid(uid)
    if not doc or not doc.to_dict()["active"] == "active":
      response = {"status": "Failed"}
      response["detail"] = "No Document found with the given uid"
      return response
    response = {"status": "Success"}
    response["data"] = doc
    return response

  except Exception as e:
    print(e)
    Logger.error(e)
    raise HTTPException(
        status_code=500, detail="Error in fetching documents") from e
  

@router.post("/get_queue")
async def get_queue(hitl_status: str):
  """
  Fetches a queue of all documents with the same hitl status
  (approved,rejected,review or pending) from firestore
  Args: hitl_queue - status of the required queue
  Returns:
    200 : Fetches a list of documents with the same hitl_status from Firestore
    500 : If there is any error during fetching from firestore
  """
  if hitl_status.lower() not in ["approved", "rejected", "pending", "review"]:
    raise HTTPException(status_code=400, detail="Invalid Parameter")
  try:
    docs = list(Document.collection.filter("active", "==", "active").fetch())
    print(docs)
    result_queue = []
    for d in docs:
      status_class = ""
      doc_dict = d.to_dict()
      print(doc_dict)
      hitl_trail = doc_dict["hitl_status"]
      print(doc_dict["is_autoapproved"])
      if hitl_trail:
        status_class = hitl_trail[-1]["status"].lower()
      else:
        if doc_dict["auto_approval"]:
          status_class = doc_dict["auto_approval"].lower()
      if status_class == hitl_status.lower():
        result_queue.append(doc_dict)
    
    response = {"status": "Success"}
    response["data"] = result_queue
    return response

  except Exception as e:
    print(e)
    Logger.error(e)
    raise HTTPException(
        status_code=500, detail="Error during fetching from Firestore") from e
  

@router.post("/update_entity")
async def update_entity(uid: str, updated_doc: dict):
  """
    Updates the entity values
    Args : uid - unique id,
    updated_doc - document with updated values in entities field
    Returns 200 : Updation was successful
    Returns 500 : If something fails
  """
  try:
    doc = Document.find_by_uid(uid)
    if not doc or not doc.to_dict()["active"] == "active":
      response = {"status": "Failed"}
      response["detail"] = "No Document found with the given uid"
      return response
    doc.entities = updated_doc["entities"]
    doc.update()
    return {"status": "Success"}
  except Exception as e:
    print(e)
    Logger.error(e)
    raise HTTPException(
        status_code=500, detail="Failed to update entity") from e


@router.post("/update_hitl_status")
async def update_hitl_status(uid: str,
                             status: str,
                             user: str,
                             comment: Optional[str] = ""):
  """
    Updates the HITL status
    Args : uid - unique id,status - hitl status,
    user-username, comment - notes or comments by user
    Returns 200 : Updation was successful
    Returns 500 : If something fails
  """
  if status.lower() not in ["approved", "rejected", "pending", "review"]:
    raise HTTPException(status_code=400, detail="Invalid Parameter")
  try:
    timestamp = str(datetime.datetime.utcnow())
    print(timestamp)
    hitl_status = {
      "timestamp": timestamp,
      "status": status.lower(),
      "user": user,
      "comment": comment
    }
  
    doc = Document.find_by_uid(uid)
    if not doc or not doc.to_dict()["active"] == "active":
      response = {"status": "Failed"}
      response["detail"] = "No Document found with the given uid"
      return response
    if doc:
      existing_hitl = doc.to_dict()["hitl_status"] if doc.to_dict(
      )["hitl_status"] is not None else []
      print(existing_hitl)
      existing_hitl.append(hitl_status)
      doc.hitl_status = existing_hitl
      doc.update()
    return {"status": "Success"}
  except Exception as e:
    print(e)
    Logger.error(e)
    raise HTTPException(
        status_code=500, detail="Failed to update hitl status") from e

@router.get("/fetch_file")
async def fetch_file(case_id:str, uid:str, download : Optional[bool] = False):
  """
  Fetches and returns the file from GCS bucket
  Args : case_id : str, uid : str
  Returns 200: returns the file and displays it
  Returns 500: If something fails
  """
  try:
    storageClient = storage.Client()
    print(case_id+uid)
    blobs = storageClient.list_blobs(BUCKET_NAME,prefix=case_id+"/"+uid+"/",delimiter="/")
    target_blob = None
    for blob in blobs:
      print(blob.name)
      target_blob = blob
    if target_blob == None:
      print("This 404 ")
      raise FileNotFoundError
    #FileResponse(data)
    print(target_blob.name.split("/")[-1])
    filename = target_blob.name.split("/")[-1]
    
    return_data = target_blob.download_as_bytes()
    async def get_bytegen():
      for d in return_data:
        yield bytes(d)
    print(type(return_data))
    data = bytearray(return_data)
    def get_gen():
      for i in data:
        print(bytes(i))
        yield bytes(i)
    
    data_gen = get_gen()
    d = get_bytegen()
    headers = None
    if download :
      headers = {"Content-Disposition":"attachment;filename="+filename}
    else:
      headers = {"Content-Disposition":"inline;filename="+filename}
    #return StreamingResponse(d,media_type="application/pdf")
    return Response(content = return_data,headers=headers,media_type="application/pdf")
    #return FileResponse(data,media_type="application/pdf")
  except FileNotFoundError as e:
    print(e)
    Logger.error(e)
    raise HTTPException(status_code=404,detail="Requested file not found") from e
  except Exception as e:
    #return Response(content=None,media_type="application/pdf")
    print(e)
    Logger.error(e)    
    raise HTTPException(status_code=500,detail="Couldn't fetch the requested file.Try checking if the case_id and uid are correct") from e