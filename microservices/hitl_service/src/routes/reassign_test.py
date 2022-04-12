"""
  Tests for hitl endpoints
"""
import os
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import
from testing.fastapi_fixtures import client_with_emulator
from testing.test_config import supporting_document_data, application_document_data
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from unittest import mock
from unittest.mock import Mock
from common.models.document import Document
# assigning url
api_url = "http://localhost:8080/hitl_service/v1/"

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
SUCCESS_RESPONSE = {"status": "Success"}


def create_document(data):
  document = Document()
  document.case_id = data.get("case_id")
  document.uid = data.get("uid")
  document.context = data.get("context")
  document.url = data.get("url")
  document.entities = data.get("entities")
  document.document_class = data.get("document_class")
  document.document_type = data.get("document_type")
  document.save()


def test_reassigne_application_form(client_with_emulator):
  create_document(supporting_document_data)
  create_document(application_document_data)
  data = {
      "old_case_id": "123A",
      "uid": "7CBdJrVpbKolmbm2MYLX",
      "new_case_id": "test456",
      "user": "Max",
      "comment": "reassign the application form"
  }
  with mock.patch("routes.reassign.Logger"):
    with mock.patch("routes.reassign.copy_blob"):
      with mock.patch("routes.reassign.stream_document_to_bigquery"):
        with mock.patch("routes.reassign.format_data_for_bq"):
          response = client_with_emulator.post(
              f"{api_url}reassign_case_id", json=data)
    print(response)
  assert response.status_code == 406


def test_document_to_reassign_not_found(client_with_emulator):
  create_document(supporting_document_data)
  create_document(application_document_data)
  data = {
      "old_case_id": "123AB",
      "uid": "7CBdJrVpbKolmbm2MYsdsdLX",
      "new_case_id": "test456",
      "user": "Max",
      "comment": "reassign the application form"
  }
  with mock.patch("routes.reassign.Logger"):
    with mock.patch("routes.reassign.copy_blob"):
      with mock.patch("routes.reassign.stream_document_to_bigquery"):
        with mock.patch("routes.reassign.format_data_for_bq"):
          response = client_with_emulator.post(
              f"{api_url}reassign_case_id", json=data)
    print(response)
  assert response.status_code == 404


def test_document_reassign_positive(client_with_emulator):
  create_document(supporting_document_data)
  create_document(application_document_data)
  data = {
      "old_case_id": "123A1",
      "uid": "7CBdJrVpbKolmbm2MYLxx",
      "new_case_id": "123A",
      "user": "Max",
      "comment": "reassign the application form"
  }
  mockresponse = Mock()
  mockresponse.status_code = 201
  with mock.patch("routes.reassign.Logger"):
    with mock.patch("routes.reassign.copy_blob", return_value="success"):
      with mock.patch(
          "routes.reassign.stream_document_to_bigquery", return_value=[]):
        with mock.patch("routes.reassign.format_data_for_bq"):
          with mock.patch(
              "routes.reassign.call_process_task",
              return_value=mockresponse.status_code):
            response = client_with_emulator.post(
                f"{api_url}reassign_case_id", json=data)
    print(response)
  assert response.status_code == 200


def test_new_application_not_found(client_with_emulator):
  create_document(supporting_document_data)
  create_document(application_document_data)
  data = {
      "old_case_id": "123AB",
      "uid": "7CBdJrVpbKolmbm2MYsdsdLX",
      "new_case_id": "test43e56",
      "user": "Max",
      "comment": "reassign the application form"
  }
  with mock.patch("routes.reassign.Logger"):
    with mock.patch("routes.reassign.copy_blob"):
      with mock.patch("routes.reassign.stream_document_to_bigquery"):
        with mock.patch("routes.reassign.format_data_for_bq"):
          response = client_with_emulator.post(
              f"{api_url}reassign_case_id", json=data)
    print(response)
  assert response.status_code == 404


def test_same_old_and_new_case_id(client_with_emulator):
  create_document(supporting_document_data)
  create_document(application_document_data)
  data = {
      "old_case_id": "123AB",
      "uid": "7CBdJrVpbKolmbm2MYsdsdLX",
      "new_case_id": "123AB",
      "user": "Max",
      "comment": "reassign the application form"
  }
  with mock.patch("routes.reassign.Logger"):
    with mock.patch("routes.reassign.copy_blob"):
      with mock.patch("routes.reassign.stream_document_to_bigquery"):
        with mock.patch("routes.reassign.format_data_for_bq"):
          response = client_with_emulator.post(
              f"{api_url}reassign_case_id", json=data)
    print(response)
  assert response.status_code == 404

