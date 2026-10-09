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

""" Tests for gcs_validation """

from common.config import BUCKET_NAME
from common.utils.gcs_validation import is_allowed_document_url

VALID = f"gs://{BUCKET_NAME}/case1/uid1/doc.pdf"


def test_valid_url():
  assert is_allowed_document_url(VALID)
  assert is_allowed_document_url(VALID, "case1", "uid1")


def test_other_bucket_rejected():
  assert not is_allowed_document_url("gs://other-bucket/case1/uid1/doc.pdf")
  assert not is_allowed_document_url(
      f"gs://{BUCKET_NAME}-evil/case1/uid1/doc.pdf")


def test_non_gcs_rejected():
  assert not is_allowed_document_url("http://169.254.169.254/x/y/z")
  assert not is_allowed_document_url("")


def test_mismatch_and_traversal_rejected():
  assert not is_allowed_document_url(VALID, "case2", "uid1")
  assert not is_allowed_document_url(VALID, "case1", "uid2")
  assert not is_allowed_document_url(f"gs://{BUCKET_NAME}/case1/doc.pdf")
  assert not is_allowed_document_url(
      f"gs://{BUCKET_NAME}/case1/../uid1/doc.pdf")
