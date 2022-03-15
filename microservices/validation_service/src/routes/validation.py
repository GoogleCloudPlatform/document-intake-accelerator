""" Validation endpoints """

from fastapi import APIRouter, HTTPException
from common.models import Document
from utils.validation import get_values
# disabling for linting to pass
# pylint: disable = broad-except

router = APIRouter(prefix="/validation")
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}


@router.post("/validation_api")
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

    doc = Document.find_by_uid(uid)
    if not doc:
        raise HTTPException(status_code=404, detail="uid not found")
    try:
        validation_score = get_values(doc_class, case_id, uid)
        print(validation_score)
        doc.validation_score = validation_score
        # To DO
        # Call status update api
        # req = "http://document-status-service/document_status_service/v1/update_validation_status"
        doc.update()
        return {
            "status": "success",
            "score": f"{validation_score}"
        }
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail="Failed to update validation score") from e
