""" Upload and process task api endpoints """

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional, List
from schemas.input_data import InputData
import uuid
import requests
from common.utils.logging_handler import Logger
import utils.upload_file_gcs_bucket as ug

# pylint: disable = broad-except
router = APIRouter()
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}



@router.post("/upload_files")
async def upload_file(context: str,
                      files: List[UploadFile] = File(...),
                      case_id: Optional[str] = None):
  """Uploads files to the GCS bucket and Save the record in the database

  Args:
    case_id (str): Case id of the files it's optionl ,
    state (str) : state for which the application will be used
    list of files : to get the list of documents from user
  Returns:
    200 : PDF files are successfully uploaded
    422 : If file other than pdf is uploaded by user """
  for file in files:
    print(file.filename)
  print(context + case_id)
  return SUCCESS_RESPONSE


@router.post("/upload_json")
async def upload_data_json(input_data: InputData):
  """Uploads input  to the GCS bucket and Save the record in the database
    Args:
       input_data: input data schema for JSON
    Returns:
       200 : data successfully saved in system
       422 : incorrect data passed
       500 : if something fails
     """

  try:
    input_data = dict(input_data)
    entity = []
    document_class = input_data.pop("document_class")
    document_type = input_data.pop("document_type")
    context = input_data.pop("context")
    case_id = input_data.pop("case_id")
    """If case-id is none generate a new case_id"""
    if case_id is None:
      case_id = str(uuid.uuid1())
    """Converting Json to required format """
    for key, value in input_data.items():
      entity.append({"entity": key, "value": value, "extraction_confidence": 1})
    uid = create_document_from_data(case_id, document_type, document_class,
                                    context, entity)

    status = ug.upload_json_file(case_id, uid, str(entity))
    return {"status": status, "input_data": input_data, "case_id": case_id}
  except Exception as e:
    Logger.error(e)
    raise HTTPException(status_code=500, detail="Error in uploading document")

@router.post("/process_task")
async def process_task(case_id: str, uid: str, gcs_url: str):
  """Process the  input  he record in the database

    Args:
        case_id (str): Case id of the file ,
         uid : unique id for  each document
         gcs : gcs url of document
    Returns:
        200 : PDF files are successfully processed
        500  : HTTPException: 500 Internal Server Error if something fails
  """
  print(gcs_url)
  return {
      "status":
          "sucess",
      "message":
          f"File with case_id {case_id} , uid {uid} successfully processed"
  }


def create_document_from_data(case_id, document_type, document_class, context,
                              entity):
  base_url = "http://document-status-service/document_status_service/v1/"
  req_url = f"{base_url}create_documet_json_input"
  response = requests.post(
      f"{req_url}?case_id={case_id}&document_class={document_class}"
      f"&document_type={document_type}&context={context}",
      json=entity)
  response = response.json()
  uid = response["uid"]
  return uid
