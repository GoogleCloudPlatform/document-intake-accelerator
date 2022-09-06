"""
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
