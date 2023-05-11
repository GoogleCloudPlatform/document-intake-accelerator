"""
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
  timestamp = datetime.datetime.utcnow()
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