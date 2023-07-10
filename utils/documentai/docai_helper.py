from common.models import Document
from common.utils.helper import split_uri_2_bucket_prefix
from common.utils.copy_gcs_documents import copy_blob
import common.config
import uuid
from common.config import STATUS_SUCCESS
import datetime
import os


def get_upload_file_path(file_path, doc_class=None):
  uid, case_id = create_document(file_path, doc_class)
  if uid is not None:
    bucket_name, prefix = split_uri_2_bucket_prefix(file_path)
    file_location_dest = f"{case_id}/{uid}/{os.path.basename(file_path)}"
    bucket_name_dest = common.config.BUCKET_NAME
    copy_blob(bucket_name, prefix, file_location_dest,
              dest_bucket_name=bucket_name_dest)
    return uid, f"gs://{bucket_name_dest}/{file_location_dest}"
  return None


def create_document(uri, doc_class=None):
  document = Document()
  case_id = str(uuid.uuid1())
  document.case_id = case_id
  document.upload_timestamp = datetime.datetime.utcnow()

  document.uid = document.save().id
  document.active = "active"
  document.document_class = doc_class
  document.url = uri
  document.system_status = [{
      "stage": "upload",
      "status": STATUS_SUCCESS,
      "timestamp": datetime.datetime.utcnow()
  }]
  document.save()
  return document.uid, document.case_id