""" Arguments Classess """
# pylint:disable=E0401,R0903,E0611
from pydantic import BaseModel

class Reassign(BaseModel):

  """ Argument class for split-upload API
  """
  old_case_id: str
  uid: str
  new_case_id: str
