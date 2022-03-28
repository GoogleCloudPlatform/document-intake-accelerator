"""
Unit Tests for Document ORM object
"""

from common.models import Document


def test_new_document_status():
  # unit test for document ORM
  case_id = "test_id123"
  document = Document()
  document.case_id = case_id
  document.validation_score = 0.9
  document.save()
  assert document.case_id == case_id
