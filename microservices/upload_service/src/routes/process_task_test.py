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
  Tests for process_task endpoint
"""
import os
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import,line-too-long
from unittest import mock
from testing.fastapi_fixtures import client_with_emulator
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from common.models import Document
from common.config import STATUS_IN_PROGRESS, STATUS_SUCCESS, STATUS_ERROR

# assigning url
API_URL = "http://localhost:8889/upload_service/v1/process_task"

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
SUCCESS_RESPONSE = {"status": STATUS_SUCCESS}


def test_process_task_api(client_with_emulator):
  """Test case to check the test_process_task_api endpoint"""
  doc = Document()
  doc.case_id = "case_arkansas_2001"
  doc.uid = "y13FLMQW4bYnHLa5t8dg"
  doc.save()
  doc.case_id = "case_arkansas_2001"
  doc.uid = "wZSrLgChiIR8NfWQkju5"
  doc.save()
  data={
      "configs": [
    {
      "case_id": "case_arkansas_2001",
      "uid": "y13FLMQW4bYnHLa5t8dg",
      "gcs_url": "gs://document-upload-test/case_arkansas_2001/"\
      "y13FLMQW4bYnHLa5t8dg/Copy of Arkansas-form-1.pdf",
      "context": "arkansas"
    },
    {
      "case_id": "case_arkansas_2001",
      "uid": "wZSrLgChiIR8NfWQkju5",
      "gcs_url": "gs://document-upload-test/case_arkansas_2001/"\
      "wZSrLgChiIR8NfWQkju5/DL-arkansas-1.pdf",
      "context": "arkansas"
    }
      ]
  }
  with mock.patch("utils.process_task_helpers.get_classification"):
    with mock.patch("utils.process_task_helpers.get_extraction_score"):
      with mock.patch("utils.process_task_helpers.get_validation_score"):
        with mock.patch("utils.process_task_helpers.get_matching_score"):
          with mock.patch(
              "utils.process_task_helpers.update_autoapproval_status"):
            with mock.patch("routes.process_task.Logger"):
              response = client_with_emulator.post(API_URL, json=data)
  assert response.status_code == 202, "Status 202"


def test_process_task_api_is_hitl(client_with_emulator):
  """Test case to check the test_process_task_api endpoint"""
  doc = Document()
  doc.case_id = "case_arkansas_2001"
  doc.uid = "y13FLMQW4bYnHLa5t8dg"
  doc.save()
  data={
      "configs": [
    {
      "case_id": "case_arkansas_2001",
      "uid": "y13FLMQW4bYnHLa5t8dg",
      "gcs_url": "gs://document-upload-test/case_arkansas_2001/"\
      "y13FLMQW4bYnHLa5t8dg/Copy of Arkansas-form-1.pdf",
      "context": "arkansas",
      "document_type": "application_form",
      "document_class": "unemployment_form"
    }
      ]
  }
  url = f"{API_URL}?is_hitl=true"
  with mock.patch("utils.process_task_helpers.get_classification"):
    with mock.patch("utils.process_task_helpers.get_extraction_score"):
      with mock.patch("utils.process_task_helpers.get_validation_score"):
        with mock.patch("utils.process_task_helpers.get_matching_score"):
          with mock.patch(
              "utils.process_task_helpers.update_autoapproval_status"):
            with mock.patch("routes.process_task.Logger"):
              response = client_with_emulator.post(url, json=data)
  assert response.status_code == 202, "Status 202"


def test_process_task_api_is_reassign(client_with_emulator):
  """Test case to check the test_process_task_api endpoint"""
  doc = Document()
  doc.case_id = "case_arkansas_2001"
  doc.uid = "wZSrLgChiIR8NfWQkju5"
  doc.save()
  data={
      "configs": [
    {
      "case_id": "case_arkansas_2001",
      "uid": "wZSrLgChiIR8NfWQkju5",
      "gcs_url": "gs://document-upload-test/case_arkansas_2001/"\
      "wZSrLgChiIR8NfWQkju5/DL-arkansas-1.pdf",
      "context": "arkansas"
    }
      ]
  }
  url = f"{API_URL}?is_reassign=true"
  with mock.patch("utils.process_task_helpers.get_classification"):
    with mock.patch("utils.process_task_helpers.get_extraction_score"):
      with mock.patch("utils.process_task_helpers.get_validation_score"):
        with mock.patch("utils.process_task_helpers.get_matching_score"):
          with mock.patch(
              "utils.process_task_helpers.update_autoapproval_status"):
            with mock.patch("routes.process_task.Logger"):
              response = client_with_emulator.post(url, json=data)
  assert response.status_code == 202, "Status 202"
