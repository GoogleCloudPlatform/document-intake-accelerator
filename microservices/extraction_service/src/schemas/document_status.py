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
  state: Optional[str] = None
  system_status: Optional[list] = None
  upload_time: Optional[datetime] = None
  status_timestamp: Optional[list] = None
  active: Optional[str] = None
  hitl_status: Optional[str] = None
  hitl_update_time: Optional[list] = None

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "case_id": "123A",
            "uid": "45tt",
            "type_of_doc": "application form",
            "class_of_doc": "unemployment application",
            "state": "callifornia",
            "system_status": ["classified", "uploaded", "extracted"],
            "upload_time": "17 feb 2022",
            "status_timestamp": ["17 feb 2022 ,1 pm", "17 feb 2022, 2pm"],
            "active": "active",
            "hitl_status": "pending_review",
        }
    }
