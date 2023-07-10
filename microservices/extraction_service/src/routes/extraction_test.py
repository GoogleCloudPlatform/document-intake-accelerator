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
  Tests for extraction endpoints
"""
import os
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import
from testing.fastapi_fixtures import client_with_emulator
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from unittest import mock
from unittest.mock import Mock, patch
from common.models import Document
from common.config import STATUS_IN_PROGRESS, STATUS_SUCCESS, STATUS_ERROR

# assigning url
api_url = "http://localhost:8080/extraction_service/v1/"

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
SUCCESS_RESPONSE = {"status": STATUS_SUCCESS}


def test_extraction_api_success(client_with_emulator):
  """
  Test case to check the Extraction
  endpoint success
  """
  doc = Document()
  doc.case_id = "123A"
  doc.uid = "aSCh3o6BxjPEqjMAQhtC"
  doc.document_class = "driving_license"
  doc.save()
  entities = [{
      "entity": "name",
      "value": "abc"
  }, {
      "entity": "last_name",
      "value": "xyzz"
  }]
  extract_entities_output = tuple([entities, 0.3, "double_key_extraction"])
  print(extract_entities_output)
  mockresponse = Mock()
  mockresponse.status_code = 200
  with mock.patch("routes.extraction.Logger"):
    with mock.patch(
        "routes.extraction.extract_entities",
        return_value=extract_entities_output):
      with mock.patch("routes.extraction.format_data_for_bq"):
        with mock.patch(
            "routes.extraction.stream_document_to_bigquery", return_value=[]):
          with mock.patch(
              "routes.extraction.update_extraction_status",
              return_value=mockresponse):
            response = client_with_emulator.post(
                f"{api_url}extraction_api?case_id=123A&uid=aSCh3o"
                f"6BxjPEqjMAQhtC&doc_class=driving_license&"
                f"context=arkansas&"
                f"gcs_url=gs://bucket_name/123A/aSCh3o6BxjPEqjMAQhtC/test.pdf")
            print(response)
  assert response.status_code == 200


def test_extraction_api_parser_not_available(client_with_emulator):
  """
  Test case to check the Extraction endpoint if
  parser not available for given document
  """
  doc = Document()
  doc.case_id = "123A"
  doc.uid = "aSCh3o6BxjPEqjMAQhtC"
  doc.document_class = "driving_license"
  doc.save()
  with mock.patch("routes.extraction.Logger"):
    with mock.patch("routes.extraction.extract_entities", return_value=None):
      with mock.patch("routes.extraction.format_data_for_bq"):
        with mock.patch("routes.extraction.stream_document_to_bigquery"):
          with mock.patch("routes.extraction.update_extraction_status"):
            response = client_with_emulator.post(
                f"{api_url}extraction_api?case_id=123A&"
                f"uid=aSCh3o6BxjPEqjMAQhtC&doc_class=driving_license&"
                f"context=arkansas&"
                f"gcs_url=gs://bucket_name/123A/aSCh3o6BxjPEqjMAQhtC/test.pdf")
            print(response)
            assert response.status_code == 404


def test_extraction_api_fail(client_with_emulator):
  """
  Test case to check the Extraction
  endpoint for failed condition """
  doc = Document()
  doc.case_id = "123A"
  doc.uid = "aSCh3o6BxjPEqjMAQhtC"
  doc.document_class = "driving_license"
  doc.save()
  with mock.patch("routes.extraction.Logger"):
    with mock.patch("routes.extraction.extract_entities", return_value="test"):
      with mock.patch("routes.extraction.format_data_for_bq"):
        with mock.patch("routes.extraction.stream_document_to_bigquery"):
          with mock.patch("routes.extraction.update_extraction_status"):
            response = client_with_emulator.post(
                f"{api_url}extraction_api?case_id=123A"
                f"&uid=aSCh3o6BxjPEqjMAQhtC&doc_class=driving_license&"
                f"context=arkansas"
                f"&gcs_url=gs://bucket_name/123A/aSCh3o6BxjPEqjMAQhtC/test.pdf")
            assert response.status_code == 500
