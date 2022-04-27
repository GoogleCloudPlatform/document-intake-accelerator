from fastapi import APIRouter,Request
import base64
import firebase_admin
import os
from firebase_admin import credentials, firestore, initialize_app
import requests
import json
from fastapi import status, Response

# Initialize Firestore DB
# cred = credentials.Certificate("serviceAccountKey.json")
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()

router = APIRouter(prefix="/queue", tags=["Queue"])
# process task api endpoint
req_url = "https://adp-dev.cloudpssolutions.com/upload_service/v1/process_task"


@router.post("/publish")
async def publish_msg(request:Request,response: Response):
    envelope = await request.json()
    print(type(envelope))
    print(envelope)
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response.status_code

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response.status_code

    # store the count of no.of documents in uploaded state to variable result 
    result=get_count()
    pubsub_message = envelope["message"]
    if result<int(os.environ['t']):
        name = "World"
        print(pubsub_message)
        print(type(pubsub_message))
        if isinstance(pubsub_message, dict) and "data" in pubsub_message:
            print("Hello")
            name = base64.b64decode(pubsub_message["data"]).decode("utf-8").strip()
            print("Check type")
            print(type(name))
            name1 = json.loads(name)
            print(type(name1))
            print(name1)
            payload= name1.get("message_list")
            data = {"configs":payload}
            print("This is data")
            print(data)
            # cloud run will send data to process task api endpoint
            response=requests.post(req_url,json=data)
            print(result)
            print(f"Hello {name}")
            return response.status_code

    if result>int(os.environ['t']):
        msg = "Message not acknowledged"
        print(f"unacknowledge: {msg}")
        print("***********")
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response.status_code

    return ("", 204)

# function to get count of no.of documents in uploaded state in collection name document  
def get_count():
    ct=0
    docs = db.collection(u'document').stream()
    for doc in docs:
        a=doc.to_dict()
        b=a["system_status"]
        if type(b)==list:
            for i in b:
                l=len(b)
                if l==1:
                    if i["stage"]=="uploaded" and i["status"]=="success":
                        ct=ct+1
                    
    return ct
