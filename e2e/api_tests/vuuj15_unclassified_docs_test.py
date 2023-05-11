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
  E2E tests for checking Unclassified documents filter table
"""

import requests
from endpoint_proxy import get_baseurl
from common.models.document import Document
import datetime


def add_records():
  """
  Function to insert records that were either unclassified or
  the classification failed for some reason
  into collection that can be fetched by the API
  """

  timestamp = datetime.datetime.utcnow()
  d = Document()
  d.case_id = "unclassify_1"
  d.uid = "unclassify_1_uid"
  d.active = "active"
  d.upload_timestamp = timestamp
  d.system_status = [{
      "stage": "classification",
      "status": "unclassified",
      "is_hitl": False,
      "timestamp": timestamp
  }]
  d.save()


def test_unclassified_docs():
  """
  User journey to see all documents in review queue
  """
  #Adding Records
  add_records()

  #Getting base url for hitl service
  base_url = get_baseurl("hitl-service")

  res = requests.get(base_url + f"/hitl_service/v1/get_unclassified")

  #Checking if response status is 200
  assert res.status_code == 200

  #Getting response data and checking the data is not empty
  res_data = res.json()
  print(res_data)
  assert res_data["len"] > 0
  assert res_data["data"] is not []
