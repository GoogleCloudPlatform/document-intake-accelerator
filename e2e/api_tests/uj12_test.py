"""
  UJ12 - E2E tests for checking
  HITL endpoint for Unclassified documents table
"""

import requests
from endpoint_proxy import get_baseurl
from common.models.document import Document
import datetime

def add_records():
  timestamp = str(datetime.datetime.utcnow())
  d = Document()
  d.case_id = "unclassify_1"
  d.uid = "unclassify_1_uid"
  d.active = "active"
  d.upload_timestamp = timestamp
  d.system_status = [{"stage":"classification",
                      "status":"unclassified",
                      "is_hitl":False,
                      "timestamp":timestamp
                      }]
  d.save()

def test_unclassified_docs():
  add_records()
  base_url = get_baseurl("hitl-service")
  print("here")
  res = requests.get(base_url + f"/hitl_service/v1/get_unclassified")
  assert res.status_code == 200
  res_data = res.json()
  print(res_data)
  assert res_data["len"]>0
  assert res_data["data"] is not []

