""" Matching endpoints"""
from fastapi import APIRouter
# disabling for linting to pass
# pylint: disable = broad-except

router = APIRouter()
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}


@router.post('/match_document')
async def match_document(case_id: str, uid: str):
  """
        matching the document with case id , uid ,
        Args:
            case_id (str): Case id of the file ,
             uid (str): unique id for  each document
        Returns:
            200 : validation score successfully  updated
            500  : HTTPException: 500 Internal Server Error if something fail
    """
  return {
      "status":
          f"Document matching  Successfull for case_id {case_id} and uid {uid}"
  }
