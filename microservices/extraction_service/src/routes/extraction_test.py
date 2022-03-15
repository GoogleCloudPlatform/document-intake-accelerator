"""
  Tests for extraction endpoints
"""
import os
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import
from testing.fastapi_fixtures import client_with_emulator
from common.testing.firestore_emulator import firestore_emulator, clean_firestore

# assigning url
api_url = "http://localhost:8080/extraction_service/v1/extraction/"

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
SUCCESS_RESPONSE = {"status": "Success"}


def test_classification_api(client_with_emulator):
  """Test case to check the classification endpoint"""

  response = client_with_emulator.post(
      f"{api_url}extraction_api?case_id=123A&uid=232a&doc_class=dl")
  print(response)
  assert response.status_code == 200, "Status 200"
