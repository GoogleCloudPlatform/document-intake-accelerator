"""
Copyright 2023 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Following methods should be moved away from classification service when switching to pub/sub system 
to eliminate high-coupling between microservices
"""

from common.config import DOCUMENT_STATUS_API_PATH
import common.config
from common.utils.iap import send_iap_request
from common.utils.logging_handler import Logger
import requests
from typing import Optional
from common.config import STATUS_SPLIT
from common.config import STATUS_SUCCESS
import os
from common.config import BUCKET_NAME
from common.models import Document
from common.utils.copy_gcs_documents import upload_file
import datetime


def create_document(case_id, filename, context=None, user=None):
  uid = None
  try:
    Logger.info(
        f"create_document: with case_id = {case_id} filename = {filename} context = {context}")
    url = f"{common.config.get_document_status_service_url()}/create_document?case_id={case_id}&filename={filename}&context={context}&user={user}"
    Logger.info(f"create_document: posting request to {url}")
    response = send_iap_request(url, method="POST")
    response = response.json()
    uid = response.get("uid")
    Logger.info(f"create_document: Response received ={response}, uid={uid}")
  except requests.exceptions.RequestException as err:
    Logger.error(err)

  return uid


def update_classification_status(case_id: str,
    uid: str,
    status: str,
    document_class: Optional[str] = None,
    classification_score: Optional[float] = None,
):
  """ Call status update api to update the classification output
    Args:
    case_id (str): Case id of the file ,
     uid (str): unique id for  each document
     status (str): status success/failure depending on the validation_score

    """
  base_url = f"{common.config.get_document_status_service_url()}/update_classification_status"
  if status in [STATUS_SUCCESS, STATUS_SPLIT]:
    req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
              f"&status={status}&document_class={document_class}" \
              f"&classification_score={classification_score}"
    response = requests.post(req_url)
    return response

  else:
    req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
              f"&status={status}"
    response = requests.post(req_url)
    return response


# Uploads split Documents
def upload_document(local_path, case_id):
  file_name = os.path.basename(local_path)
  Logger.info(
      f"upload - using local_path={local_path}, case_id={case_id}")
  if local_path is None:
    Logger.error(f"Error, {local_path} is not set, exiting.")
    return

  # Create record in Firestore
  uid = create_document(case_id, file_name)
  if uid is None:
    Logger.error(f"upload - Failed to create document {file_name}")
    return
  else:
    Logger.info(f"upload - Succeeded to create document {file_name} with uid = {uid}")
    file_uri = f"{case_id}/{uid}/{file_name}"
    gsc_uri = f"gs://{BUCKET_NAME}/{file_uri}"

    upload_file(local_path, BUCKET_NAME, file_uri)
    Logger.info(
        f"upload - File {file_name} with case_id {case_id} and uid {uid}"
        f" uploaded successfully in GCS bucket = {gsc_uri}")

    # remove the blob from local after prediction as it is of no use further
    os.remove(local_path)

    # Update the document upload as success in DB
    document = Document.find_by_uid(uid)
    if document is not None:
      document.url = gsc_uri
      system_status = {
          "stage": "uploaded",
          "status": STATUS_SUCCESS,
          "timestamp": datetime.datetime.utcnow(),
          "comment": "Created by Splitter"
      }
      document.system_status = [system_status]
      document.update()
      return uid
    else:
      Logger.error(f"upload - Could not retrieve document by id {uid}")
      return

