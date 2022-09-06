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
  Tests for Matching endpoints
"""
import os
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import
from testing.fastapi_fixtures import client_with_emulator
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from common.models import Document
from unittest.mock import patch
# assigning url
api_url = "http://localhost:8080/matching_service/v1/"

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
SUCCESS_RESPONSE = {"status": STATUS_SUCCESS}


def test_matching_api_all_ok(client_with_emulator):
  """Test case to check the matching endpoint"""

  doc = Document()

  doc.case_id = "test_id123"

  doc.uid = "2102"

  doc.active = "active"

  doc.document_class = "unemployment_form"

  doc.document_type = "application_form"

  doc.entities = [{"entity": "name", "value": "Mohit"}]
  doc.save()

  doc_sd = Document()

  doc_sd.case_id = "test_id123"

  doc_sd.uid = "2103"
  doc_sd.active = "active"

  doc_sd.document_class = "utility_bill"

  doc_sd.document_type = "supporting_documents"

  doc_sd.entities = [{"entity": "name", "value": "Mohi"}]
  doc_sd.save()

  with patch("routes.matching.get_matching_score", return_value=([], 0)):
    with patch(
        "routes.matching.update_matching_status",
        return_value={"status": STATUS_SUCCESS}):
      with patch("routes.matching.Logger"):
        response = client_with_emulator.post(
            f"{api_url}match_document?case_id=test_id123&uid=2103")
        print(response)
        assert response.status_code == 200, "Status 200"


def test_matching_api_no_af(client_with_emulator):
  """Test case to check the matching endpoint"""

  doc_sd = Document()

  doc_sd.case_id = "test_id123"

  doc_sd.uid = "2103"
  doc_sd.active = "active"

  doc_sd.document_class = "utility_bill"

  doc_sd.document_type = "supporting_documents"

  doc_sd.entities = [{
      "entity": "first name",
      "value": "Moh",
      "corrected_value": "Mohit"
  }]
  doc_sd.save()

  with patch("routes.matching.get_matching_score", return_value=([], 0)):
    with patch(
        "routes.matching.update_matching_status",
        return_value={"status": STATUS_SUCCESS}):
      with patch("routes.matching.Logger"):
        response = client_with_emulator.post(
            f"{api_url}match_document?case_id=test_id123&uid=2103")
        print(response)
        assert response.status_code == 404, "Status 404"


def test_matching_api_update_dsm_failed(client_with_emulator):
  """Test case to check the matching endpoint"""

  doc = Document()

  doc.case_id = "test_id123"

  doc.uid = "2102"

  doc.active = "active"

  doc.document_class = "unemployment_form"

  doc.document_type = "application_form"

  doc.entities = [{
      "entity": "first name",
      "value": "Moh",
      "corrected_value": "Mohit"
  }]
  doc.save()

  doc_sd = Document()

  doc_sd.case_id = "test_id123"

  doc_sd.uid = "2103"
  doc_sd.active = "active"

  doc_sd.document_class = "utility_bill"

  doc_sd.document_type = "supporting_documents"

  doc_sd.entities = [{
      "entity": "first name",
      "value": "Moh",
      "corrected_value": "Mohit"
  }]
  doc_sd.save()

  with patch("routes.matching.get_matching_score", return_value=([], 0)):
    with patch(
        "routes.matching.update_matching_status",
        return_value={"status": STATUS_ERROR}):
      with patch("routes.matching.Logger"):
        response = client_with_emulator.post(
            f"{api_url}match_document?case_id=test_id123&uid=2103")
        print(response)
        assert response.status_code == 500, "Status 500"


def test_matching_api_get_matching_failed(client_with_emulator):
  """Test case to check the matching endpoint"""

  doc = Document()
  doc.case_id = "test_id123"
  doc.uid = "2102"
  doc.active = "active"
  doc.document_class = "unemployment_form"
  doc.document_type = "application_form"
  doc.entities = [{
      "entity": "first name",
      "value": "Moh",
      "corrected_value": "Mohit"
  }]
  doc.save()

  doc_sd = Document()
  doc_sd.case_id = "test_id123"
  doc_sd.uid = "2103"
  doc_sd.active = "active"
  doc_sd.document_class = "utility_bill"
  doc_sd.document_type = "supporting_documents"
  doc_sd.entities = [{
      "entity": "first name",
      "value": "Moh",
      "corrected_value": "Mohit"
  }]
  doc_sd.save()

  with patch("routes.matching.get_matching_score", return_value=None):
    with patch(
        "routes.matching.update_matching_status",
        return_value={"status": STATUS_SUCCESS}):
      with patch("routes.matching.Logger"):
        response = client_with_emulator.post(
            f"{api_url}match_document?case_id=test_id123&uid=2103")
        print(response)
        assert response.status_code == 500, "Status 500"
