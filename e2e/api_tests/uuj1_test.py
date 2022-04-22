"""
  UUJ Arkansas - General upload documents
  get message for file is successfully uploaded
  process the document
  check all the stages ["uploaded","classification","extraction","auto_approval"] are successful
"""

import requests
from endpoint_proxy import get_baseurl
import os
import time
from helpers import is_processing_success

TESTDATA_FILENAME1 = os.path.join(
    os.path.dirname(__file__), "fake_data", "Copy of Arkansas-form-1.pdf")

TESTDATA_FILENAME2 = os.path.join(
    os.path.dirname(__file__), "fake_data", "arkansas-paystub-1.pdf")
TESTDATA_FILENAME3 = os.path.join(
    os.path.dirname(__file__), "fake_data", "Arkansas-claim-1.pdf")
TESTDATA_FILENAME4 = os.path.join(
    os.path.dirname(__file__), "fake_data", "DL-arkansas-1.pdf")
CONTEXT = "arkansas"

def test_uuj_1_arkansas(setup):
  """
    UUJ 1 - General upload one document with case_id workflow:
    submit Pdf document with one case_id
    get message for file is successfully uploaded
    process the document
    check all the stages ["uploaded","classification","extraction","auto_approval"] are successful
  """
  base_url = get_baseurl("upload-service")
  case_id = "test123x1"
  files = [("files", ("Copy of Arkansas-form-1.pdf", open(TESTDATA_FILENAME1,
                                                  "rb"), "application/pdf"))]
  response = requests.post(base_url+f"/upload_service/v1/upload_files?context={CONTEXT}&case_id={case_id}",files=files)
  assert response.status_code == 200
  data = response.json().get("configs")
  payload={"configs": data}
  response = requests.post(base_url+f"/upload_service/v1/process_task",json=payload)
  assert response.status_code == 202
  time.sleep(120)
  is_processed = is_processing_success(data)
  assert is_processed == True
  
  

def test_uuj_2_arkansas(setup):
  """
    UUJ 2 - General upload multiple documents with case_id workflow:
    submit Pdf document with one case_id
    get message for files are successfully uploaded
    process the document
    check all the stages ["uploaded","classification","extraction","validation","matching","auto_approval"] are successful
  """
  base_url = get_baseurl("upload-service")
  case_id = "test123x2"
  
  files = [("files", ("Copy of Arkansas-form-1.pdf", open(TESTDATA_FILENAME1,"rb"), "application/pdf")),
           ("files", ("arkansas-paystub-1.pdf", open(TESTDATA_FILENAME2,"rb"), "application/pdf")),
           ("files", ("Arkansas-claim-1.pdf", open(TESTDATA_FILENAME3,"rb"), "application/pdf")),
           ("files", ("DL-arkansas-1.pdf", open(TESTDATA_FILENAME4,"rb"), "application/pdf"))]
  response = requests.post(base_url+f"/upload_service/v1/upload_files?context={CONTEXT}&case_id={case_id}",files=files)
  assert response.status_code == 200
  data = response.json().get("configs")
  payload={"configs": data}
  response = requests.post(base_url+f"/upload_service/v1/process_task",json=payload)
  assert response.status_code == 202
  time.sleep(120)
  is_processed = is_processing_success(data)
  assert is_processed == True

def test_uuj_3_arkansas(setup):
  """
    UUJ 3 - General upload single document without case_id workflow:
    submit Pdf document without providing case_id
    get message for file is successfully uploaded
    process the document
    check all the stages ["uploaded","classification","extraction","validation","matching","auto_approval"] are successful
  """
  base_url = get_baseurl("upload-service")
  files = [("files", ("Copy of Arkansas-form-1.pdf", open(TESTDATA_FILENAME1,
                                                  "rb"), "application/pdf"))]
  response = requests.post(base_url+f"/upload_service/v1/upload_files?context={CONTEXT}",files=files)
  assert response.status_code == 200
  data = response.json().get("configs")
  payload={"configs": data}
  response = requests.post(base_url+f"/upload_service/v1/process_task",json=payload)
  assert response.status_code == 202
  time.sleep(120)
  is_processed = is_processing_success(data)
  assert is_processed == True

def test_uuj_4_arkansas(setup):
  """
    UUJ 4 - General upload multiple documents with case_id workflow:
    submit Pdf document without providing case_id
    get message for file is successfully uploaded
    process the document
    check all the stages ["uploaded","classification","extraction","validation","matching","auto_approval"] are successful
  """
  base_url = get_baseurl("upload-service")
  files = [("files", ("Copy of Arkansas-form-1.pdf", open(TESTDATA_FILENAME1,"rb"), "application/pdf")),
           ("files", ("arkansas-paystub-1.pdf", open(TESTDATA_FILENAME2,"rb"), "application/pdf")),
           ("files", ("Arkansas-claim-1.pdf", open(TESTDATA_FILENAME3,"rb"), "application/pdf")),
           ("files", ("DL-arkansas-1.pdf", open(TESTDATA_FILENAME4,"rb"), "application/pdf"))]
  response = requests.post(base_url+f"/upload_service/v1/upload_files?context={CONTEXT}",files=files)
  assert response.status_code == 200
  data = response.json().get("configs")
  payload={"configs": data}
  response = requests.post(base_url+f"/upload_service/v1/process_task",json=payload)
  assert response.status_code == 202
  time.sleep(120)
  is_processed = is_processing_success(data)
  assert is_processed == True
