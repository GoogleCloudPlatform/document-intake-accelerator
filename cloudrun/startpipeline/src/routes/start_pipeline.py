
from google.cloud import storage
from fastapi import Request, status, Response
import json
from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from config import DOCUMENT_STATUS_URL, UPLOAD_URL
from common.utils.copy_gcs_documents import copy_blob
from common.utils.helper import split_uri_2_path_filename
import uuid
import requests
import traceback
import datetime
from fastapi import HTTPException
from common.utils.logging_handler import Logger
from common.models import Document
from common.utils.publisher import publish_document
from common.config import BUCKET_NAME
from common.config import STATUS_SUCCESS, STATUS_ERROR
import os

# API clients
gcs = None

MIME_TYPES = [
    "application/pdf",
    # "image/gif",  # TODO Add Support for all these types
    # "image/tiff",
    # "image/jpeg",
    # "image/png",
    # "image/bmp",
    # "image/webp"
]

START_PIPELINE_FILENAME = os.environ.get("START_PIPELINE_NAME",
                                         "START_PIPELINE")
router = APIRouter(prefix="/start-pipeline", tags=["Start Pipeline"])


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

  if not isinstance(envelope,
                    dict) or "bucket" not in envelope or "name" not in envelope:
    response.status_code = status.HTTP_400_BAD_REQUEST
    response.body = "invalid Pub/Sub message format"
    Logger.error(f"error: {response.body}")
    return response

  bucket_name = envelope['bucket']
  file_uri = envelope['name']
  Logger.info(f"bucket_name={bucket_name}, file_uri={file_uri}")
  comment = ""
  context = "california" # TODO is a temp workaround
  dirs, filename = split_uri_2_path_filename(file_uri)

  Logger.info(
      f"Received event for bucket[{bucket_name}] file_uri=[{file_uri}], filename=[{filename}]")

  if filename != START_PIPELINE_FILENAME:
    Logger.info(f"Skipping action, since waiting for {START_PIPELINE_FILENAME} to trigger pipe-line")
    return "", status.HTTP_204_NO_CONTENT

  Logger.info(
      f"Starting pipeline to process documents inside {bucket_name} bucket and {dirs} folder")

  global gcs
  if not gcs:
    gcs = storage.Client()

    # Get List of Document Objects from the Output Bucket
  blob_list = gcs.list_blobs(bucket_name, prefix=dirs + "/")
  uid_list = []
  message_list = []
  # generate a case_id
  dirs_string = dirs.replace("/", "_")
  uuid_str = str(uuid.uuid1())
  ll = max(len(str(dirs_string)), int(len(uuid_str)/2))
  case_id = str(dirs_string) + "_" + str(uuid.uuid1())[:-ll]
  event_id = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')

  try:
    # Browse through output Forms and identify matching Processor for each Form
    for blob in blob_list:
      if blob.name and not blob.name.endswith('/') and blob.name != START_PIPELINE_FILENAME:
        mime_type = blob.content_type
        if mime_type not in MIME_TYPES:
          continue
        d, blob_filename = split_uri_2_path_filename(blob.name)
        Logger.info(
          f"Handling case_id={case_id}, file_path={blob.name}, file_name={blob_filename}")

        # create a record in database for uploaded document
        output = create_document(case_id, blob.name, context)
        uid = output
        Logger.info(f"Created document with uid={uid} for case_id={case_id}, file_path={blob.name}, file_name={blob_filename}")
        uid_list.append(uid)

        # Copy document in GCS bucket
        new_file_name = f"{case_id}/{uid}/{blob_filename}"
        result = await run_in_threadpool(copy_blob, bucket_name, blob.name, new_file_name, BUCKET_NAME)
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

        Logger.info(f"File {blob.name} with case_id {case_id} and uid {uid}"
                    f" uploaded successfully in GCS bucket")

        # Update the document upload as success in DB
        document = Document.find_by_uid(uid)
        if document is not None:
          gcs_base_url = f"gs://{BUCKET_NAME}"
          document.url = f"{gcs_base_url}/{case_id}/{uid}/{blob_filename}"
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
        else:
          Logger.error(f"Could not retrieve document by id {uid}")

    # Pushing Message To Pubsub
    pubsub_msg = f"batch for {case_id} moved to bucket"
    message_dict = {"message": pubsub_msg, "message_list": message_list}
    publish_document(message_dict)
    Logger.info(f"Message with case id {case_id} published"
                f" successfully {uid_list}")

    # TODO Temp Disabling moving to processed
    # #move file to the processed folder
    # destination_blob_name = f"processed/{dirs}/{event_id}/{blob_filename}"
    # Logger.info(f"Moving file from {bucket_name}/{blob.name} to {bucket_name}/{destination_blob_name}")
    # result = await run_in_threadpool(move_blob, bucket_name, blob.name, destination_blob_name)
    # if result != STATUS_SUCCESS:
    #   Logger.error(f"Error: {result}")
    #   raise HTTPException(
    #       status_code=500,
    #       detail="Error "
    #              "when copying to processed folder")
    # Logger.info(f"File {blob.name} with case_id {case_id} and uid {uid} moved to {bucket_name}/{destination_blob_name}")


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
