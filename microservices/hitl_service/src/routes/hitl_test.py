"""
  Tests for hitl endpoints
"""
import os
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import
from testing.fastapi_fixtures import client_with_emulator
from common.testing.firestore_emulator import firestore_emulator, clean_firestore

# assigning url
api_url = "http://localhost:8080/hitl_service/v1/"

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
SUCCESS_RESPONSE = {"status": "Success"}


def test_report_data_api(client_with_emulator):
  """Test case to check the hitl endpoint"""

  response = client_with_emulator.get(f"{api_url}report_data")
  assert response.status_code == 200


def test_get_document_api(client_with_emulator):
  """Test case to check the hitl endpoint"""

  response = client_with_emulator.post(f"{api_url}get_document?uid=u123")
  assert response.status_code == 200


def test_get_queue_api(client_with_emulator):
  """Test case to check the hitl endpoint"""

  response = client_with_emulator.post(
      f"{api_url}get_queue?hitl_status=accepted")
  assert response.status_code == 200


def test_update_hitl_status_api(client_with_emulator):
  """Test case to check the hitl endpoint"""

  response = client_with_emulator.post(
      f"{api_url}update_hitl_status?uid=u123&status=accepted&user=Jon&comment="
  )
  assert response.status_code == 200


def test_update_entity_api(client_with_emulator):
  """Test case to check the hitl endpoint"""

  data = {
      "entities": [{
          "key": "first_name",
          "raw-value": "Mo",
          "corrected-value": "Mohit"
      }]
  }
  response = client_with_emulator.post(
      f"{api_url}update_entity?uid=u123", json=data)
  assert response.status_code == 200
