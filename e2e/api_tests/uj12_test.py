"""
  UJ12 - E2E tests for checking
  HITL endpoint for Unclassified documents table
"""

import requests
from endpoint_proxy import get_baseurl
from common.models.document import Document
import datetime

def test_unclassified_docs():
  timestamp = str(datetime.datetime.utcnow())
  d = Document()
  d.case_id = "unclassify_1"
  d.uid = "unclassify_1_uid"
  d.upload_timestamp = timestamp
  d.system_status = [{"stage":"classification",
                      "status":"unclassified",
                      "is_hitl":False,
                      "timestamp":timestamp
                      }]
  d.save()
  base_url = get_baseurl("hitl-service")
  print("here")
  res = requests.get(base_url + f"/hitl_service/v1/get_unclassified")
  assert res.status_code == 200
