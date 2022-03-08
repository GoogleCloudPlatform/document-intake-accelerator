""" hitl endpoints """
from fastapi import APIRouter
# disabling for linting to pass
# pylint: disable = broad-except

router = APIRouter()
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}


@router.get('/report_data')
async def report_data():
  """ reports all data to user
            the database
          Returns:
              200 : fetches all the data from database
    """
  print("iiii")
  data = [
      {
          "case_id": "123",
          "uid": "d018f778-8f29-11ec-9081-f2a4dc7e55e0",
          "status": "pending review",
          "uploaded_time": "2/16/22, 6:40 PM"
      },
      {
          "case_id": "4322",
          "uid": "d018f7uii-8f29-11ec-9081-f2a4dc7e55e0",
          "status": "accepeted",
          "uploaded_time": "2/17/22, 6:40 PM"
      },
      {
          "case_id": "4322",
          "uid": "d018f7uii-8f29-11ec-9081-f2a4dc7e55e0",
          "status": "accepeted",
          "uploaded_time": "2/17/22, 6:40 PM"
      },
  ]
  return {"status": "Success", "data": data}
