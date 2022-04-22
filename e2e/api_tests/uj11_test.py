"""
  UJ11 - E2E tests for checking
  HITL endpoint for Review documents table
"""

import requests
from endpoint_proxy import get_baseurl
import datetime
from common.models.document import Document

def add_records():
  timestamp = str(datetime.datetime.utcnow())

  d = Document()
  d.case_id = "uj11_rejected_test_1"
  d.uid = "uj11_rejected_test_1"
  d.active = "active"
  d.upload_timestamp = timestamp
  d.auto_approval = "Review"
  d.system_status = [{
    "stage":"uploaded",
    "status":"success",
    "timestamp":timestamp
  },
  {
    "stage":"auto_approval",
    "status":"success",
    "timestamp":timestamp
  }]
  d.save()


def test_review_queue():
  add_records()
  base_url = get_baseurl("hitl-service")
  status="review"
  res = requests.post(base_url + f"/hitl_service/v1/get_queue?"\
    f"hitl_status={status}")
  assert res.status_code == 200
  res_data = res.json()
  print(res_data)
  assert res_data["len"]>0
  assert res_data["data"] is not []
