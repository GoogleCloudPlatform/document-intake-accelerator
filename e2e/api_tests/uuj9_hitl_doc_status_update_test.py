"""
  E2E tests for checking Document status update by HITL
"""

import requests
from endpoint_proxy import get_baseurl
from common.models.document import Document
import datetime

def add_records():
  """
  Function to insert records into collection
  """
  timestamp = str(datetime.datetime.utcnow())
  
  case_id = "uj15_update_status_test_1"
  uid = "uj15_update_status_test_1"
  d = Document()
  d.case_id = "uj15_update_status_test_1"
  d.uid = "uj15_update_status_test_1u"
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
  d.uid = "uj15_update_status_test_2u"
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
  """
  User journey to update the status of the document
  """
  #Inserting records
  add_records()
  
  uid = "uj15_update_status_test_1u"
  status = "rejected"
  user = "John.Adams"

  #Updating the status of document and checking if request was successful
  base_url = get_baseurl("hitl-service")
  res = requests.post(base_url + f"/hitl_service/v1/update_hitl_status?"\
    f"uid={uid}&status={status}&user={user}")
  assert res.status_code == 200

  #Checking if the status was successful
  res = requests.post(base_url + f"/hitl_service/v1/get_document?uid={uid}")
  assert res.status_code == 200
  res_data = res.json()
  print(res_data)
  assert res_data["data"]["current_status"].lower() == "rejected"


  uid = "uj15_update_status_test_2u"
  status = "approved"
  user = "John.Adams"

  #Updating the status of document and checking if request was successful
  res = requests.post(base_url + f"/hitl_service/v1/update_hitl_status?"\
    f"uid={uid}&status={status}&user={user}")
  assert res.status_code == 200

  #Checking if the status was successful
  res = requests.post(base_url + f"/hitl_service/v1/get_document?uid={uid}")
  assert res.status_code == 200
  res_data = res.json()
  print(res_data)
  assert res_data["data"]["current_status"].lower() == "approved"
