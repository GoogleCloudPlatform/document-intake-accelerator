""" classification endpoints """
from distutils.log import Log
import os
import json
from fastapi import APIRouter
from fastapi import APIRouter, HTTPException, UploadFile, File
from google.cloud import storage
from google.cloud import storage
from google.cloud.storage import Blob
from common.models import Document
from common.utils.logging_handler import Logger
#from services.classification_service import predict_doc_type
from utils.classification.split_and_classify import DocClassifier
import requests
from typing import Optional
# disabling for linting to pass
# pylint: disable = broad-except

router = APIRouter(prefix="/classification")
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}

def predict_doc_type(case_id:str , uid:str ,gcs_url : str):
    """
    Fetches the model predictions and returns the output in a dictionary format
    
    Args: case_id:str, uid:str, gcs_url:str

    Returns: case_id, u_id, predicted_class, model_conf, model_endpoint_id
    """
    
    outfolder = os.path.join(os.path.dirname(__file__),"temp_files")
    if not os.path.exists(outfolder):
        os.mkdir(os.path.join(os.path.dirname(__file__),"temp_files"))
    
    classifier  = DocClassifier(case_id,uid,gcs_url,outfolder)
    
    doc_type = json.loads(classifier.execute_job())
    os.rmdir(outfolder)
    print(doc_type)
    return doc_type

def update_classification_status(case_id: str,uid: str,status: str,document_class: Optional[str] = None,document_type: Optional[str] = None):
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
    f"&status={status}&document_class={document_class}&document_type={document_type}"
    response = requests.post(req_url)
    return response
  else:
    req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
    f"&status={status}"
    response = requests.post(req_url)
    return response

@router.post("/classification_api")
async def classifiction(case_id: str, uid: str, gcs_url: str):
  """classifies the  input and updates the active status of document in
        the database
      Args:
          case_id (str): Case id of the file ,
           uid (str): unique id for  each document
           gcs (str): gcs url of document
      Returns:
          200 : PDF files are successfully classified and database updated
          500  : HTTPException: 500 Internal Server Error if something fails
    """
  if not case_id.strip() or not uid.strip() or not gcs_url.strip():
    Logger.error(f"Classification failed parameters missing")
    raise HTTPException(status_code=400,detail={"status":"Failed", "message":"Parameters Missing"})

  if not gcs_url.endswith(".pdf") or not gcs_url.startswith("gs://"):
    Logger.error(f"Classification failed GCS path is invalid")
    raise HTTPException(status_code=400,detail={"status":"Failed", "message":"GCS pdf path is incorrect"})

  if case_id != gcs_url.split('/')[3] or uid != gcs_url.split('/')[4]:
    Logger.error(f"Classification failed parameters mismatched")
    raise HTTPException(status_code=400,detail={"status":"Failed", "message":"Parameters Mismatched"})

  try:
    
    label_map = {"UE":"unemployment_form", "DL" : "driving_licence", "Claim":"claims_form", "Utility":"utility_bill" , "PayStub" : "pay_stub" }
    
    Logger.info(f"Starting classification for {case_id} and {uid}")

    doc_prediction_result = predict_doc_type(case_id,uid,gcs_url)
    
    if doc_prediction_result:
      
      if doc_prediction_result["predicted_class"] == "Negative":
        FAILED_RESPONSE["message"] = "Invalid Document"
        response = update_classification_status(case_id,uid,"failed")
        Logger.error(f"Document unclassified")
        
        if response.status_code != 200:
          Logger.error(f"Document status update failed")
          raise HTTPException(status_code=500,detail="Failed to update document status")  
        return FAILED_RESPONSE
      
      doc_type = ""
      doc_class = label_map[doc_prediction_result["predicted_class"]]
      
      if doc_prediction_result["predicted_class"] == "UE":
        doc_type = "application"
      else:
        doc_type = "supporting_documents"
      
      SUCCESS_RESPONSE["case_id"] = doc_prediction_result["case_id"]
      SUCCESS_RESPONSE["uid"] =  uid
      SUCCESS_RESPONSE["doc_type"] = doc_type
      SUCCESS_RESPONSE["doc_class"] = doc_class
    
      #DocumentStatus api call
      response = update_classification_status(case_id,uid,"success",document_class=doc_class,document_type=doc_type)
      print(response)
      if response.status_code != 200:
        Logger.error(f"Document status updation failed for {case_id} and {uid}")
        raise HTTPException(status_code=500,detail="Document status updation failed")
      
      return SUCCESS_RESPONSE
    
    else:
      raise HTTPException(status_code=500,detail="Classification Failed")

  except HTTPException as e:
    print(e)
    Logger.error(f"{e} while classification {case_id} and {uid}")
    update_classification_status(case_id,uid,"failed")
    raise e
  
  except Exception as e:
    print(f"{e} while classification {case_id} and {uid}")
    Logger.error(e)
    #DocumentStatus api call
    update_classification_status(case_id,uid,"failed")
    raise HTTPException(status_code=500, detail="Classification Failed")