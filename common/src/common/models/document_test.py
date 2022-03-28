"""
Unit Tests for Document ORM object
"""

from common.models import Document
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import,ungrouped-imports
from common.testing.firestore_emulator import firestore_emulator, clean_firestore


def test_new_document_status(firestore_emulator):
  # unit test for document ORM
  case_id = "test_id123"
  document = Document(firestore_emulator)
  document.case_id = case_id
  document.save()
  assert document.case_id == case_id
