"""
  UJ13 - E2E tests for checking
  HITL endpoint for Updating Document status by HITL
"""

import requests
from endpoint_proxy import get_baseurl
from common.models.document import Document
import datetime

def add_records():
  timestamp = str(datetime.datetime.utcnow())
  
  case_id = "uj15_update_status_test_1"
  uid = "uj15_update_status_test_1"
  d = Document()
  d.case_id = "uj15_update_status_test_1"
  d.uid = "uj15_update_status_test_1"
  d.upload_timestamp = timestamp
  d.active="active"
  d.auto_approval = "Approved"
  d.system_status = [{"stage":"uploaded",
                      "status":"success",
                      "timestamp":timestamp
                      },
                      {
                      "stage":"auto_approval",
                      "status":"success",
                      "timestamp":timestamp
                      }]
  d.save()

  d = Document()
  d.case_id = "uj15_update_status_test_2"
  d.uid = "uj15_update_status_test_2"
  d.upload_timestamp = timestamp
  d.active="active"
  d.auto_approval = "Approved"
  d.system_status = [{"stage":"uploaded",
                      "status":"success",
                      "timestamp":timestamp
                      },
                      {
                      "stage":"auto_approval",
                      "status":"success",
                      "timestamp":timestamp
                      }]
  d.hitl_status=[{
    "status":"rejected",
    "user":"john.adams",
    "comment":"",
    "timestamp":str(datetime.datetime.utcnow())
  }]
  d.save()


def test_update_entities():
  add_records()
  
  uid = "uj15_update_status_test_1"
  status = "rejected"
  user = "John.Adams"

  base_url = get_baseurl("hitl-service")
  res = requests.post(base_url + f"/hitl_service/v1/update_hitl_status?"\
    f"uid={uid}&status={status}&user={user}")
  assert res.status_code == 200

  uid = "uj15_update_status_test_2"
  status = "approved"
  user = "John.Adams"
  res = requests.post(base_url + f"/hitl_service/v1/update_hitl_status?"\
    f"uid={uid}&status={status}&user={user}")
  assert res.status_code == 200
