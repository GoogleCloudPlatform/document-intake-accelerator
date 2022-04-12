""" Arguments Classess """
# pylint:disable=E0401,R0903,E0611
from pydantic import BaseModel
from typing import List, Dict

class ProcessTask(BaseModel):

  """ Argument class for split-upload API
  """
  applications:List[Dict]
  supporting_docs:List[Dict]
