"""
  Tests for classification endpoints
"""
import os
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import
from testing.fastapi_fixtures import client_with_emulator
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
# from .config_test import  TESTDATA_FILENAME1 ,TESTDATA_FILENAME2

# assigning url
api_url = "http://localhost:8080/classification_service/v1/classification/classification_api"

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
SUCCESS_RESPONSE = {"status": "Success"}


def test_classification_api(client_with_emulator):

  response = client_with_emulator.post(
      f"{api_url}",
      json={
          "case_id":
              "123A",
          "uid":
              "232a",
          "gcs_url":
              "http://storage.googleapis.com/document-upload-test/123A/232a/file_name",
      })
  print(response)
  assert response.status_code == 200, "Status 200"
