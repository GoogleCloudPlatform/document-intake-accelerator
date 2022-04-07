"""
  Tests for process_task endpoint
"""
import os
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import
from unittest import mock
from testing.fastapi_fixtures import client_with_emulator
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from common.models import Document

# assigning url
API_URL = "http://localhost:8889/upload_service/v1/process_task"

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
SUCCESS_RESPONSE = {"status": "Success"}


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
  with mock.patch("routes.process_task.get_classification"):
    with mock.patch("routes.process_task.get_extraction_score"):
      with mock.patch("routes.process_task.get_validation_score"):
        with mock.patch("routes.process_task.get_matching_score"):
          with mock.patch("routes.process_task.update_autoapproval_status"):
            with mock.patch("routes.process_task.Logger"):
              with mock.patch("routes.process_task.filter_documents"):
                response = client_with_emulator.post(
                  API_URL, json=data)
  assert response.status_code == 202, "Status 202"

