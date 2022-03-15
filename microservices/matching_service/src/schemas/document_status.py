"""
Pydantic Model for Claim API's
"""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class DocumentstatusModel(BaseModel):
  """Claim Pydantic Model"""
  case_id: str
  uid: str
  url: Optional[str] = None
  type_of_doc: Optional[str] = None
  class_of_doc: Optional[str] = None
  State: Optional[str] = None
  parser_type: Optional[str] = None
  system_status: Optional[str] = None
  upload_time: datetime
  status_update_time: Optional[str] = None
  expiry_of_supporting_doc: Optional[str] = None
  active: Optional[str] = None
  hitl_status: Optional[str] = None

  class Config():
    orm_mode = True
    schema_extra = {"example": {"case_id": "123A", "document": " a file"}}
