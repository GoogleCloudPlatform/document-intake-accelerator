"""
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

""" Validation of caller-supplied GCS document URLs """

from typing import Optional
from common.config import BUCKET_NAME


def is_allowed_document_url(gcs_url: str,
                            case_id: Optional[str] = None,
                            uid: Optional[str] = None) -> bool:
  """Checks that gcs_url points to a document inside the upload bucket.

  Services read documents with their own service account, so accepting an
  arbitrary gs:// URL would let a caller make the service read (and
  process) objects from any bucket it has access to (confused deputy).
  Only objects laid out as gs://<BUCKET_NAME>/<case_id>/<uid>/<file>
  are allowed.

  Args:
    gcs_url: URL supplied by the caller.
    case_id: if given, the URL must belong to this case id.
    uid: if given, the URL must belong to this document uid.
  Returns:
    True if the URL is allowed, False otherwise.
  """
  if not gcs_url or not BUCKET_NAME:
    return False
  prefix = f"gs://{BUCKET_NAME}/"
  if not gcs_url.startswith(prefix):
    return False
  parts = gcs_url[len(prefix):].split("/")
  if len(parts) < 3 or any(p in ("", ".", "..") for p in parts):
    return False
  if case_id is not None and parts[0] != case_id:
    return False
  if uid is not None and parts[1] != uid:
    return False
  return True
