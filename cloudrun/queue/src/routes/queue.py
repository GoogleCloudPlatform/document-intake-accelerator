"""
Copyright 2022 Google LLC

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

from fastapi import APIRouter, Request
import base64
import firebase_admin
import os
from firebase_admin import credentials, firestore, initialize_app
import requests
import json
from fastapi import status, Response
from config import PROCESS_TASK_URL, API_DOMAIN
from common.config import STATUS_IN_PROGRESS, STATUS_SUCCESS, STATUS_ERROR
from common.utils.logging_handler import Logger

PROJECT_ID = os.environ.get("PROJECT_ID")

# Initializing Firebase client.
firebase_admin.initialize_app(credentials.ApplicationDefault(), {
    "projectId": PROJECT_ID,
})
db = firestore.client()

router = APIRouter(prefix="/queue", tags=["Queue"])


@router.post("/publish")
async def publish_msg(request: Request, response: Response):
  Logger.info(f"PROCESS_TASK_URL = {PROCESS_TASK_URL}")

  body = await request.body()
  if not body or body == "":
    response.status_code = status.HTTP_400_BAD_REQUEST
    response.body = "Request has no body"
    print(response.body)
    return response

  try:
    envelope = await request.json()
    print("Pub/Sub envelope:")
    print(envelope)

  except json.JSONDecodeError:
    response.status_code = status.HTTP_400_BAD_REQUEST
    response.body = f"Unable to parse to JSON: {body}"
    return response

  if not envelope:
    response.status_code = status.HTTP_400_BAD_REQUEST
    response.body = "No Pub/Sub message received"
    print(f"error: {response.body}")
    return response

  if not isinstance(envelope, dict) or "message" not in envelope:
    response.status_code = status.HTTP_400_BAD_REQUEST
    response.body = "invalid Pub/Sub message format"
    print(f"error: {response.body}")
    return response

  doc_count = get_count()
  print(f"Current number of uploaded documents doc_count = {doc_count}")

  pubsub_message = envelope["message"]

  # if doc_count < int(os.environ["MAX_UPLOADED_DOCS"]):
  print("Pub/Sub message:")
  print(pubsub_message)

  print(f"MAX_UPLOADED_DOCS={os.environ['MAX_UPLOADED_DOCS']}")
  if isinstance(pubsub_message, dict) and "data" in pubsub_message:
    msg_data = base64.b64decode(
        pubsub_message["data"]).decode("utf-8").strip()
    name = json.loads(msg_data)
    payload = name.get("message_list")
    request_body = {"configs": payload}

    # Sample request body
    # {
    #   "configs": [
    #     {
    #       "case_id": "6075e034-2763-11ed-8345-aa81c3a89f04",
    #       "uid": "jcdQmUqUKrcs8GGsmojp",
    #       "gcs_url": "gs://sample-project-dev-document-upload/6075e034-2763-11ed-8345-aa81c3a89f04/jcdQmUqUKrcs8GGsmojp/arizona-application-form.pdf",
    #       "context": "arizona"
    #     }
    #   ]
    # }
    print(f"Sending data to {PROCESS_TASK_URL}:")
    print(request_body)

    process_task_response = requests.post(PROCESS_TASK_URL, json=request_body)
    print(f"Response from {PROCESS_TASK_URL}")
    print(process_task_response.json())

    response.status_code = process_task_response.status_code
    return response

  # if doc_count > int(os.environ["MAX_UPLOADED_DOCS"]):
  #   print(f"unacknowledged: {response.body}")
  #   response.body = "Message not acknowledged"
  #   response.status_code = status.HTTP_400_BAD_REQUEST
  #   return response

  # No Content
  return "", status.HTTP_204_NO_CONTENT


def get_count():
  ct = 0
  docs = db.collection(u"document").stream()
  for doc in docs:
    a = doc.to_dict()
    #print(a)
    #print("loop")
    b = a["system_status"]
    if type(b) == list:
      #print("in loop")
      for i in b:
        l = len(b)
        if l == 1:
          #print("loop")
          if i["stage"] == "uploaded" and i["status"] == STATUS_SUCCESS:
            ct = ct + 1

  return ct
