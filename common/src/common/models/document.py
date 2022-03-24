"""
Document Status object in the ORM
"""
import os
from common.models import BaseModel
from fireo.fields import TextField,ListField ,NumberField

DATABASE_PREFIX = os.getenv("DATABASE_PREFIX", "")
PROJECT_ID = os.environ.get("PROJECT_ID", "")

class Document(BaseModel):
  """Documentstatus ORM class  """
  case_id = TextField()
  uid = TextField()
  url = TextField()
  document_type  = TextField()
  document_class = TextField()
  context = TextField()
  system_status = ListField()
  hitl_status = ListField()
  active = TextField()
  upload_timestamp = TextField()
  entities = ListField()
  extraction_score = NumberField()
  validation_score = NumberField()
  matching_score = NumberField()
  auto_approval = TextField()
  is_autoapproved =  TextField()

  class Meta:
    ignore_none_field = False
    collection_name = DATABASE_PREFIX+"Mtest_" +"document"

  @classmethod
  def find_by_uid(cls, uuid):
    """Find the document  using  uid
    Args:
        uuid (string):  UID
    Returns:
        Document: Document Object
    """
    return Document.collection.filter("uid", "==", uuid).get()

