"""
  Tests for Document status endpoints
"""
import os
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import
from testing.fastapi_fixtures import client_with_emulator
from common.testing.firestore_emulator import firestore_emulator, clean_firestore

# assigning url
api_url = "http://localhost:8080/document_status_service/v1/"
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
SUCCESS_RESPONSE = {"status": "Success"}


def test_create_document_positive(client_with_emulator):

  response = client_with_emulator.post(
      f"{api_url}create_document?case_id=345&filename=arkansaa.pdf&context=arizona",
  )
  print(response)
  assert response.status_code == 200


def test_create_document_negative(client_with_emulator):
  response = client_with_emulator.post(
      f"{api_url}create_document?filename=arkansaa.pdf&context=arizona",)
  print(response)
  assert response.status_code == 422
