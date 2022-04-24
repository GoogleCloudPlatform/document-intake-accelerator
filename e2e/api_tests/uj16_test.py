"""
  UJ16 - E2E tests for checking
  document review by HITL
"""

import requests
from e2e.api_tests.uj6_test import add_records
from endpoint_proxy import get_baseurl
from common.models.document import Document
import datetime

def add_records(case_id,uid):
  """
  Function to insert records
  """
  timestamp = str(datetime.datetime.utcnow())
  d = Document()
  d.uid = uid
  d.case_id = case_id
  d.active = "active"
  d.context = "arkansas"
  d.upload_timestamp = timestamp
  d.document_type = "supporting_documents"
  d.system_status = [{"stage":"uploaded",
                      "status":"success",
                      "timestamp":timestamp
                    }]
  d.save()
  timestamp = str(datetime.datetime.utcnow())
  d = Document()
  d.uid = uid+"app"
  d.case_id = case_id
  d.document_type = "application_form"
  d.active = "active"
  d.context = "arkansas"
  d.upload_timestamp = timestamp
  d.system_status = [{"stage":"uploaded",
                      "status":"success",
                      "timestamp":timestamp
                    }]
  d.save()

def test_review_page():
  """
  User journey to review a document
  """
  #Inserting Records
  case_id = "769f79df-bf25-11ec-a675-43fd64c79606"
  uid = "aSCh3o6BxjPEqjMAQhtC"
  add_records(case_id,uid)

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