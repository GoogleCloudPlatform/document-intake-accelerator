"""
  UJ7 - E2E tests for checking
  Search functionality
"""

import requests
from e2e.api_tests.uj6_test import add_records
from endpoint_proxy import get_baseurl
from common.models.document import Document
import datetime

def add_records():
  timestamp = str(datetime.datetime.utcnow())
  d = Document()
  d.case_id = "uj7_search_test_1"
  d.uid = "uj7_search_test_1"
  d.active = "active"
  d.upload_timestamp = timestamp
  d.auto_approval = "Approved"
  d.system_status = [{
    "stage":"uploaded",
    "status":"success",
    "timestamp":timestamp
  }]
  d.save()

  d = Document()
  d.case_id = "uj7_search_test_2"
  d.uid = "uj7_search_test_2"
  d.active = "active"
  d.upload_timestamp = timestamp
  d.system_status = [{
    "stage":"uploaded",
    "status":"success",
    "timestamp":timestamp
  }]
  d.entities = [{
    "entity":"name",
    "value":"James L fernandez",
    "corrected_value":None
  }]
  d.save()

def test_search():
  add_records()
  base_url = get_baseurl("hitl-service")
  payload = {"term":"uj7_search_test_1"}
  res = requests.post(base_url + f"/hitl_service/v1/search",json=payload)
  print(res)
  res_data = res.json()
  print(res_data)
  
  assert res.status_code == 200
  res_data = res.json()
  print(res_data)
  assert res_data["len"] > 0
  assert res_data["data"] is not []

  payload = {"term":"james"}
  res = requests.post(base_url + f"/hitl_service/v1/search",json=payload)
  print(res)
  res_data = res.json()
  print(res_data)
  
  assert res.status_code == 200
  assert res_data["len"] > 0
  assert res_data["data"] is not []