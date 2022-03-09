""" classification endpoints """

from fastapi import APIRouter
from fastapi import APIRouter, HTTPException, UploadFile, File
from google.cloud import storage
from common.models import Document
from google.cloud import storage
from google.cloud.storage import Blob
from services.classification_service import predict_doc_type
from fastapi.responses import HTMLResponse
import requests

# disabling for linting to pass
# pylint: disable = broad-except

router = APIRouter(prefix="/classification")
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}


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
    raise HTTPException(status_code=400,detail={"status":"Failed", "message":"Parameters Missing"})
  if not gcs_url.endswith(".pdf") or not gcs_url.startswith("gs://"):
    raise HTTPException(status_code=400,detail={"status":"Failed", "message":"GCS pdf path is incorrect"})
  try:
    doc_prediction_result = predict_doc_type(case_id,uid,gcs_url)
  except Exception as e:
    print(e)

    #DocumentStatus api call
    #FAILED_RESPONSE["case_id"] = case_id
    #FAILED_RESPONSE["uid"] = uid
    #requests.post("http://document-status-service/document_service/v1/update_classification_status",data=FAILED_RESPONSE)
    
    FAILED_RESPONSE["message"] = "Classification Failed"
    raise HTTPException(status_code=500, detail=FAILED_RESPONSE)

  print(doc_prediction_result)
  if doc_prediction_result:
    print(predict_doc_type)
    doc_type = ""
    if doc_prediction_result["predicted_class"] == "UE":
      doc_type = "AF"
    else:
      doc_type = "SD"
    SUCCESS_RESPONSE["case_id"] = doc_prediction_result["case_id"]
    SUCCESS_RESPONSE["uid"] =  uid
    SUCCESS_RESPONSE["type_of_doc"] = doc_type
    SUCCESS_RESPONSE["doc_class"] = doc_prediction_result["predicted_class"]
    
    #DocumentStatus api call
    #requests.post("http://document-status-service/document_service/v1/update_classification_status",data=SUCCESS_RESPONSE)
    
    return {"detail" : SUCCESS_RESPONSE}
  else:

    #DocumentStatus api call
    #FAILED_RESPONSE["case_id"] = case_id
    #FAILED_RESPONSE["uid"] = uid
    #requests.post("http://document-status-service/document_service/v1/update_classification_status",data=SUCCESS_RESPONSE)
    
    FAILED_RESPONSE["message"] = "Classification Failed"
    raise HTTPException(status_code=500,detail=FAILED_RESPONSE)