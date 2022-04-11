""" Arguments Classess """
# pylint:disable=E0401,R0903,E0611
import json
from pydantic import BaseModel
from typing import Optional


class SearchPayload(BaseModel):
  """ Argument class for Search
  """
  term: Optional[object] = None
  filter_key: Optional[str] = None
  filter_value: Optional[object] = None
  limit_start: Optional[int] = None
  limit_end: Optional[int] = None

  def toJSON(self):
    return json.dumps(
        self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
