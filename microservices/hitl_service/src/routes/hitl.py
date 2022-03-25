""" hitl endpoints """
from fastapi import APIRouter, HTTPException, Response
from typing import Optional
from common.models import Document
from common.utils.logging_handler import Logger
from common.config import BUCKET_NAME
# disabling for linting to pass
# pylint: disable = broad-except
import datetime
from google.cloud import storage

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
    #Fetching only active documents
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
    200 : Fetches a list of documents with the same status from Firestore
    400 : If hitl_status is invalid
    500 : If there is any error during fetching from firestore
  """
  if hitl_status.lower() not in ["approved", "rejected", "pending", "review"]:
    raise HTTPException(status_code=400, detail="Invalid Parameter")
  try:
    docs = list(Document.collection.filter("active", "==", "active").fetch())
    result_queue = []
    for d in docs:
      status_class = ""
      doc_dict = d.to_dict()
      hitl_trail = doc_dict["hitl_status"]

      #Preference for hitl_status
      #if hitl_status trail is not present autoapproval status is considered
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
      #if hitl_status is empty
      # create a list push the latest status and update doc
      existing_hitl = doc.to_dict()["hitl_status"] if doc.to_dict(
      )["hitl_status"] is not None else []
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
async def fetch_file(case_id: str, uid: str, download: Optional[bool] = False):
  """
  Fetches and returns the file from GCS bucket
  Args : case_id : str, uid : str
  Returns 200: returns the file and displays it
  Returns 500: If something fails
  """
  try:
    storage_client = storage.Client()
    #listing out all blobs with case_id and uid
    blobs = storage_client.list_blobs(
        BUCKET_NAME, prefix=case_id + "/" + uid + "/", delimiter="/")

    target_blob = None
    #Selecting the last blob which would be the pdf file
    for blob in blobs:
      target_blob = blob

    #If file is not found raise 404
    if target_blob is None:
      raise FileNotFoundError

    filename = target_blob.name.split("/")[-1]
    #Downloading the pdf file into a byte string
    return_data = target_blob.download_as_bytes()

    #Checking for download flag and setting headers
    headers = None
    if download:
      headers = {"Content-Disposition": "attachment;filename=" + filename}
    else:
      headers = {"Content-Disposition": "inline;filename=" + filename}
    return Response(
        content=return_data, headers=headers, media_type="application/pdf")

  except FileNotFoundError as e:
    print(e)
    Logger.error(e)
    raise HTTPException(
        status_code=404, detail="Requested file not found") from e

  except Exception as e:
    #return Response(content=None,media_type="application/pdf")
    print(e)
    Logger.error(e)
    raise HTTPException(
        status_code=500,
        detail="Couldn't fetch the requested file.\
          Try checking if the case_id and uid are correct"
    ) from e

@router.get("/update_hitl_classification")
async def update_hitl_classification(case_id: str, uid: str, document_class: str):
  """
  Updates the hitl classification status flag and doc type and doc class in DB
  Args : case_id : str, uid : str
  Returns 200: returns the file and displays it
  Returns 500: If something fails
  """
  try:
    pass
  except HTTPException as e:
    print(e)
    Logger.error(e)
    raise e

  except Exception as e:
    #return Response(content=None,media_type="application/pdf")
    print(e)
    Logger.error(e)
    raise HTTPException(
        status_code=500,
        detail="Couldn't fetch the requested file.\
          Try checking if the case_id and uid are correct"
    ) from e
