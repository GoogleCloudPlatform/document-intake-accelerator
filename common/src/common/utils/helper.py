import re
import os
from google.cloud import storage


def split_uri_2_bucket_prefix(uri: str):
  match = re.match(r"gs://([^/]+)/(.+)", uri)
  if not match:
    # just bucket no prefix
    match = re.match(r"gs://([^/]+)", uri)
    return match.group(1), ""
  bucket = match.group(1)
  prefix = match.group(2)
  return bucket, prefix


def split_uri_2_path_filename(uri: str):
  dirs = os.path.dirname(uri)
  file_name = os.path.basename(uri)
  return dirs, file_name


def get_processor_location(processor_path):
  m = re.match(r'projects/(.+)/locations/(.+)/processors', processor_path)
  if m and len(m.groups()) >= 2:
    return m.group(2)

  return None


storage_client = storage.Client()


def upload_to_gcs(local_file, file_uri, bucket_name):
  bucket = storage_client.bucket(bucket_name)
  if os.path.isfile(local_file):
    blob = bucket.blob(file_uri)
    print(f"Uploading {local_file} to gs://{bucket_name}/{blob.name} ...")
    blob.upload_from_filename(local_file)
