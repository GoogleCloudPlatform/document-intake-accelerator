"""
  UJ15 - E2E tests for checking
  HITL endpoint for document review
"""

import requests
from endpoint_proxy import get_baseurl
from common.models.document import Document
import datetime

def test_review_page():
  timestamp = str(datetime.datetime.utcnow())
  d = Document()
  d.uid = "aSCh3o6BxjPEqjMAQhtC"
  d.case_id = "769f79df-bf25-11ec-a675-43fd64c79606"
  d.context = "arkansas"
  d.upload_timestamp = str(datetime.datetime.utcnow())
  d.system_status = [{"stage":"uploaded",
                      "status":"success",
                      "timestamp":timestamp
                    }]
  d.save()
  
  base_url = get_baseurl("hitl-service")
  
  case_id = "769f79df-bf25-11ec-a675-43fd64c79606"
  uid = "aSCh3o6BxjPEqjMAQhtC"
  
  res = requests.get(base_url + f"/hitl_service/v1/fetch_file?"\
    f"case_id={case_id}&uid={uid}")
  assert res.status_code == 200

  res = requests.post(base_url + f"/hitl_service/v1/get_document?uid={uid}")
  assert res.status_code == 200