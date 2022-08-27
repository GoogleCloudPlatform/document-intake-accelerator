""" Upload file to gcs bucket function """

from common.config import BUCKET_NAME
from google.cloud.storage import Blob
from google.cloud import storage
from common.config import STATUS_IN_PROGRESS, STATUS_SUCCESS, STATUS_ERROR


def upload_file(case_id, uid, file):
  client = storage.Client()
  bucket = client.get_bucket(BUCKET_NAME)
  blob_name = f"{case_id}/{uid}/{file.filename}"
  blob = Blob(blob_name, bucket)
  blob.upload_from_file(file.file)
  return STATUS_SUCCESS


def upload_json_file(case_id, uid, input_data):
  destination_blob_name = f"{case_id}/{uid}/input_data_{case_id}_{uid}.json"
  storage_client = storage.Client()
  bucket = storage_client.bucket(BUCKET_NAME)
  blob = bucket.blob(destination_blob_name)
  blob.upload_from_string(input_data)
  print(case_id + uid + input_data)
  return STATUS_SUCCESS
