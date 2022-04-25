"""
  UUJ5 -User journey to check the reassign flow of a document

"""

import requests
from endpoint_proxy import get_baseurl
import os
import time
from common.models.document import Document
from helpers import is_processing_success , is_autoapproved

upload_base_url = get_baseurl("upload-service")
hitl_base_url = get_baseurl("hitl-service")


def test_reassign_user_journey(setup):
  """
    This test case describes then user journey of reassigning
    a supporting document
    1. User upload application with supporting document
    2. User uploads another application
    3. User selects a supporting document and selects other
    application where he wants to reassign the document
    4.User then clicks on reassign button to reassign the
    document
  """

  TESTDATA_APPLICATION1 = os.path.join(
    os.path.dirname(__file__), "fake_data", "California14.pdf")
  TESTDATA_APPLICATION2 = os.path.join(
    os.path.dirname(__file__), "fake_data", "California18.pdf")
  TESTDATA_SUPPORTING_DOC_DL = os.path.join(
    os.path.dirname(__file__), "fake_data", "california-dl-18.pdf")
  TESTDATA_SUPPORTING_DOC_PAYSTUB = os.path.join(
    os.path.dirname(__file__), "fake_data", "california-paystub-14.pdf")
  TESTDATA_SUPPORTING_UTILITY_BILL = os.path.join(
    os.path.dirname(__file__), "fake_data", "california-utility-bills-14.pdf")

  files1 = [("files", ("California14.pdf", open(TESTDATA_APPLICATION1,"rb"),
                       "application/pdf")),
           ("files", ("california-dl-18.pdf", open(TESTDATA_SUPPORTING_DOC_DL,"rb"),
                      "application/pdf")),
           ("files", ("california-paystub-14.pdf", open(TESTDATA_SUPPORTING_DOC_PAYSTUB, "rb"),
                      "application/pdf")),
           ("files", ("california-utility-bills-14.pdf", open(TESTDATA_SUPPORTING_UTILITY_BILL, "rb"),
                      "application/pdf"))
         ]

  files2 = [("files", ("California18.pdf", open(TESTDATA_APPLICATION2,"rb"),
                       "application/pdf"))]

  print(f"{upload_base_url}/upload_service/v1/upload_files?context=california&case_id=test1")

  #user uploads one supporting document and application form
  response_app1 = requests.post(
    f"{upload_base_url}/upload_service/v1/upload_files?context=california&case_id=test1",
    files=files1)
  #assert response from the upload API
  assert  response_app1.status_code == 200

  #user uploads another application form with different case_id
  response_app2 = requests.post(
    f"{upload_base_url}/upload_service/v1/upload_files?context="
    f"california&case_id=test2",
    files=files2)

  document_data1 = response_app1.json().get("configs")
  document_data2 = response_app2.json().get("configs")

  #assert the response from upload api
  assert  response_app2.status_code == 200

  #This is payload for Process task api  which is output of the upload API
  #payload for application and a supporting document to be processed
  payload_app1= {"configs": document_data1}
  print("=======data is=======", payload_app1)

  #payload for other application to be processed
  payload_app2 = {"configs":document_data2}

  #asserting process task api output for all uploaded documents
  response = requests.post(upload_base_url + f"/upload_service/v1/process_task",
                           json=payload_app2)
  assert response.status_code == 202

  response = requests.post(upload_base_url + f"/upload_service/v1/process_task",
                           json=payload_app1)
  assert response.status_code == 202

  #Adding time.sleep for  3 min so that all uploaded documents are processed
  time.sleep(120)

  #this for loop iterates on output of upload api response to  get uid
  # and case_id of the uploaded supporting document which will be
  #required for the reassign api as input
  for doc in document_data1:
    uid = doc.get("uid")
    document = Document.find_by_uid(uid)
    if document.document_type == "supporting_documents" and\
        document.document_class == "driving_licence":
      supporting_doc_case_id =  document.case_id
      supporting_doc_uid =  document.uid
    elif document.document_type == "application_form":
      application_case_id = document.case_id
      application_uid =  document.uid

  #is_processing is a helper functions which checks if all
  #uploaded documents succssfully processed and returns
  #boolean value
  is_processed1 = is_processing_success(document_data1)
  is_processed2 = is_processing_success(document_data2)

  #assert the processing of all uploaded documents is
  # successful
  assert  is_processed1 == True
  print("Before False")
  assert  is_processed2 == True
  print("After false")


  #assigning parameters for reassign paylod
  old_case_id = "test1"
  uid = supporting_doc_uid
  new_case_id =  "test2"

  #User journey to assert response when user assigns the
  # supporting document to same case_id user get's a bad
  #request response and reassign API gives 400 status
  #code

  reassign_data = {
    "old_case_id":old_case_id,
    "uid" : uid,
    "new_case_id" : old_case_id,
    "user" : "adam",
    "comment": "reassign user joueney"
  }

  reassign_response = requests.post(
    f"{hitl_base_url}/hitl_service/v1/reassign_case_id",json=reassign_data)
  assert  reassign_response.status_code == 400

  #User provides a wrong uid which does not exists in DB
  reassign_data = {
    "old_case_id": old_case_id,
    "uid": uid + "test",
    "new_case_id": new_case_id,
    "user": "adam",
    "comment": "reassign user joueney"
  }
  #assert document not found 404
  reassign_response = requests.post(
    f"{hitl_base_url}/hitl_service/v1/reassign_case_id", json=reassign_data)
  assert reassign_response.status_code == 404

  # when user tries to reassign a application instead of supporting
  #document user reassign api returns 406 status code
  reassign_data = {
    "old_case_id": application_case_id,
    "uid": application_uid,
    "new_case_id": new_case_id,
    "user": "adam",
    "comment": "reassign user joueney"
  }
  reassign_response = requests.post(
    f"{hitl_base_url}/hitl_service/v1/reassign_case_id", json=reassign_data)
  assert reassign_response.status_code == 406


  #reassign the supporting document to new case_id positive
  #response
  reassign_data = {
    "old_case_id":old_case_id,
    "uid" : uid,
    "new_case_id" : new_case_id,
    "user" : "adam",
    "comment": "reassign user joueney"
  }
  reassign_response = requests.post(
    f"{hitl_base_url}/hitl_service/v1/reassign_case_id", json=reassign_data)
  assert reassign_response.status_code == 200

  #adding time.sleep to check that document is processed
  #after the reassign process
  time.sleep(120)

  #asserting that the right hitl audit trail is added in
  #database
  document_final =  Document.find_by_uid(uid)
  print(document_final.hitl_status)
  assert  document_final.hitl_status != None

  #assert that the document which got reassigned is successfully
  #processed
  is_autoapproved_status = is_autoapproved(uid)
  assert is_autoapproved_status == True
