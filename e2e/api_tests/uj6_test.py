"""
  UUJ6 - E2E tests for checking
  HITL endpoint for table data
  is working
"""

import datetime
import requests
from endpoint_proxy import get_baseurl
from common.models.document import Document

def test_all_table_data():
  timestamp = str(datetime.datetime.utcnow())
  d = Document()
  d.case_id = "test_1"
  d.uid = "utest_1"
  d.active = "active"
  d.upload_timestamp = timestamp
  d.system_status = [{
    "stage":"uploaded",
    "status":"success",
    "timestamp":timestamp
  }]
  d.save()
  base_url = get_baseurl("hitl-service")
  res = requests.get(base_url + "/hitl_service/v1/report_data")
  assert res.status_code == 200

  res_data = res.json()
  print(res_data)

  assert res_data["len"] > 0
  assert res_data["data"] is not []
