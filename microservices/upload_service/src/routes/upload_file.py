""" Upload endpoints """

import datetime
from fastapi import APIRouter, HTTPException
from typing import Optional
from typing import List
from fastapi import FastAPI, File, UploadFile
import uuid
import utils.upload_file_gcs_bucket as ug

# pylint: disable = broad-except
router = APIRouter(prefix="/upload")
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}


@router.post("/upload_file")
async def upload_file(case_id: Optional[str] = None ,files: List[UploadFile] = File(...) ):
      filenames= [file.filename for file in files]
      return {"status": "Success", "case_id": case_id,"filenames": filenames}
