""" extraction endpoints """

from fastapi import APIRouter

# disabling for linting to pass
# pylint: disable = broad-except

router = APIRouter(prefix="/extraction")
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}


@router.post("/extraction_api")
async def extraction(case_id: str, uid: str, doc_class: str):
  """extracts the document with given case id and uid
        Args:
            case_id (str): Case id of the file ,
             uid (str): unique id for  each document
             doc_class (str): class of document
        Returns:
            200 : PDF files are successfully classified and database updated
            500  : HTTPException: 500 Internal Server Error if something fails
      """

  print(doc_class)
  return {
      "status": "Success",
      "message": f"document with case_id {case_id} ,uid_id {uid} "
                 f"successfully extracted"
  }
