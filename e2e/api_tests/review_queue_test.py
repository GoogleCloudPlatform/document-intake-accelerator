"""
  E2E tests for checking Review queue documents table
"""

import requests
from endpoint_proxy import get_baseurl
import datetime
from common.models.document import Document


def add_records():
  """
  Function to insert records with status review
  into collection that can be fetched by the API
  """

  timestamp = str(datetime.datetime.utcnow())

  d = Document()
  d.case_id = "uj11_review_test_1"
  d.uid = "uj11_review_test_1"
  d.active = "active"
  d.upload_timestamp = timestamp
  d.auto_approval = "Review"
  d.system_status = [{
      "stage": "uploaded",
      "status": "success",
      "timestamp": timestamp
  }, {
      "stage": "auto_approval",
      "status": "success",
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

  status = "review"
  res = requests.post(base_url + f"/hitl_service/v1/get_queue?"\
    f"hitl_status={status}")

  #Checking if response status is 200
  assert res.status_code == 200

  #Getting response data and checking the data is not empty
  res_data = res.json()
  print(res_data)
  assert res_data["len"] > 0
  assert res_data["data"] is not []
