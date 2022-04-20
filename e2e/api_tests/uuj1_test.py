"""
  UUJ 1 - General upload one document with case_id workflow:
  submit Pdf document with one case_id
  get message for file is successfully uploaded
"""

import requests
from endpoint_proxy import get_baseurl
import os
import json
TESTDATA_FILENAME1 = os.path.join(
    os.path.dirname(__file__), "fake_data", "Copy of Arkansas-form-1.pdf")

TESTDATA_FILENAME2 = os.path.join(
    os.path.dirname(__file__), "fake_data", "arkansas-paystub-1.pdf")
TESTDATA_FILENAME3 = os.path.join(
    os.path.dirname(__file__), "fake_data", "Arkansas-claim-1.pdf")
TESTDATA_FILENAME4 = os.path.join(
    os.path.dirname(__file__), "fake_data", "DL-arkansas-1.pdf")

def test_uuj_1():
  """
    UUJ 1 - General upload one document with case_id workflow:
    submit Pdf document with one case_id
    get message for file is successfully uploaded
  """
  base_url = get_baseurl("upload-service")
  case_id = 'test123x1'
  files = [("files", ("Copy of Arkansas-form-1.pdf", open(TESTDATA_FILENAME1,
                                                  "rb"), "application/pdf"))]
  response = requests.post(base_url+'/upload_service/v1/upload_files?context=arkansas&case_id=test123_x2',files=files)
  assert response.status_code == 200

def test_uuj_2():
  """
    UUJ 2 - General upload multiple documents with case_id workflow:
    submit Pdf document with one case_id
    get message for files are successfully uploaded
  """
  base_url = get_baseurl("upload-service")
  case_id = 'test123x2'
  files = [("files", ("Copy of Arkansas-form-1.pdf", open(TESTDATA_FILENAME1,"rb"), "application/pdf")),
           ("files", ("arkansas-paystub-1.pdf", open(TESTDATA_FILENAME2,"rb"), "application/pdf")),
           ("files", ("Arkansas-claim-1.pdf", open(TESTDATA_FILENAME3,"rb"), "application/pdf")),
           ("files", ("DL-arkansas-1.pdf", open(TESTDATA_FILENAME4,"rb"), "application/pdf"))]
  response = requests.post(base_url+'/upload_service/v1/upload_files?context=arkansas&case_id=test123_x2',files=files)
  assert response.status_code == 200

def test_uuj_3():
  """
    UUJ 3 - General upload single document without case_id workflow:
    submit Pdf document without providing case_id
    get message for file is successfully uploaded
  """
  base_url = get_baseurl("upload-service")
  files = [("files", ("Copy of Arkansas-form-1.pdf", open(TESTDATA_FILENAME1,
                                                  "rb"), "application/pdf"))]
  response = requests.post(base_url+'/upload_service/v1/upload_files?context=arkansas',files=files)
  assert response.status_code == 200

def test_uuj_4():
  """
    UUJ 4 - General upload multiple documents with case_id workflow:
    submit Pdf document without providing case_id
    get message for file is successfully uploaded
  """
  base_url = get_baseurl("upload-service")
  files = [("files", ("Copy of Arkansas-form-1.pdf", open(TESTDATA_FILENAME1,"rb"), "application/pdf")),
           ("files", ("arkansas-paystub-1.pdf", open(TESTDATA_FILENAME2,"rb"), "application/pdf")),
           ("files", ("Arkansas-claim-1.pdf", open(TESTDATA_FILENAME3,"rb"), "application/pdf")),
           ("files", ("DL-arkansas-1.pdf", open(TESTDATA_FILENAME4,"rb"), "application/pdf"))]
  response = requests.post(base_url+'/upload_service/v1/upload_files?context=arkansas',files=files)
  response_data = response.json()
  assert response.status_code == 200