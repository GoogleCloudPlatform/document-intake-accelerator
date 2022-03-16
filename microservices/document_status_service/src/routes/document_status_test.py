"""
  Tests for Document status endpoints
"""
import os
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import
from testing.fastapi_fixtures import client_with_emulator
from common.models import Document
from common.testing.firestore_emulator import firestore_emulator, clean_firestore

# assigning url
api_url = "http://localhost:8080/document_status_service/v1/"
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
SUCCESS_RESPONSE = {"status": "Success"}


def create_document(client_with_emulator, case_id: str):
  response = client_with_emulator.post(
      f"{api_url}create_document?case_id={case_id}&filename="
      f"arkansaa.pdf&context=arizona",)
  response = response.json()
  uid = response["uid"]
  return uid


def test_create_document_positive(client_with_emulator):

  response = client_with_emulator.post(
      f"{api_url}create_document?case_id=345&filename="
      f"arkansaa.pdf&context=arizona",)
  print(response)
  assert response.status_code == 200


def test_create_document_negative(client_with_emulator):
  response = client_with_emulator.post(
      f"{api_url}create_document?filename=arkansaa.pdf&context=arizona",)
  print(response)
  assert response.status_code == 422


def test_extracion_status_update(client_with_emulator):
  uid = create_document(client_with_emulator, "test-01")
  response = client_with_emulator.post(
      f"{api_url}update_extraction_status?case_id=test-01&"
      f"uid={uid}&status=success&extraction_score=0.9",
      json=[{
          "key": "name",
          "raw-value": "Max"
      }, {
          "key": "last_name",
          "value": "Doe"
      }])
  print(response)
  assert response.status_code == 200


def test_validation_status_update(client_with_emulator):
  uid = create_document(client_with_emulator, "test-01")
  response = client_with_emulator.post(
      f"{api_url}update_validation_status?case_id=test-01&"
      f"uid={uid}&status=success&validation_score=9")
  print(response)
  assert response.status_code == 200


def test_matching_status_update(client_with_emulator):
  uid = create_document(client_with_emulator, "test-01")
  response = client_with_emulator.post(
      f"{api_url}update_matching_status?case_id=test-01"
      f"&uid={uid}&status=success&matching_score=0.9",
      json=[{
          "key": "name",
          "raw-value": "Max",
          "extraction_score": 0.1,
          "matching_score": 1
      }, {
          "key": "last_name",
          "value": "Doe",
          "extraction_score": 0.1,
          "matching_score": 1
      }])
  print(response)
  assert response.status_code == 200


def test_auto_approved_status_update(client_with_emulator):
  uid = create_document(client_with_emulator, "test-01")
  response = client_with_emulator.post(
      f"{api_url}update_autoapproved_status?case_id=test-01&uid={uid}"
      f"&status=success&autoapproved_status=accepted&"
      f"is_autoapproved=yes")
  assert response.status_code == 200


def test_create_documet_json_input(client_with_emulator):
  response = client_with_emulator.post(
      f"{api_url}create_documet_json_input?case_id=1236&document_class="
      f"unemployment&document_type=application&context=arizona",
      json=[{
          "entity": "name",
          "value": "Max",
          "extraction_confidence": 1
      }, {
          "entity": "last_name",
          "value": "Doe",
          "extraction_confidence": 1
      }])
  print(response)
  assert response.status_code == 200
