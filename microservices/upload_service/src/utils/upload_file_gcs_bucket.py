""" Upload file to gcs bucket function """

from common.config import BUCKET_NAME
from google.cloud.storage import Blob
from google.cloud import storage



def upload_file(case_id, uid, file):
  client = storage.Client()
  bucket = client.get_bucket(BUCKET_NAME)
  blob_name = f"{case_id}/{uid}/{file.filename}"
  blob = Blob(blob_name, bucket)
  blob.upload_from_file(file.file)
  return "success"


def upload_json_file(case_id, uid, input_data):
  destination_blob_name = f"{case_id}/{uid}/input_data_{case_id}_{uid}.json"
  storage_client = storage.Client()
  bucket = storage_client.bucket(BUCKET_NAME)
  blob = bucket.blob(destination_blob_name)
  blob.upload_from_string(input_data)
  print(case_id + uid + input_data)
  return "success"
