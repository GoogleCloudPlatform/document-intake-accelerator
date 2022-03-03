"""
Schema for  Model for Upload  JSON API's
"""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class InputJson(BaseModel):
  """json input  Pydantic Model"""
  case_id: Optional[str]
  first_name : str
  middle_name : str
  last_name : str
  employer_name : str
  city : str
  state : str
  dob : str

  class Config():
    orm_mode = True
    schema_extra = {
      "example":{
        "case_id": "123A",
        "first_name": "Jon",
        "middle_name" :"Max",
        "last_name":"Doe",
        "employer_name":"Quantiphi",
        "city": "New York" ,
        "state":"Callifornia",
        "dob":"7 Feb 1997"
      }
    }
