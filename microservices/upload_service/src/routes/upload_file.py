""" Upload and process task api endpoints """

import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File
from common.models import Documentstatus
from typing import Optional,List
from schemas.input_json import InputJson
import uuid
import utils.upload_file_gcs_bucket as ug

# pylint: disable = broad-except
router = APIRouter(prefix="/upload")
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}


@router.post("/upload_files")
async def upload_file(
    files: List[UploadFile] = File(...),case_id: Optional[str] = None):

    """Uploads files to the GCS bucket and Save the record in the database

    Args:
        case_id (str): Case id of the files it's optionl ,
        list of files : to get the list of documents from user
    Returns:
        200 : PDF files are successfully uploaded
        422 : If file other than pdf is uploaded by user """
    print(case_id)
    return SUCCESS_RESPONSE



@router.post("/upload_json")
async def upload_data_json(input : InputJson):

    """Uploads input  to the GCS bucket and Save the record in the database

    Args:
        case_id (str): Case id of the files it's optionl ,
         : to get the list of documents from user
    Returns:
        200 : PDF files are successfully uploaded
        422 : If file other than pdf is uploaded by user """


    print("Inside Json input")
    print(input)
    return {"status": "Success", "input_data": input}


@router.post("/process_task")
async def process_task(case_id : str , uid : str , gcs_url : str):

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
    return {"status": "sucess" , "message":f"File with case_id {case_id} , uid {uid} successfully processed"}


@router.post("/process_json")
async def process_json(case_id : str , uid : str , gcs_url : str):

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
    return {"status": "sucess" , "message":f"File with case_id {case_id} , uid {uid} successfully processed"}