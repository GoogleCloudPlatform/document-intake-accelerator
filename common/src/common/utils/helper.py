import re
import os

def split_uri_2_bucket_prefix(uri: str):
  match = re.match(r"gs://([^/]+)/(.+)", uri)
  if not match:
    return "", ""
  bucket = match.group(1)
  prefix = match.group(2)
  return bucket, prefix


def split_uri_2_path_filename(uri: str):
  dirs = os.path.dirname(uri)
  file_name = os.path.basename(uri)
  return dirs, file_name
