"""
Unit Tests for Document_status ORM object
"""

from common.models import Documentstatus


def test_new_document_status():
  # a placeholder unit test so github actions runs for check Models
  case_id = "test_id123"
  document = Documentstatus()
  document.case_id = case_id
  document.save()
  assert document.case_id == case_id
