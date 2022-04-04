""" Arguments Classess """
# pylint:disable=E0401,R0903,E0611
from pydantic import BaseModel

class ProcessTask(BaseModel):

  """ Argument class for split-upload API
  """
  case_id: str
  uid: str
  gcs_url: str
  is_hitl: bool = False
  document_class: str = ""
  document_type: str=""
