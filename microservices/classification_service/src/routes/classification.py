""" classification endpoints """

from pydoc import doc
from fastapi import APIRouter
from fastapi import APIRouter, HTTPException, UploadFile, File
from google.cloud import storage
from common.models import Document
from google.cloud import storage
from google.cloud.storage import Blob
from services.classification_service import predict_doc_type
from fastapi.responses import HTMLResponse
import requests
from typing import Optional
# disabling for linting to pass
# pylint: disable = broad-except

router = APIRouter(prefix="/classification")
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}

def update_classification_status(case_id: str,uid: str,status: str,document_class: Optional[str] = None,document_type: Optional[str] = None):
  """ Call status update api to update the classification output
    Args:
    case_id (str): Case id of the file ,
     uid (str): unique id for  each document
     status (str): status success/failure depending on the validation_score

    """
  base_url = "http://document-status-service/document_status_service" \
    "/v1/update_classification_status"
  req_url = f"{base_url}?case_id={case_id}&uid={uid}" \
    f"&status={status}&document_class={document_class}&document_type={document_type}"
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
    raise HTTPException(status_code=400,detail={"status":"Failed", "message":"Parameters Missing"})
  if not gcs_url.endswith(".pdf") or not gcs_url.startswith("gs://"):
    raise HTTPException(status_code=400,detail={"status":"Failed", "message":"GCS pdf path is incorrect"})

  if case_id != gcs_url.split('/')[3] or uid != gcs_url.split('/')[4]:
    raise HTTPException(status_code=400,detail={"status":"Failed", "message":"Parameters Mismatched"})

  try:
    doc_prediction_result = predict_doc_type(case_id,uid,gcs_url)
    print(doc_prediction_result)
    if doc_prediction_result:
      print(predict_doc_type)
      if doc_prediction_result["predicted_class"] == "Negative":
        FAILED_RESPONSE["message"] = "Invalid Document"
        update_classification_status(case_id,uid,"failed")
        return {"detail" : FAILED_RESPONSE}
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
      update_classification_status(case_id,uid,"success",document_class=doc_prediction_result["predicted_class"],document_type=doc_type)
      
      return {"detail" : SUCCESS_RESPONSE}
    else:

      #DocumentStatus api call
      update_classification_status(case_id,uid,"failed")
      
      FAILED_RESPONSE["message"] = "Classification Failed"
      raise HTTPException(status_code=500,detail=FAILED_RESPONSE)

  except HTTPException as e:
    print(e)
    update_classification_status(case_id,uid,"failed")
    raise e
  except Exception as e:
    print(e)
    #DocumentStatus api call
    update_classification_status(case_id,uid,"failed")
    FAILED_RESPONSE["message"] = "Classification Failed"
    raise HTTPException(status_code=500, detail=FAILED_RESPONSE)

  