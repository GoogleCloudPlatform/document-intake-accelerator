"""
  E2E tests for checking Rejected queue documents table
"""

import requests
from endpoint_proxy import get_baseurl
import datetime
from common.models.document import Document
from common.config import STATUS_IN_PROGRESS, STATUS_SUCCESS, STATUS_ERROR


def add_records():
  """
  Function to insert records with status rejected
  into collection that can be fetched by the API
  """
  #Inserting two documents 1 with auto approval status as rejected
  #and one with hitl status as rejected

  timestamp = str(datetime.datetime.utcnow())
  d = Document()
  d.case_id = "uj9_rejected_test_1"
  d.uid = "uj9_rejected_test_1"
  d.active = "active"
  d.upload_timestamp = timestamp
  d.auto_approval = "Rejected"
  d.system_status = [{
      "stage": "uploaded",
      "status": STATUS_SUCCESS,
      "timestamp": timestamp
  }, {
      "stage": "auto_approval",
      "status": STATUS_SUCCESS,
      "timestamp": timestamp
  }]
  d.save()

  d = Document()
  d.case_id = "uj9_rejected_test_2"
  d.uid = "uj9_rejected_test_2"
  d.active = "active"
  d.upload_timestamp = timestamp
  d.auto_approval = STATUS_APPROVED
  d.hitl_status = [{
      "status":
          "rejected",
      "user":
          "John Adam",
      "comment":
          "Approving",
      "timestamp":
          str(datetime.datetime.utcnow() + datetime.timedelta(seconds=3))
  }]
  d.system_status = [{
      "stage": "uploaded",
      "status": STATUS_SUCCESS,
      "timestamp": timestamp
  }, {
      "stage": "auto_approval",
      "status": STATUS_SUCCESS,
      "timestamp": timestamp
  }]
  d.save()


def test_rejected_queue():
  """
  User journey to see all documents in rejected queue
  """
  #Adding Records
  add_records()

  #Getting base url for hitl service
  base_url = get_baseurl("hitl-service")

  status = "rejected"
  res = requests.post(base_url + f"/hitl_service/v1/get_queue?"\
    f"hitl_status={status}")

  #Checking if response status is 200
  assert res.status_code == 200

  #Getting response data and checking the data is not empty
  res_data = res.json()
  print(res_data)
  assert res_data["len"] > 0
  assert res_data["data"] is not []
