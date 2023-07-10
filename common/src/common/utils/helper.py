import re
import os
from google.cloud import storage

storage_client = storage.Client()


def split_uri_2_bucket_prefix(uri: str):
  match = re.match(r"gs://([^/]+)/(.+)", uri)
  if not match:
    # just bucket no prefix
    match = re.match(r"gs://([^/]+)", uri)
    return match.group(1), ""
  bucket = match.group(1)
  prefix = match.group(2)
  return bucket, prefix


def get_id_from_file_path(uri: str):
  match = re.match(r"gs://([^/]+)/([^/]+)/([^/]+)/(.+)", uri)
  if len(match.groups()) < 4:
    return None, None

  bucket = match.group(1)
  case_id = match.group(2)
  uid = match.group(3)
  return case_id, uid


def split_uri_2_path_filename(uri: str):
  dirs = os.path.dirname(uri)
  file_name = os.path.basename(uri)
  return dirs, file_name


def get_processor_location(processor_path):
  m = re.match(r'projects/(.+)/locations/(.+)/processors', processor_path)
  if m and len(m.groups()) >= 2:
    return m.group(2)

  return None




