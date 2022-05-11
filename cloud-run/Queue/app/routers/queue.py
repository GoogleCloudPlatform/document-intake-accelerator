from fastapi import APIRouter,Request
import base64
import firebase_admin
import os
from firebase_admin import credentials, firestore, initialize_app
import requests
import json
from fastapi import status, Response
from app.config.config import PROCESS_TASK_URL


#Initialize Firestore DB

cred = credentials.Certificate("serviceAccountKey.json")
default_app = firebase_admin.initialize_app(cred)
#firebase_admin.initialize_app(cred)
db = firestore.client()

router = APIRouter(prefix="/queue", tags=["Queue"])

req_url = PROCESS_TASK_URL



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
            #data={"case_id": name1.get("caseid"),"uid": name1.get("uid"),"gcs_url": name1.get("gcs_url"),"context": name1.get("context")}
            #data=name1.get("message_list")
            print("This is data")
            print(data)
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



def get_count():
    ct=0
    docs = db.collection(u'document').stream()
    for doc in docs:
        a=doc.to_dict()
        #print(a)
        #print('loop')
        b=a["system_status"]
        if type(b)==list:
            #print('in loop')
            for i in b:
                l=len(b)
                if l==1:
                #print('loop')
                    if i["stage"]=="uploaded" and i["status"]=="success":
                        ct=ct+1
                    
    return ct
