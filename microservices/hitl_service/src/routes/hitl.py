""" hitl endpoints """
from fastapi import APIRouter, HTTPException
from typing import Optional
from common.models import Document
# disabling for linting to pass
# pylint: disable = broad-except
import datetime

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
  except Exception as e:
    print(e)
    raise HTTPException(
        status_code=500, detail="Error in fetching documents") from e
  for d in docs:
    doc_list.append(d.to_dict())
  response = {"status": "Success"}
  response["data"] = doc_list
  return response


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
  except Exception as e:
    print(e)
    raise HTTPException(
        status_code=500, detail="Error in fetching documents") from e
  response = {"status": "Success"}
  response["data"] = doc
  return response


@router.post("/get_queue")
async def get_queue(hitl_status: str):
  """
  Fetches a queue of all documents with the same hitl status
  (accepted,rejected or pending) from firestore
  Args: hitl_queue - status of the required queue
  Returns:
    200 : Fetches a list of documents with the same hitl_status from Firestore
    500 : If there is any error during fetching from firestore
  """
  if hitl_status.lower() not in ["accepted", "rejected", "pending"]:
    raise HTTPException(status_code=400, detail="Invalid Parameter")
  try:
    docs = list(Document.collection.filter("active", "==", "active").fetch())
  except Exception as e:
    print(e)
    raise HTTPException(
        status_code=500, detail="Error during fetching from Firestore") from e
  result_queue = []
  for d in docs:
    status_class = ""
    doc_dict = d.to_dict()
    hitl_trail = doc_dict["hitl_status"]
    if hitl_trail:
      status_class = hitl_trail[-1]["status"].lower()
    if status_class == hitl_status.lower():
      result_queue.append(doc_dict)
  response = {"status": "Success"}
  response["data"] = result_queue
  return response


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
  timestamp = str(datetime.datetime.utcnow())
  hitl_status = {
      "timestamp": timestamp,
      "status": status,
      "user": user,
      "comment": comment
  }
  try:
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
    raise HTTPException(
        status_code=500, detail="Failed to update hitl status") from e
