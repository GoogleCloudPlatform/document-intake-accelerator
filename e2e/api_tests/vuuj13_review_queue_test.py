"""
  E2E tests for checking Review queue documents table
"""

import requests
from endpoint_proxy import get_baseurl
import datetime
from common.models.document import Document
from common.config import STATUS_IN_PROGRESS, STATUS_SUCCESS, STATUS_ERROR


def add_records():
  """
  Function to insert records with status review
  into collection that can be fetched by the API
  """

  timestamp = datetime.datetime.utcnow()

  d = Document()
  d.case_id = "uj11_review_test_1"
  d.uid = "uj11_review_test_1"
  d.active = "active"
  d.upload_timestamp = timestamp
  d.auto_approval = STATUS_REVIEW
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


def test_review_queue():
  """
  User journey to see all documents in review queue
  """
  #Adding Records
  add_records()

  #Getting base url for hitl service
  base_url = get_baseurl("hitl-service")

  status = STATUS_REVIEW
  res = requests.post(base_url + f"/hitl_service/v1/get_queue?"\
    f"hitl_status={status}")

  #Checking if response status is 200
  assert res.status_code == 200

  #Getting response data and checking the data is not empty
  res_data = res.json()
  print(res_data)
  assert res_data["len"] > 0
  assert res_data["data"] is not []
