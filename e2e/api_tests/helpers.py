from common.models.document import Document
from typing import List,Dict


def is_processing_success(data:List[Dict]):
  """Checks if the document is processed and went through all the
     stages successfully

  Args:
      data (List[Dict]): List of uploaded documents

  Returns:
      Bool: Returns a boolean value if document processing is successful or not
  """
  d = Document()
  is_processed = False
  for doc in data:
    uid = doc.get("uid")
    details=d.find_by_uid(uid)
    status = details.system_status
    print("System status is: ",status)
    stages = ["uploaded","classification","extraction","auto_approval","validation","matching"]
    if status is not None:
      for stat in status:
        is_processed = stat.get("stage") in stages and stat.get("status") == "success"
  return is_processed