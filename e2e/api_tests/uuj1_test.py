"""
  UUJ 1 - General upload one document with case_id workflow:
  submit Pdf document with one case_id
  get message for file is successfully uploaded
"""

import requests
from endpoint_proxy import get_baseurl
import os
import time
from common.models.document import Document

TESTDATA_FILENAME1 = os.path.join(
    os.path.dirname(__file__), "fake_data", "Copy of Arkansas-form-1.pdf")

TESTDATA_FILENAME2 = os.path.join(
    os.path.dirname(__file__), "fake_data", "arkansas-paystub-1.pdf")
TESTDATA_FILENAME3 = os.path.join(
    os.path.dirname(__file__), "fake_data", "Arkansas-claim-1.pdf")
TESTDATA_FILENAME4 = os.path.join(
    os.path.dirname(__file__), "fake_data", "DL-arkansas-1.pdf")

def test_uuj_1(setup):
  """
    UUJ 1 - General upload one document with case_id workflow:
    submit Pdf document with one case_id
    get message for file is successfully uploaded
  """
  base_url = get_baseurl("upload-service")
  case_id = 'test123x1'
  context = "arkansas"
  files = [("files", ("Copy of Arkansas-form-1.pdf", open(TESTDATA_FILENAME1,
                                                  "rb"), "application/pdf"))]
  response = requests.post(base_url+f"/upload_service/v1/upload_files?context={context}&case_id={case_id}",files=files)
  assert response.status_code == 200
  data = response.json().get("configs")
  payload={"configs": data}
  print("=======data is=======",payload)
  response = requests.post(base_url+f"/upload_service/v1/process_task",json=payload)
  assert response.status_code == 202
  time.sleep(120)
  d = Document()
  for doc in data:
    uid = doc.get("uid")
    details=d.find_by_uid(uid)
    status = details.system_status
    print("System status is: ",status)
    stages = ["uploaded","classification","extraction","auto_approval"]
    if status is not None:
      for stat in status:
        assert stat.get("stage") in stages and stat.get("status") == "success"
  

# def test_uuj_2():
#   """
#     UUJ 2 - General upload multiple documents with case_id workflow:
#     submit Pdf document with one case_id
#     get message for files are successfully uploaded
#   """
#   base_url = get_baseurl("upload-service")
#   case_id = 'test123x2'
#   files = [("files", ("Copy of Arkansas-form-1.pdf", open(TESTDATA_FILENAME1,"rb"), "application/pdf")),
#            ("files", ("arkansas-paystub-1.pdf", open(TESTDATA_FILENAME2,"rb"), "application/pdf")),
#            ("files", ("Arkansas-claim-1.pdf", open(TESTDATA_FILENAME3,"rb"), "application/pdf")),
#            ("files", ("DL-arkansas-1.pdf", open(TESTDATA_FILENAME4,"rb"), "application/pdf"))]
#   response = requests.post(base_url+'/upload_service/v1/upload_files?context=arkansas&case_id=test123_x2',files=files)
#   assert response.status_code == 200

# def test_uuj_3():
#   """
#     UUJ 3 - General upload single document without case_id workflow:
#     submit Pdf document without providing case_id
#     get message for file is successfully uploaded
#   """
#   base_url = get_baseurl("upload-service")
#   files = [("files", ("Copy of Arkansas-form-1.pdf", open(TESTDATA_FILENAME1,
#                                                   "rb"), "application/pdf"))]
#   response = requests.post(base_url+'/upload_service/v1/upload_files?context=arkansas',files=files)
#   assert response.status_code == 200

# def test_uuj_4():
#   """
#     UUJ 4 - General upload multiple documents with case_id workflow:
#     submit Pdf document without providing case_id
#     get message for file is successfully uploaded
#   """
#   base_url = get_baseurl("upload-service")
#   files = [("files", ("Copy of Arkansas-form-1.pdf", open(TESTDATA_FILENAME1,"rb"), "application/pdf")),
#            ("files", ("arkansas-paystub-1.pdf", open(TESTDATA_FILENAME2,"rb"), "application/pdf")),
#            ("files", ("Arkansas-claim-1.pdf", open(TESTDATA_FILENAME3,"rb"), "application/pdf")),
#            ("files", ("DL-arkansas-1.pdf", open(TESTDATA_FILENAME4,"rb"), "application/pdf"))]
#   response = requests.post(base_url+'/upload_service/v1/upload_files?context=arkansas',files=files)
#   response_data = response.json()
#   assert response.status_code == 200