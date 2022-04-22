"""
  UJ16 - E2E tests for checking
  HITL endpoint for document review
"""

import requests
from e2e.api_tests.uj6_test import add_records
from endpoint_proxy import get_baseurl
from common.models.document import Document
import datetime

def add_records(case_id,uid):
  timestamp = str(datetime.datetime.utcnow())
  d = Document()
  d.uid = uid
  d.case_id = case_id
  d.active = "active"
  d.context = "arkansas"
  d.upload_timestamp = timestamp
  d.system_status = [{"stage":"uploaded",
                      "status":"success",
                      "timestamp":timestamp
                    }]
  d.save()
  

def test_review_page():
  case_id = "769f79df-bf25-11ec-a675-43fd64c79606"
  uid = "aSCh3o6BxjPEqjMAQhtC"
  add_records(case_id,uid)
  base_url = get_baseurl("hitl-service")
  
  res = requests.get(base_url + f"/hitl_service/v1/fetch_file?"\
    f"case_id={case_id}&uid={uid}")
  print(res.headers["content-disposition"])

  assert res.status_code == 200
  assert res.headers["content-disposition"].split(";")[0] == "inline"

  res = requests.post(base_url + f"/hitl_service/v1/get_document?uid={uid}")
  assert res.status_code == 200
  res_data = res.json()
  print(res_data)
  assert res_data["data"] is not []