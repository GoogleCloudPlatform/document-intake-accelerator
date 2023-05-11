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
  E2E test case for download by HITL functionality
"""

import os
import time
import requests
from endpoint_proxy import get_baseurl

TESTDATA_FILENAME4 = os.path.join(
    os.path.dirname(__file__), "fake_data", "DL-arkansas-1.pdf")

def add_records(case_id):
  """
  Function to insert records
  """

  base_url = get_baseurl("upload-service")
  files = [("files", ("DL-arkansas-1.pdf", open(TESTDATA_FILENAME4,
                                           "rb"), "application/pdf"))]
  CONTEXT = "arkansas"

  response = requests.post(base_url+f"/upload_service/v1/upload_files?"\
    f"context={CONTEXT}&case_id={case_id}",files=files)

  #Check if the files were uploaded successfully
  assert response.status_code == 200

  #Get response data from the upload endpoint
  # and pass that as a parameter to process task endpoint
  data = response.json().get("configs")
  uid = response.json().get("uid_list")[0]
  payload={"configs": data}
  response = requests.post(base_url+f"/upload_service/v1/process_task",\
    json=payload)

  #Check if the processing is started
  assert response.status_code == 202

  #Waiting for process task to complete execution of the documents
  time.sleep(120)
  return uid

def test_download_document_api(setup):
  """"User journey to download a document"""
  case_id = "test123xdownload_test"
  uid = add_records(case_id)
  #Getting base url
  base_url = get_baseurl("hitl-service")
  #Checking if the request was successful
  res = requests.get(base_url + f"/hitl_service/v1/fetch_file?"\
    f"case_id={case_id}&uid={uid}&download={True}")
  assert res.status_code == 200
  assert res.headers["content-disposition"].split(";")[0] == "attachment"
