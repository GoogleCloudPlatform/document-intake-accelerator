import re


def split_uri_2_bucket_prefix(uri: str):
  match = re.match(r"gs://([^/]+)/(.+)", uri)
  if not match:
    return "", ""
  bucket = match.group(1)
  prefix = match.group(2)
  return bucket, prefix


def split_uri_2_path_filename(uri: str):
  match = re.match(r"([^/]+)/(.+)", uri)
  if not match:
    return "", ""
  dirs = match.group(1)
  file_name = match.group(2)
  return dirs, file_name
