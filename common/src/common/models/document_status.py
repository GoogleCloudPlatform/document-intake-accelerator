"""
Document Status object in the ORM
"""
import os
from common.models import BaseModel
from fireo.fields import TextField, DateTime ,ListField

DATABASE_PREFIX = os.getenv("DATABASE_PREFIX", "")
PROJECT_ID = os.environ.get("PROJECT_ID", "")


# sample class
class Documentstatus(BaseModel):
  """Documentstatus ORM class
  """
  case_id = TextField()
  uid = TextField()
  url = TextField()
  state = TextField()
  type_of_doc = TextField()
  class_of_doc = TextField()
  system_status = ListField()
  status_timestamp = ListField()
  upload_time = DateTime()
  active = TextField()
  hitl_status = TextField()
  hitl_update_time =  ListField()

  class Meta:
    ignore_none_field = False
    collection_name = DATABASE_PREFIX+ "document_status"
