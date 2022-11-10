import re

from google.cloud import storage

from fastapi import APIRouter
import os
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
async def start_pipeline(event, context):
  print(f"This Function was triggered by messageId {context.event_id} published at {context.timestamp}")
  bucket_name = event['bucket']
  file_uri = event['name']
  comment = ""
  dirs, filename = split_uri(file_uri)

  print(f"Received event for  bucket - {bucket_name}, file added {file_uri} , filename:  {filename}")
  print(f"Starting Pipeline To process documents inside {bucket_name} bucket and {dirs} folder")

  if filename != START_PIPELINE_FILENAME:
    return

  global gcs
  if not gcs:
    gcs = storage.Client()

  # Get List of Document Objects from the Output Bucket
  source_bucket = gcs.get_bucket(bucket_name)
  blob_list = list(source_bucket.list_blobs(prefix=dirs))
  uid_list = []
  message_list = []
  #generate a case_id if not provided by the user
  case_id = str(uuid.uuid1())

  try:
    # Browse through output Forms and identify matching Processor for each Form
    for i, blob in enumerate(blob_list):
      if blob.name and not blob.name.endswith('/') and blob.name != START_PIPELINE_FILENAME:
        mime_type = blob.content_type
        if mime_type not in MIME_TYPES:
          continue
        # gcs_document = {
        #     "gcs_uri": gcs_doc_path,
        #     "mime_type": blob.content_type
        # }

        # Copy file into gs bucket
        #TODO do it async
        #create a record in database for uploaded document
        output = create_document(case_id, blob.name, context)
        uid = output
        uid_list.append(uid)
        #Copy document in GCS bucket
        #TODO do it async
        new_file_name = f"{case_id}/{uid}/{blob.name}"
        print(f"Copying {blob.name} from {bucket_name} bucket as "
              f"{new_file_name} into {BUCKET_NAME} bucket")
        # status = await run_in_threadpool(copy_blob, bucket_name, blob.name, new_file_name, BUCKET_NAME)
        status = copy_blob(bucket_name=bucket_name, source_blob_name=blob.name,
                           destination_blob_name=new_file_name,
                           dest_bucket_name=BUCKET_NAME)
        # status = await run_in_threadpool(ug.upload_file, case_id, uid, file)
        if status != STATUS_SUCCESS:

          #Update the document upload in GCS as failed
          document = Document.find_by_uid(uid)
          system_status = {
              "stage": "upload",
              "status": STATUS_ERROR,
              "timestamp": datetime.datetime.utcnow(),
              "comment": comment
          }
          document.system_status = [system_status]
          document.update()

          raise HTTPException(
              status_code=500,
              detail="Error "
                     "in uploading document in gcs bucket")

        Logger.info(f"File with case_id {case_id} and uid {uid}"
                    f" uploaded successfully in GCS bucket")


        #Update the document upload as success in DB
        document = Document.find_by_uid(uid)

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
    # message_json = json.dumps({
    #                            'uri': gcs_doc_path,
    #                            })
    # data = message_json.encode('utf-8')
    # publish_message(topic_path, data)
  except Exception as e:
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise HTTPException(
        status_code=500, detail="Error "
                                "in uploading document") from e


# TODO Refactor to common
def create_document(case_id, filename, context, user=None):
  base_url = "http://document-status-service/document_status_service/v1/"
  req_url = f"{base_url}create_document"
  response = requests.post(
      f"{req_url}?case_id={case_id}&filename={filename}&context={context}&user={user}"
  )
  response = response.json()
  uid = response["uid"]
  return uid
# def process(calls):
#   publisher = pubsub_v1.PublisherClient(batch_settings)
#   topic_path = publisher.topic_path(project_id, pubsub_topic)
#   publish_futures = []
#
#   # Resolve the publish future in a separate thread.
#   def callback(future: pubsub_v1.publisher.futures.Future) -> None:
#     message_id = future.result()
#     #print(message_id)
#
#   for call in calls:
#     #print(line)
#     # Data must be a bytestring
#     data = call[0].encode("utf-8")
#     publish_future = publisher.publish(topic_path, data)
#     # Non-blocking. Allow the publisher client to batch multiple messages.
#     publish_future.add_done_callback(callback)
#     publish_futures.append(publish_future)
#     # TODO rate limiting
#     time.sleep(PUBLISHING_SLEEP_TIME_BETWEEN_RECORDS)
#
#   futures.wait(publish_futures, return_when=futures.ALL_COMPLETED)
#
#   print(f"Published messages with batch settings to {topic_path}.")
#
#   return