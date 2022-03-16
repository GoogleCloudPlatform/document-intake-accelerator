""" Upload file to gcs bucket function """

from common.config import BUCKET_NAME
from google.cloud import storage


def upload_file(case_id, uid, file):
  print(case_id + uid + file)
  print(BUCKET_NAME)
  return "success"


def upload_file_json(case_id, uid, file):
  print(case_id + uid + file)
  return "success"


def upload_json_file(case_id, uid, input_data):
  destination_blob_name = f"{case_id}/{uid}/input_data_{case_id}_{uid}.json"
  storage_client = storage.Client()
  bucket = storage_client.bucket(BUCKET_NAME)
  blob = bucket.blob(destination_blob_name)
  blob.upload_from_string(input_data)
  print(case_id + uid + input_data)
  return "success"
