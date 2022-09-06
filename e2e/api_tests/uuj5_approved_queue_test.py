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
  E2E tests for checking Approved queue documents table
"""

import requests
from endpoint_proxy import get_baseurl
import datetime
from common.models.document import Document
from common.config import STATUS_IN_PROGRESS, STATUS_SUCCESS, STATUS_ERROR, STATUS_APPROVED


def add_records():
  """
  Function to insert records with status approved
  into collection that can be fetched by the API
  """
  #Inserting two documents 1 with auto approval status as approved
  #and one with hitl status as approved

  timestamp = datetime.datetime.utcnow()
  d = Document()
  d.case_id = "uj8_approved_test_1"
  d.uid = "uj8_approved_test_1"
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
  d.case_id = "uj8_approved_test_2"
  d.uid = "uj8_approved_test_2"
  d.active = "active"
  d.upload_timestamp = timestamp
  d.auto_approval = "Rejected"
  d.hitl_status = [{
      "status":
          STATUS_APPROVED,
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


def test_approved_queue():
  """
  User journey to see all documents in approved queue
  """
  #Adding Records
  add_records()

  #Getting base url for hitl service
  base_url = get_baseurl("hitl-service")

  status = STATUS_APPROVED
  res = requests.post(base_url + f"/hitl_service/v1/get_queue?"\
    f"hitl_status={status}")

  #Checking if response status is 200
  assert res.status_code == 200

  #Getting response data and checking the data is not empty
  res_data = res.json()
  print(res_data)
  assert res_data["len"] > 0
  assert res_data["data"] is not []
