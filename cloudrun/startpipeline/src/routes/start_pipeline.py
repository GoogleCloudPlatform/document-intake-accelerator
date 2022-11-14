import re

from google.cloud import storage
from fastapi import Request, status, Response
import json
from fastapi import APIRouter
import os
from config import DOCUMENT_STATUS_URL
from common.utils.copy_gcs_documents import copy_blob
import uuid
import requests
import traceback
import datetime
from fastapi import HTTPException
from common.utils.logging_handler import Logger
from common.models import Document
from common.utils.publisher import publish_document
from common.config import BUCKET_NAME
from common.config import STATUS_IN_PROGRESS, STATUS_SUCCESS, STATUS_ERROR

# API clients
gcs = None

MIME_TYPES = [
    "application/pdf",
    "application/pdf",
    "image/gif",
    "image/tiff",
    "image/jpeg",
    "image/png",
    "image/bmp",
    "image/webp"
]

START_PIPELINE_FILENAME = os.environ.get("START_PIPELINE_NAME", "START_PIPELINE")
router = APIRouter(prefix="/start-pipeline", tags=["Start Pipeline"])


def split_uri(uri: str):
  match = re.match(r"([^/]+)/(.+)", uri)
  if not match:
    return "", ""
  dirs = match.group(1)
  file = match.group(2)
  return dirs, file


@router.post("/run")
async def start_pipeline(request: Request, response: Response):
  body = await request.body()
  if not body or body == "":
    response.status_code = status.HTTP_400_BAD_REQUEST
    response.body = "Request has no body"
    Logger.warning(response.body)
    return response

  try:
    envelope = await request.json()
    Logger.info("Pub/Sub envelope:")
    Logger.info(envelope)

  except json.JSONDecodeError:
    response.status_code = status.HTTP_400_BAD_REQUEST
    response.body = f"Unable to parse to JSON: {body}"
    return response

  if not envelope:
    response.status_code = status.HTTP_400_BAD_REQUEST
    response.body = "No Pub/Sub message received"
    Logger.error(f"error: {response.body}")
    return response

  if not isinstance(envelope, dict) or "bucket" not in envelope or "name" not in envelope:
    response.status_code = status.HTTP_400_BAD_REQUEST
    response.body = "invalid Pub/Sub message format"
    Logger.error(f"error: {response.body}")
    return response

  bucket_name = envelope['bucket']
  file_uri = envelope['name']
  Logger.info(f"bucket_name={bucket_name}, file_uri={file_uri}")
  comment = ""
  context = ""
  dirs, filename = split_uri(file_uri)

  Logger.info(f"Received event for  bucket - {bucket_name}, file added {file_uri} , filename:  {filename}")
  Logger.info(f"Starting Pipeline To process documents inside {bucket_name} bucket and {dirs} folder")

  if filename != START_PIPELINE_FILENAME:
    return "", status.HTTP_204_NO_CONTENT

  global gcs
  if not gcs:
    gcs = storage.Client()

  # Get List of Document Objects from the Output Bucket
  source_bucket = gcs.get_bucket(bucket_name)
  blob_list = list(source_bucket.list_blobs(prefix=dirs))
  uid_list = []
  message_list = []
  # generate a case_id
  case_id = str(uuid.uuid1())

  try:
    # Browse through output Forms and identify matching Processor for each Form
    for i, blob in enumerate(blob_list):
      if blob.name and not blob.name.endswith('/') and blob.name != START_PIPELINE_FILENAME:
        mime_type = blob.content_type
        if mime_type not in MIME_TYPES:
          continue

        Logger.info(f"case_id={case_id}, file_name={blob.name}")

        # Copy file into gs bucket
        #TODO do it async
        #create a record in database for uploaded document
        output = create_document(case_id, blob.name, context)
        uid = output
        uid_list.append(uid)

        #Copy document in GCS bucket
        new_file_name = f"{case_id}/{uid}/{blob.name}"
        Logger.info(f"Copying {blob.name} from {bucket_name} bucket as "
              f"{new_file_name} into {BUCKET_NAME} bucket")

        result = copy_blob(bucket_name=bucket_name, source_blob_name=blob.name,
                           destination_blob_name=new_file_name,
                           dest_bucket_name=BUCKET_NAME)
        #TODO do it async
        # result = await run_in_threadpool(copy_blob, bucket_name, blob.name, new_file_name, BUCKET_NAME)
        if result != STATUS_SUCCESS:
          # Update the document upload in GCS as failed
          document = Document.find_by_uid(uid)
          system_status = {
              "stage": "upload",
              "status": STATUS_ERROR,
              "timestamp": datetime.datetime.utcnow(),
              "comment": comment
          }
          document.system_status = [system_status]
          document.update()
          Logger.error(f"Error: {result}")
          raise HTTPException(
              status_code=500,
              detail="Error "
                     "in uploading document in gcs bucket")

        Logger.info(f"File with case_id {case_id} and uid {uid}"
                    f" uploaded successfully in GCS bucket")

        #Update the document upload as success in DB
        document = Document.find_by_uid(uid)
        if document is not None:
          gcs_base_url = f"gs://{BUCKET_NAME}"
          document.url = f"{gcs_base_url}/{case_id}/{uid}/{blob.name}"
          system_status = {
              "stage": "uploaded",
              "status": STATUS_SUCCESS,
              "timestamp": datetime.datetime.utcnow(),
              "comment": comment
          }
          document.system_status = [system_status]
          document.update()
          message_list.append({
              "case_id": case_id,
              "uid": uid,
              "gcs_url": document.url,
              "context": context
          })

    # Pushing Message To Pubsub
    pubsub_msg = f"batch for {case_id} moved to bucket"
    message_dict = {"message": pubsub_msg, "message_list": message_list}
    publish_document(message_dict)
    Logger.info(f"Files with case id {case_id} uploaded"
                f" successfully")
    return {
        "status": f"Files with case id {case_id} uploaded"
                  f"successfully, the document"
                  f" will be processed in sometime ",
        "case_id": case_id,
        "uid_list": uid_list,
        "configs": message_list
    }

  except Exception as e:
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=500, detail="Error "
                                "in uploading document") from e


def create_document(case_id, filename, context, user=None):
  uid = None
  try:
    base_url = f"{DOCUMENT_STATUS_URL}"
    req_url = f"{base_url}/create_document"
    url = f"{req_url}?case_id={case_id}&filename={filename}&context={context}&user={user}"
    Logger.info(f"Posting request to {url}")
    response = requests.post(url)
    response = response.json()
    Logger.info(f"Response received ={response}")
    uid = response.get("uid")
  except requests.exceptions.RequestException as err:
    Logger.error(err)

  return uid
