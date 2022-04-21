"""
  UJ14 - E2E tests for checking
  HITL endpoint for Updating entity values with user provided values
"""

import requests
from endpoint_proxy import get_baseurl
from common.models.document import Document
import datetime

def test_update_entities():
  timestamp = str(datetime.datetime.utcnow())
  case_id = "update_entity_1"
  uid = "update_entity_uid_1"
  entity = [{"entity":"name",
            "value":"JAMES ADAM",
            "corrected_value":None
          }]
  d = Document()
  d.case_id = case_id
  d.uid = uid
  d.upload_timestamp = timestamp
  d.system_status = [{"stage":"uploaded",
                      "status":"success",
                      "timestamp":timestamp
                      }]
  d.entities = entity
  d.save()
  doc_dict = d.to_dict()
  entity[0]["corrected_value"] = "James fernandez"
  doc_dict["entities"] = entity 
  base_url = get_baseurl("hitl-service")
  res = requests.post(base_url + f"/hitl_service/v1/update_entity?"\
    f"uid={uid}",json=doc_dict)
  assert res.status_code == 200
