"""
  E2E test case for document review by HITL
"""
import os
import requests
from endpoint_proxy import get_baseurl
from common.models.document import Document
import datetime
import time

TESTDATA_FILENAME1 = os.path.join(
    os.path.dirname(__file__), "fake_data", "Copy of Arkansas-form-1.pdf")
TESTDATA_FILENAME4 = os.path.join(
    os.path.dirname(__file__), "fake_data", "DL-arkansas-1.pdf")

def add_records(case_id):
  """
  Function to insert records
  """

  base_url = get_baseurl("upload-service")
  files = [("files", ("Copy of Arkansas-form-1.pdf", \
    open(TESTDATA_FILENAME1,"rb"), "application/pdf")),\
      ("files", ("DL-arkansas-1.pdf", open(TESTDATA_FILENAME4,
                                                  "rb"), "application/pdf"))]
  CONTEXT = "arkansas"

  response = requests.post(base_url+f"/upload_service/v1/upload_files?"\
    f"context={CONTEXT}&case_id={case_id}",files=files)

  #Check if the files were uploaded successfully
  assert response.status_code == 200

  #Get response data from the upload endpoint
  # and pass that as a parameter to process task endpoint 
  data = response.json().get("configs")
  payload={"configs": data}
  response = requests.post(base_url+f"/upload_service/v1/process_task",\
    json=payload)

  #Check if the processing is started
  assert response.status_code == 202

  #Waiting for process task to complete execution of the documents
  time.sleep(180)
  print(case_id)
  #Getting base url
  base_url = get_baseurl("hitl-service")
  payload = {"filter_key":"case_id","filter_value":case_id}
  res = requests.post(base_url + f"/hitl_service/v1/search",json=payload)
  assert res.status_code == 200
  res_docs = res.json()["data"]
  res_doc = list(filter(lambda i:i["document_type"]=="supporting_documents",res_docs))[0]
  return res_doc["uid"]


def test_review_page(setup):
  """
  User journey to review a document
  """
  #Inserting Records
  case_id = "test123xdoc_review_test"
  uid = add_records(case_id)

  #Getting base url
  base_url = get_baseurl("hitl-service")

  #Fetching the file for preview
  res = requests.get(base_url + f"/hitl_service/v1/fetch_file?"\
    f"case_id={case_id}&uid={uid}")

  assert res.status_code == 200
  assert res.headers["content-disposition"].split(";")[0] == "inline"

  #Getting the document data
  res = requests.post(base_url + f"/hitl_service/v1/get_document?uid={uid}")
  assert res.status_code == 200
  res_data = res.json()
  print(res_data)
  assert res_data["data"] is not []

  #Getting the corresponding application
  payload = {"filter_key":"case_id","filter_value":res_data["data"]["case_id"]}
  res = requests.post(base_url + f"/hitl_service/v1/search",json=payload)
  assert res.status_code == 200

  res_docs = res.json()["data"]
  app_form = None
  for d in res_docs:
    if d["document_type"].lower() == "application_form":
      app_form = d
      break
  assert app_form is not None