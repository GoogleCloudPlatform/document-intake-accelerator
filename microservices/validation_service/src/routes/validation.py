""" Validation endpoints """

from fastapi import APIRouter
# disabling for linting to pass
# pylint: disable = broad-except

router = APIRouter(prefix="/validation")
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}


@router.post('/validation_api')
async def validation(case_id: str, uid: str, doc_class: str):
  """ validates the document with case id , uid ,
        Args:
            case_id (str): Case id of the file ,
             uid (str): unique id for  each document
             doc_class (str): class of document
        Returns:
            200 : validation score successfully  updated
            500  : HTTPException: 500 Internal Server Error if something fails
      """
  print(doc_class)
  return {
      "status": f"validation score for case_id {case_id}, uid {uid} updated "
  }
