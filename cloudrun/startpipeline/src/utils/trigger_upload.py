import os
import random
import string

import requests
from config import UPLOAD_URL
from fastapi import APIRouter
from common.utils.helper import split_uri_2_path_filename
from common.utils.logging_handler import Logger
from common.utils.iap import send_iap_request

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

from google.cloud import storage
storage_client = storage.Client()


CONTEXT = "california" #TODO
def upload_file(bucket_name, files, case_id):
  # download blob locally
  bucket = storage_client.get_bucket(bucket_name)
  # Create a blob object from the filepath

  letters = string.ascii_lowercase
  temp_folder = "".join(random.choice(letters) for i in range(10))
  if not os.path.exists(temp_folder):
    Logger.info(f"Output directory used for extraction locally: {temp_folder}")
    os.mkdir(temp_folder)

  uploadFilesList = []
  for file_uri in files:
    print(f"file_uri={file_uri}")
    blob = bucket.blob(file_uri)
    # Download the file to a destination
    prefix, file_name = split_uri_2_path_filename(file_uri)
    print(f"file_name={file_name}")
    destination_file_name = os.path.join(temp_folder, file_name)
    print(f"destination_file_name={destination_file_name}")
    blob.download_to_filename(destination_file_name)
    print(f"Downloaded {file_uri} to  {destination_file_name}")
    # uploadFilesList.append(("files", (file_name, open(destination_file_name,"rb"), "application/pdf")))
    files = {'file': (file_name, open(destination_file_name, 'rb'))}
    upload_task_url = f"{UPLOAD_URL}/upload_service/v1/upload_files?context={CONTEXT}&case_id={case_id}"
    process_task_response = send_iap_request(upload_task_url, method="POST", files=files)

    print(f"response={process_task_response.text} with status code={process_task_response.status_code}")
    # assert response.status_code == 200
    # data = response.json().get("configs")
    # print(data)

