"""
Unit Tests for Document ORM object
"""

from common.models import Document
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import
from testing.fastapi_fixtures import client_with_emulator
from common.testing.firestore_emulator import firestore_emulator, clean_firestore


def test_new_document_status(client_with_emulator):
  # unit test for document ORM
  case_id = "test_id123"
  document = Document()
  document.case_id = case_id
  document.save()
  assert document.case_id == case_id
