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
  print("PROCESS_TASK_URL = {PROCESS_TASK_URL}")

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

  result = get_count()
  pubsub_message = envelope["message"]
  if result < int(os.environ["t"]):
    print("Pub/Sub message:")
    print(pubsub_message)

    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
      msg_data = base64.b64decode(
          pubsub_message["data"]).decode("utf-8").strip()
      name = json.loads(msg_data)
      payload = name.get("message_list")
      request_body = {"configs": payload}

      #data={"case_id": name.get("caseid"),"uid": name.get("uid"),"gcs_url": name.get("gcs_url"),"context": name.get("context")}
      #data=name.get("message_list")

      print(f"Sending data to {PROCESS_TASK_URL}:")
      print(request_body)

      response = requests.post(PROCESS_TASK_URL, json=request_body)
      print(result)
      return response

  if result > int(os.environ["t"]):
    print(f"unacknowledge: {response.body}")
    response.body = "Message not acknowledged"
    response.status_code = status.HTTP_400_BAD_REQUEST
    return response

  # No Content
  return ("", 204)


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
