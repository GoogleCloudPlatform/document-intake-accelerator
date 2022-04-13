""" hitl endpoints """
from fastapi import APIRouter, HTTPException, Response
from typing import Optional
from common.models import Document
from common.utils.logging_handler import Logger
from common.config import BUCKET_NAME
from google.cloud import storage
import datetime
import requests
import fireo
import traceback
from models.search_payload import SearchPayload
from config import DB_KEYS
from config import ENTITY_KEYS
# disabling for linting to pass
# pylint: disable = broad-except

router = APIRouter()
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}


@router.get("/report_data")
async def report_data():
  """ reports all data to user
            the database
          Returns:
              200 : fetches all the data from database
              500 : If any error occurs
    """
  docs_list = []
  try:
    #Fetching only active documents
    docs_list = list(
        map(lambda x: x.to_dict(),
            Document.collection.filter(active="active").fetch()))
    docs_list = sorted(
        docs_list, key=lambda i: i["upload_timestamp"], reverse=True)
    response = {"status": "Success"}
    response["data"] = docs_list
    return response

  except Exception as e:
    print(e)
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=500, detail="Error in fetching documents") from e


@router.post("/get_document")
async def get_document(uid: str):
  """ Returns a single document to user using uid from the database
        Args : uid - Unique ID for every document
        Returns:
          200 : Fetches a single document from database
          500 : If any error occurs
    """
  try:
    doc = Document.find_by_uid(uid)
    if doc:
      print(doc)
      print(doc.to_dict()["active"])

    if not doc or not doc.to_dict()["active"] == "active":
      response = {"status": "Failed"}
      response["detail"] = "No Document found with the given uid"
      return response
    response = {"status": "Success"}
    response["data"] = doc.to_dict()
    print(response)
    return response

  except Exception as e:
    print(e)
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
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
    docs = list(Document.collection.filter(active="active").fetch())
    result_queue = []
    for d in docs:
      doc_dict = d.to_dict()
      hitl_trail = doc_dict["hitl_status"]

      current_status = None
      system_status = doc_dict["system_status"]

      #Check the latest action hitl or system
      #If the last step of system status is autoapproval
      # consider autoapproval status
      # elif last update was to hitl consider hitl
      if hitl_trail:
        last_hitl_status = hitl_trail[-1]
        last_system_status = system_status[-1]
        if last_system_status["timestamp"] > last_hitl_status["timestamp"]:
          if last_system_status["stage"].lower() == "auto_approval"\
             and last_system_status["status"].lower() == "success":
            current_status = doc_dict["auto_approval"].lower()

        else:
          if last_hitl_status["status"].lower() != "reassigned":
            current_status = last_hitl_status["status"].lower()
      else:
        if doc_dict["auto_approval"]:
          current_status = doc_dict["auto_approval"].lower()
      if current_status == hitl_status:
        result_queue.append(doc_dict)

    result_queue = sorted(
        result_queue, key=lambda i: i["upload_timestamp"], reverse=True)

    response = {"status": "Success"}
    response["len"] = len(result_queue)
    response["data"] = result_queue
    return response

  except Exception as e:
    print(e)
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
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
    if not doc or not doc.to_dict()["active"].lower() == "active":
      response = {"status": "Failed"}
      response["detail"] = "No Document found with the given uid"
      return response
    doc.entities = updated_doc["entities"]
    doc.update()
    return {"status": "Success"}

  except Exception as e:
    print(e)
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
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
    if not doc or not doc.to_dict()["active"].lower() == "active":
      response = {"status": "Failed"}
      response["detail"] = "No Document found with the given uid"
      return response
    if doc:
      # create a list push the latest status and update doc
      doc.hitl_status = fireo.ListUnion([hitl_status])
      doc.is_autoapproved = "no"
      doc.update()
    return {"status": "Success"}

  except Exception as e:
    print(e)
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=500, detail="Failed to update hitl status") from e


@router.get("/fetch_file")
async def fetch_file(case_id: str, uid: str, download: Optional[bool] = False):
  """
  Fetches and returns the file from GCS bucket
  Args : case_id : str, uid : str
  Returns 200: returns the file and displays it
  Returns 404: Document not found
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
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=404, detail="Requested file not found") from e

  except Exception as e:
    #return Response(content=None,media_type="application/pdf")
    print(e)
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=500,
        detail="Couldn't fetch the requested file.\
          Try checking if the case_id and uid are correct") from e


@router.get("/get_unclassified")
async def get_unclassified():
  """
  Fetches a queue of all unclassified documents
  Returns:
    200 : Fetches a list of documents with the same status from Firestore
    500 : If there is any error during fetching from firestore
  """
  try:
    docs = list(Document.collection.filter(active="active").fetch())
    result_queue = []
    for d in docs:
      doc_dict = d.to_dict()
      system_trail = doc_dict["system_status"]
      if system_trail[-1]["stage"].lower() == "classification":
        if system_trail[-1]["status"].lower() != "success":
          result_queue.append(doc_dict)
    response = {"status": "success"}
    response["data"] = result_queue
    return response
  except Exception as e:
    print(e)
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=500,
        detail="Error during getting unclassified documents") from e


def update_classification_status(case_id: str,
                                 uid: str,
                                 status: str,
                                 document_class: Optional[str] = None,
                                 document_type: Optional[str] = None):
  """ Call status update api to update the classification output
    Args:
    case_id (str): Case id of the file ,
     uid (str): unique id for  each document
     status (str): status success/failure depending on the validation_score

    """
  base_url = "http://document-status-service/document_status_service" \
  "/v1/update_classification_status"

  if status.lower() == "success":
    req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
    f"&status={status}&is_hitl={True}&document_class={document_class}"\
      f"&document_type={document_type}"
    response = requests.post(req_url)
    return response

  else:
    req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
    f"&status={status}"
    response = requests.post(req_url)
    return response


def call_process_task(case_id: str, uid: str, document_class: str,
                      document_type: str, gcs_uri: str, context: str):
  """
    Starts the process task API after hitl classification
  """

  data = {
      "case_id": case_id,
      "uid": uid,
      "gcs_url": gcs_uri,
      "document_class": document_class,
      "document_type": document_type,
      "context": context
  }
  payload = {"configs": [data]}
  base_url = "http://upload-service/upload_service/v1/process_task"
  print("params for process task", base_url, payload)
  Logger.info(f"Params for process task {payload}")
  response = requests.post(base_url, json=payload)
  return response


@router.post("/update_hitl_classification")
async def update_hitl_classification(case_id: str, uid: str,
                                     document_class: str):
  """
  Updates the hitl classification status flag and doc type and doc class in DB
  and starts the process task
  Args : case_id : str, uid : str
  Returns 200: updates the DB and starts process task
  Returns 400: Invalid Parameters
  Returns 404: Document not found
  Returns 500: If something fails
  """
  try:

    doc = Document.find_by_uid(uid)
    print(doc.to_dict()["active"].lower())
    if not doc or not doc.to_dict()["active"].lower() == "active":
      Logger.error("Document for hitl classification not found")
      raise HTTPException(status_code=404, detail="Document not found")

    if document_class not in [
        "unemployment_form", "driving_licence", "claims_form", "utility_bill",
        "pay_stub"
    ]:
      Logger.error("Invalid parameter document_class")
      raise HTTPException(
          status_code=400, detail="Invalid Parameter. Document class")

    Logger.info(f"Starting manual classification for case_id"\
        f" {case_id} and uid {uid}")
    document_type = None
    if document_class.lower() == "unemployment_form":
      document_type = "application_form"
    else:
      document_type = "supporting_documents"

    #Update DSM
    Logger.info("Updating Doc status from Hitl classification for case_id"\
      f"{case_id} and uid {uid}")
    response = update_classification_status(
        case_id,
        uid,
        "success",
        document_class=document_class,
        document_type=document_type)
    print(response)
    if response.status_code != 200:
      Logger.error(f"Document status update failed for {case_id} and {uid}")
      raise HTTPException(
          status_code=500, detail="Document status updation failed")

    #Call Process task
    Logger.info("Starting Process task from hitl classification")
    res = call_process_task(case_id, uid, document_class, document_type,
                            doc.url, doc.context)
    if res.status_code == 202:
      return {
          "status": "success",
          "message": "Process task api has been started successfully"
      }

  except HTTPException as e:
    print(e)
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise e

  except Exception as e:
    print(e)
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=500,
        detail="Couldn't update the classification.\
          Try checking if the case_id and uid are correct") from e


def compare_value(entity, term, entity_key):
  if entity["entity"] == entity_key:

    if isinstance(term, str):
      if entity["corrected_value"] is not None:
        if isinstance(entity["corrected_value"], str):
          return term.lower() in entity["corrected_value"].lower()
        else:
          return False

      else:
        if entity["value"] is not None:
          if isinstance(entity["value"], str):
            return term.lower() in entity["value"].lower()
          else:
            return False
        else:
          return False

    else:
      if entity["corrected_value"] is not None:
        return term == entity["corrected_value"]

      else:
        if entity["value"] is not None:
          return term == entity["value"]
        else:
          return False

  else:
    return False


@router.post("/search")
async def search(search_term: SearchPayload):
  """
  Searches for documents that include the search term in the keys
  present in config
  Args :search_term : SearchPayload
  Returns 200: searches and returns the list of documents
  Returns 400: Invalid Parameters
  Returns 422: Filter key is not filterable(Not present in Config)
  Returns 500: If something fails
  """

  try:
    filter_key = search_term.filter_key
    filter_value = search_term.filter_value
    term = search_term.term
    limit_start = search_term.limit_start
    limit_end = search_term.limit_end

    docs_list = []

    if filter_key is not None and filter_value is not None:
      if not isinstance(filter_key, str):
        raise HTTPException(
            status_code=400,
            detail="Invalid Parameter type.\
              Filter key should be of type string")
      if filter_key in DB_KEYS:
        docs_list = list(
            map(
                lambda x: x.to_dict(),
                Document.collection.filter(active="active").filter(
                    filter_key, "==", filter_value).fetch()))
        docs_list = sorted(
            docs_list, key=lambda i: i["upload_timestamp"], reverse=True)
        if term is None:
          if limit_start is not None and limit_end is not None:
            if not isinstance(limit_start, int) or not isinstance(
                limit_end, int):
              raise HTTPException(
                  status_code=400,
                  detail="Invalid Parameter type.\
                    Limit start and end should be of type int")
            docs_list = docs_list[limit_start:limit_end]
          return {"status": "success","len": len(docs_list),"data": docs_list}
      else:
        raise HTTPException(
            status_code=422, detail="Entered key is not filterable")

    elif term is None:
      raise HTTPException(status_code=400, detail="Search term not found")

    else:
      docs_list = list(
          map(lambda x: x.to_dict(),
              Document.collection.filter(active="active").fetch()))
      docs_list = sorted(
          docs_list, key=lambda i: i["upload_timestamp"], reverse=True)
    resultset = []

    for doc in docs_list:
      for db_key in DB_KEYS:
        if doc in resultset:
          break
        if doc[db_key] is not None:
          if isinstance(term, str) and isinstance(doc[db_key], str):
            if term.lower() in doc[db_key].lower():
              resultset.append(doc)
              break
          else:
            if term == doc[db_key]:
              resultset.append(doc)
              break

      entities = doc.get("entities", None)
      if doc in resultset or entities is None:
        continue
      for entity_key in ENTITY_KEYS:
        temp = [
            doc for entity in entities
            if compare_value(entity, term, entity_key)
        ]
        if len(temp) > 0:
          resultset.extend(temp)
          temp.clear()
          break

    if limit_start is not None and limit_end is not None:
      resultset = resultset[limit_start:limit_end]

    return {"status": "success", "len": len(resultset), "data": resultset}

  except HTTPException as e:
    print(e)
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise e

  except Exception as e:
    print(e)
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=400, detail="Error occurred in search") from e
