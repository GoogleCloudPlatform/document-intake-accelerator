"""
  UJ14 - E2E tests for checking
  HITL endpoint for Updating entity values with user provided values
"""

import requests
from endpoint_proxy import get_baseurl
from common.models.document import Document
import datetime

def add_records(entity,case_id,uid):
  timestamp = str(datetime.datetime.utcnow())
  
  d = Document()
  d.case_id = case_id
  d.uid = uid
  d.upload_timestamp = timestamp
  d.active="active"
  d.system_status = [{"stage":"uploaded",
                      "status":"success",
                      "timestamp":timestamp
                      }]
  d.entities = entity
  d.save()
  doc_dict = d.to_dict()
  return doc_dict

def test_update_entities():
  case_id = "uj14_update_entity_1"
  uid = "uj14_update_entity_uid_1"
  entity = [{"entity":"name",
            "value":"JAMES ADAM",
            "corrected_value":None
          }]
  doc_dict = add_records(entity,case_id,uid)  
  entity[0]["corrected_value"] = "James fernandez"
  doc_dict["entities"] = entity 
  base_url = get_baseurl("hitl-service")
  res = requests.post(base_url + f"/hitl_service/v1/update_entity?"\
    f"uid={uid}",json=doc_dict)
  assert res.status_code == 200
