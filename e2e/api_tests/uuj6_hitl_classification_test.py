"""
  E2E test for checking HITL classification of unclassified document
"""

import requests
from endpoint_proxy import get_baseurl
from common.models.document import Document
import os
import time
from helpers import is_processing_success

TESTDATA_FILENAME1 = os.path.join(
    os.path.dirname(__file__), "fake_data", "Copy of Arkansas-form-1.pdf")

TESTDATA_FILENAME2 = os.path.join(
    os.path.dirname(__file__), "fake_data", "arkansas-utility-1.pdf")

def is_doc_unclassified(details):
  """
  Function checks if the document with the data passed as arguement
  is unclassified or failed and returns the result as True or False
  """
  is_unclassified = False
  status = details["system_status"]
  #Checking if the last entry in system status trail is of classification
  # and the status was not successful
  if status[-1]["stage"].lower() == "classification" \
    and status[-1]["status"].lower() != "success":
    is_unclassified=True
  return is_unclassified

def upload_and_process():
  """
  Function to upload and process one application form and one
  supporting document with the same case_id and
  returns the data of the unclassified document
  """
  #Get base url of upload service and gather input
  base_url = get_baseurl("upload-service")
  case_id = "test123x1_unclassified"
  files = [("files", ("Copy of Arkansas-form-1.pdf", \
    open(TESTDATA_FILENAME1,"rb"), "application/pdf")),\
      ("files", ("arkansas-utility-1.pdf", open(TESTDATA_FILENAME2,
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

  #Check and get document that does not have a document class
  doc_data = None
  document = Document()
  for d in data:
    doc = document.find_by_uid(d["uid"])
    if doc.document_class is None:
      doc_data = doc.to_dict()
  assert doc_data is not None

  #Check if the document was unclassified
  is_unclassified = is_doc_unclassified(doc_data)
  assert is_unclassified == True

  return doc_data

def test_hitl_classification(setup):
  """
  User Journey to classify an unclassified document
  to an existing document class
  """
  #Upload and process documents
  data = upload_and_process()

  #Gathering input of unclassified document
  case_id = data["case_id"]
  uid = data["uid"]
  doc_class = "utility_bill"

  #Getting base url and marking the request
  base_url = get_baseurl("hitl-service")
  res = requests.post(base_url + f"/hitl_service/v1/update_hitl_classification"\
    f"?case_id={case_id}&uid={uid}&document_class={doc_class}")

  #Checking if the classification was successful
  assert res.status_code == 200

  #Waiting for the processing for this document to be completed
  time.sleep(120)

  #Check if the processing for this document is complete
  is_processed = is_processing_success([data])
  assert is_processed == True

  #Get document from database and check if the values are as expected
  d = Document()
  doc = d.find_by_uid(uid)
  assert doc.is_hitl_classified == True
  assert doc.document_class == "utility_bill"
  assert doc.document_type == "supporting_documents"
