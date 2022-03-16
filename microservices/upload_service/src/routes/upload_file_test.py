"""
  Tests for Upload endpoints
"""
import os
from unittest import mock
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import
from testing.fastapi_fixtures import client_with_emulator
from common.testing.firestore_emulator import firestore_emulator, clean_firestore

# assigning url
api_url = "http://localhost:8080/upload_service/v1/"
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
SUCCESS_RESPONSE = {"status": "Success"}


def test_upload_json_without_case_id_positive(client_with_emulator):
  with mock.patch("routes.upload_file.create_document_from_data"):
    response = client_with_emulator.post(
        f"{api_url}upload_json",
        json={
            "name": "Jon",
            "employer_name": "Quantiphi",
            "employer_phone_no": "9282112222",
            "context": "Callifornia",
            "dob": "7 Feb 1997",
            "document_type": "application/ supporting",
            "document_class": "unemployment",
            "ssn": "1234567",
            "phone_no": "9730388333",
            "application_apply_date": "2022/03/16",
            "mailing_address": "Arizona USA",
            "mailing_city": "Phoniex",
            "mailing_zip": "123-33-22",
            "residential_address": "Phoniex , USA",
            "work_end_date": "2022/03",
            "sex": "Female"
        })
    print(response)
    assert response.status_code == 200


def test_upload_json_with_case_id_positive(client_with_emulator):
  with mock.patch("routes.upload_file.create_document_from_data"):
    response = client_with_emulator.post(
        f"{api_url}upload_json",
        json={
            "case_id": "123A",
            "name": "Jon",
            "employer_name": "Quantiphi",
            "employer_phone_no": "9282112222",
            "context": "Callifornia",
            "dob": "7 Feb 1997",
            "document_type": "application/ supporting",
            "document_class": "unemployment",
            "ssn": "1234567",
            "phone_no": "9730388333",
            "application_apply_date": "2022/03/16",
            "mailing_address": "Arizona USA",
            "mailing_city": "Phoniex",
            "mailing_zip": "123-33-22",
            "residential_address": "Phoniex , USA",
            "work_end_date": "2022/03",
            "sex": "Female"
        })
    print(response)
    assert response.status_code == 200


def test_upload_file_json_negative(client_with_emulator):
  with mock.patch("routes.upload_file.create_document_from_data"):
    response = client_with_emulator.post(
        f"{api_url}upload_json",
        json={
            "case_id": "123A",
            "first_name": "Jon",
            "middle_name": "Max",
            "last_name": "Doe",
            "employer_name": "Quantiphi",
            "city": "New York",
            "state": "Callifornia",
            "dob": "7 Feb 1997"
        })
  print(response)
  assert response.status_code == 422
