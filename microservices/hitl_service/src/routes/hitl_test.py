"""
  Tests for hitl endpoints
"""
import os
import json
from unittest.mock import Mock, patch
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import
from testing.fastapi_fixtures import client_with_emulator
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from common.models.document import Document
# assigning url
api_url = "http://localhost:8080/hitl_service/v1/"

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
SUCCESS_RESPONSE = {"status": "Success"}


def test_report_data_api(client_with_emulator):
  """Test case to check the report_data hitl endpoint"""

  response = client_with_emulator.get(f"{api_url}report_data")
  assert response.status_code == 200


def test_get_document_api(client_with_emulator):
  """Test case to check the get_document hitl endpoint"""
  d = Document()
  d.uid = "u123"
  d.active = "active"
  d.save()
  response = client_with_emulator.post(f"{api_url}get_document?uid=u123")
  print(response)
  assert response.status_code == 200


def test_get_document_api_invalid_uid(client_with_emulator):
  """Test case to check the get_document hitl endpoint"""

  d = Document()
  d.uid = "u123"
  d.active = "active"
  d.save()
  response = client_with_emulator.post(f"{api_url}get_document?uid=u12")
  res = response.json()
  print(res)
  json_response = json.loads(response.text)
  print(json_response)

  assert response.status_code == 200
  assert json_response["status"] == "Failed"


def test_get_queue_api(client_with_emulator):
  """Test case to check the get_queue hitl endpoint"""

  d = Document()
  d.hitl_status = [{"status": "approved","user": "Adam","timestamp": "12.00"}]
  d.active = "active"
  d.save()
  response = client_with_emulator.post(
      f"{api_url}get_queue?hitl_status=approved")
  assert response.status_code == 200


def test_get_queue_api_invalid_status(client_with_emulator):
  """Test case to check the get_queue hitl endpoint"""

  d = Document()
  d.active = "active"
  d.hitl_status = [{"status": "approved", "user": "Adam", "timestamp": "12.00"}]
  d.save()
  response = client_with_emulator.post(
      f"{api_url}get_queue?hitl_status=accepted")
  assert response.status_code == 400


def test_update_hitl_status_api(client_with_emulator):
  """Test case to check the update_hitl_status hitl endpoint"""

  d = Document()
  d.active = "active"
  d.uid = "u123"
  d.hitl_status = []
  d.save()
  response = client_with_emulator.post(
      f"{api_url}update_hitl_status?uid=u123&status=approved&user=Jon&comment=")
  assert response.status_code == 200


def test_update_hitl_status_api_invalid_uid(client_with_emulator):
  """Test case to check the update_hitl_status hitl endpoint"""
  d = Document()
  d.uid = "u123"
  d.active = "active"
  d.hitl_status = []
  d.save()
  response = client_with_emulator.post(
      f"{api_url}update_hitl_status?uid=u12&status=approved&user=Jon&comment=")
  assert response.status_code == 200
  json_response = json.loads(response.text)
  assert json_response["status"] == "Failed"


def test_update_hitl_status_api_invalid_status(client_with_emulator):
  """Test case to check the update_hitl_status hitl endpoint"""
  d = Document()
  d.uid = "u123"
  d.hitl_status = []
  d.active = "active"
  d.save()
  response = client_with_emulator.post(
      f"{api_url}update_hitl_status?uid=u123&status=accepted&user=Jon&comment=")
  assert response.status_code == 400


def test_update_entity_api(client_with_emulator):
  """Test case to check the update_entity hitl endpoint"""

  d = Document()
  d.uid = "u123"
  d.entities = []
  d.active = "active"
  d.save()
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


def test_update_entity_api_invalid_uid(client_with_emulator):
  """Test case to check the update_entity hitl endpoint"""
  d = Document()
  d.uid = "u123"
  d.active = "active"
  d.entities = []
  d.save()

  data = {
      "entities": [{
          "key": "first_name",
          "raw-value": "Mo",
          "corrected-value": "Mohit"
      }]
  }
  response = client_with_emulator.post(
      f"{api_url}update_entity?uid=u12", json=data)
  assert response.status_code == 200
  json_response = json.loads(response.text)
  assert json_response["status"] == "Failed"


def test_fetch_api(client_with_emulator):
  """Test case to check the fetch_file hitl endpoint"""

  response = client_with_emulator.get(
      f"{api_url}fetch_file?case_id= wwe&uid=CS2EeDc2Gl0OAkdZ4rWK")
  assert response.status_code == 200


def test_fetch_api_download(client_with_emulator):
  """Test case to check the fetch_file hitl endpoint"""

  response = client_with_emulator.get(
    f"{api_url}fetch_file?case_id= wwe&uid=CS2EeDc2Gl0OAkdZ4rWK&download=true"
  )
  assert response.status_code == 200


def test_fetch_api_invalid_case_id(client_with_emulator):
  """Test case to check the fetch_file hitl endpoint"""

  response = client_with_emulator.get(
      f"{api_url}fetch_file?case_id= ww&uid=CS2EeDc2Gl0OAkdZ4rWK")
  assert response.status_code == 404


def test_fetch_api_invalid_uid(client_with_emulator):
  """Test case to check the fetch_file hitl endpoint"""

  response = client_with_emulator.get(
      f"{api_url}fetch_file?case_id= wwe&uid=CS2EeDc2Gl0OAkdZ4r")
  assert response.status_code == 404


def test_get_unclassified_api(client_with_emulator):
  """Test case to check the get_unclassified hitl endpoint"""
  d = Document()
  d.uid = "u123"
  d.active = "active"
  d.system_status = [{"stage": "classification", "status": "unclassified"}]
  d.save()
  response = client_with_emulator.get(f"{api_url}get_unclassified")
  assert response.status_code == 200


def test_update_hitl_classification_api(client_with_emulator):
  """Test case to check the update_hitl_classification hitl endpoint"""
  d = Document()
  d.case_id = "test_case"
  d.uid = "u123"
  d.active = "active"
  d.system_status = [{"stage": "classification", "status": "unclassified"}]
  d.document_class = None
  d.document_type = None
  d.save()

  case_id = "test_case"
  uid = "u123"
  document_class = "driving_licence"

  mockresponse = Mock()
  mockresponse.status_code = 200
  
  process_mockresponse = Mock()
  process_mockresponse.status_code = 202
  with patch(
      "routes.hitl.call_process_task", return_value=process_mockresponse):
    with patch(
        "routes.hitl.update_classification_status", return_value=mockresponse):
      response = client_with_emulator.post(
        f"{api_url}update_hitl_classification?case_id={case_id}"\
          f"&uid={uid}&document_class={document_class}"
      )
      assert response.status_code == 200


def test_update_hitl_classification_api_invalid_doc_type(client_with_emulator):
  """Test case to check the update_hitl_classification hitl endpoint"""
  d = Document()
  d.case_id = "test_case"
  d.uid = "u123"
  d.system_status = [{"stage": "classification", "status": "unclassified"}]
  d.document_class = None
  d.document_type = None
  d.active = "active"
  d.save()

  case_id = "test_case"
  uid = "u123"
  document_class = "driver_licence"

  mockresponse = Mock()
  mockresponse.status_code = 400

  process_mockresponse = Mock()
  process_mockresponse.status_code = 202
  with patch(
      "routes.hitl.call_process_task", return_value=process_mockresponse):
    with patch(
        "routes.hitl.update_classification_status", return_value=mockresponse):
      response = client_with_emulator.post(
          f"{api_url}update_hitl_classification?case_id={case_id}"\
            f"&uid={uid}&document_class={document_class}"
      )
      assert response.status_code == 400
