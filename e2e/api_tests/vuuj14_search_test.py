"""
  E2E tests for checking
  Search functionality
"""

import datetime
import requests
from endpoint_proxy import get_baseurl
from common.models.document import Document
from common.config import STATUS_IN_PROGRESS, STATUS_SUCCESS, STATUS_ERROR


def add_records():
  """
  Function to insert records into collection
  that can be searched and fetched by the API
  """
  timestamp = str(datetime.datetime.utcnow())
  d = Document()
  d.case_id = "uj7_search_test_1"
  d.uid = "uj7_search_test_1"
  d.active = "active"
  d.upload_timestamp = timestamp
  d.auto_approval = STATUS_APPROVED
  d.system_status = [{
      "stage": "uploaded",
      "status": STATUS_SUCCESS,
      "timestamp": timestamp
  }]
  d.save()

  d = Document()
  d.case_id = "uj7_search_test_2"
  d.uid = "uj7_search_test_2"
  d.active = "active"
  d.upload_timestamp = timestamp
  d.system_status = [{
      "stage": "uploaded",
      "status": STATUS_SUCCESS,
      "timestamp": timestamp
  }]
  d.entities = [{
      "entity": "name",
      "value": "James L fernandez",
      "corrected_value": None
  }]
  d.save()


def test_search():
  """
  User journey to perform search on the document records
  """
  #Inserting records
  add_records()

  #Getting base url of hitl service
  base_url = get_baseurl("hitl-service")

  #Preparing payload and making request
  #Searching for case_id
  payload = {"term": "uj7_search_test_1"}
  res = requests.post(base_url + f"/hitl_service/v1/search", json=payload)

  #Checking if the response status is 200
  assert res.status_code == 200

  res_data = res.json()
  print(res_data)

  #Checking if the response data is not empty
  assert res_data["len"] > 0
  assert res_data["data"] is not []

  #Searching for applicant name which is an extracted entity
  payload = {"term": "james"}
  res = requests.post(base_url + f"/hitl_service/v1/search", json=payload)
  res_data = res.json()
  print(res_data)

  assert res.status_code == 200
  assert res_data["len"] > 0
  assert res_data["data"] is not []