""" hitl endpoints """
from fastapi import APIRouter
# disabling for linting to pass
# pylint: disable = broad-except

router = APIRouter()
SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}


@router.get("/report_data")
async def report_data():
  """ reports all data to user
            the database
          Returns:
              200 : fetches all the data from database
    """

  data = [
      {
          "case_id": "123",
          "uid": "d018f778-8f29-11ec-9081-f2a4dc7e55e0",
          "url": "http://http://storage.googleapis.com/document-upload-test/"
                 "123/d018f778-8f29-11ec-9081-f2a4dc7e55e0/arkans.pdf",
          "entities": [{
              "entity": "name",
              "raw-value": "Jon",
              "corrected_value": "Jonathan",
              "extraction": 0.9,
              "matching": 0.1
          }, {
              "entity": "last-name",
              "raw-value": "Doe",
              "corrected_value": "Doon",
              "extraction": 0.9,
              "matching": 0.5
          }],
          "document_type": "application",
          "document_class": "unemployment",
          "context": "Arizona",
          "system_status": [{
              "stage": "uploaded",
              "status": "success",
              "timestamp": "2022-03-02 05:38:44.748676"
          }, {
              "stage": "classification",
              "status": "success",
              "timestamp": "2022-03-09 05:38:44.748676"
          }, {
              "stage": "extraction",
              "status": "success",
              "timestamp": "2022-04-09 05:38:44.748676"
          }],
          "uploaded_time": "2022-03-09 05:38:44.748676",
          "active": "active",
          "validation_score": 0.9,
          "matching_score": 0.7,
          "extraction_score": 0.8,
          "hitl_status": [{
              "stage": "pending",
              "timestamp": "2022-03-02 05:38:44.748676",
              "user": "Max",
              "comment": "Its pending review"
          }, {
              "stage": "reject",
              "timestamp": "2022-03-01 05:38:44.748676",
              "user": "William",
              "comment": " The document is rejected"
          }, {
              "stage": "approved",
              "timestamp": "2022-04-01 06:38:44.748676",
              "user": "William",
              "comment": " The document is accepted"
          }],
          "auto_approval": "yes"
      },
      {
          "case_id": "346",
          "uid": "d018f778-11ec-9081-f2a4dc7e55e0",
          "url": "http://http://storage.googleapis.com/document-upload-test"
                 "/346/d018f778-11ec-9081-f2a4dc7e55e0/arizona.pdf",
          "entities": [{
              "entity": "name",
              "raw-value": "Jon",
              "corrected_value": "Jonathan",
              "extraction": 0.9,
              "matching": 0.1
          }, {
              "entity": "last-name",
              "raw-value": "Doe",
              "corrected_value": "Doon",
              "extraction": 0.9,
              "matching": 0.5
          }],
          "document_type": "supporting_document",
          "document_class": "driving_licence",
          "context": "Arizona",
          "system_status": [{
              "stage": "uploaded",
              "status": "success",
              "timestamp": "2022-03-02 05:38:44.748676"
          }, {
              "stage": "classification",
              "status": "success",
              "timestamp": "2022-03-09 05:38:44.748676"
          }, {
              "stage": "extraction",
              "status": "success",
              "timestamp": "2022-04-09 05:38:44.748676"
          }],
          "uploaded_time": "2022-03-09 05:38:44.748676",
          "active": "active",
          "validation_score": 0.9,
          "matching_score": 0.7,
          "extraction_score": 0.8,
          "hitl_status": [{
              "stage": "pending",
              "timestamp": "2022-03-02 05:38:44.748676",
              "user": "Max",
              "comment": "Its pending review"
          }, {
              "stage": "reject",
              "timestamp": "2022-03-01 05:38:44.748676",
              "user": "William",
              "comment": " The document is rejected"
          }, {
              "stage": "approved",
              "timestamp": "2022-04-01 06:38:44.748676",
              "user": "William",
              "comment": " The document is accepted"
          }],
          "auto_approval": "no"
      },
      {
          "case_id": "89989990",
          "uid": "d018f778-11ecf2a4dc7e55e0",
          "url": "http://http://storage.googleapis.com/document-upload-test"
                 "/89989990/d018f778-11ecf2a4dc7e55e0/california.pdf",
          "entities": [{
              "entity": "name",
              "raw-value": "James",
              "corrected_value": "Jamee",
              "extraction": 0.9,
              "matching": 0.1
          }, {
              "entity": "last-name",
              "raw-value": "Doe",
              "corrected_value": "Doon",
              "extraction": 0.9,
              "matching": 0.5
          }],
          "document_type": "supporting_document",
          "document_class": "driving_licence",
          "context": "Arizona",
          "system_status": [{
              "stage": "uploaded",
              "status": "success",
              "timestamp": "2022-03-02 05:38:44.748676"
          }, {
              "stage": "classification",
              "status": "success",
              "timestamp": "2022-03-09 05:38:44.748676"
          }, {
              "stage": "extraction",
              "status": "success",
              "timestamp": "2022-04-09 05:38:44.748676"
          }],
          "uploaded_time": "2022-03-09 05:38:44.748676",
          "active": "active",
          "validation_score": 0.9,
          "matching_score": 0.7,
          "extraction_score": 0.8,
          "hitl_status": [{
              "stage": "pending",
              "timestamp": "2022-03-02 05:38:44.748676",
              "user": "Max",
              "comment": "Its pending review"
          }, {
              "stage": "pending",
              "timestamp": "2022-03-01 05:38:44.748676",
              "user": "William",
              "comment": " The document is pending"
          }, {
              "stage": "approved",
              "timestamp": "2022-04-01 06:38:44.748676",
              "user": "William",
              "comment": " The document is accepted"
          }],
          "auto_approval": "no"
      },
  ]
  return {"status": "Success", "data": data}
