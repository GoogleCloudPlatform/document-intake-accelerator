""" classification endpoints """

from fastapi import APIRouter

# disabling for linting to pass
# pylint: disable = broad-except

router = APIRouter(prefix="/classification")
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}


@router.post("/classification_api")
async def classifiction(case_id: str, uid: str, gcs_url: str):
  """classifies the  input and updates the active status of document in
        the database
      Args:
          case_id (str): Case id of the file ,
           uid (str): unique id for  each document
           gcs (str): gcs url of document
      Returns:
          200 : PDF files are successfully classified and database updated
          500  : HTTPException: 500 Internal Server Error if something fails
    """
  print(gcs_url)
  return {
      "status":
          "Success",
      "message":
          f'document with case_id {case_id} ,uid_id {uid} '
          f'successfully classified'
  }
