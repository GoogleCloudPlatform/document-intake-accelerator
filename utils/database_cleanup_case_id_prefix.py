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


"""
  Deletes datasets from firestore and bigquery when the github actions
  complete running tests
"""
import os, sys
import argparse
import firebase_admin
from firebase_admin import credentials, firestore
sys.path.append(os.path.join(os.path.dirname(__file__), '../common/src'))
from common.models import Document

PROJECT_ID = os.getenv("PROJECT_ID", None)

# Initializing Firebase client.
firebase_admin.initialize_app(credentials.ApplicationDefault(), {
    "projectId": PROJECT_ID,
})
db = firestore.client()


def delete_document(document, dryrun):
  print(f" ---> Document uid={document.uid}, case_id={document.case_id}")
  if not dryrun:
    print(f"      Deleting uid={document.uid}, url={document.url}")
    document.delete_by_id(document.uid)


def delete_firestore_documents_by_caseid_prefix(collection_id, case_id_prefix_include, case_id_prefix_exclude, dryrun=False):
  docs = db.collection(collection_id).stream()

  for doc in docs:
    document = Document.from_dict(doc.to_dict())
    case_id = document.case_id
    if case_id is not None:
      #If include list is empty, and exclude is not empty, remove all except those to be excluded
      to_include = (len(case_id_prefix_include) == 0 and len(case_id_prefix_exclude) != 0) \
                   or case_id.startswith(tuple(case_id_prefix_include))
      to_exclude = case_id.startswith(tuple(case_id_prefix_exclude))
      if to_include and not to_exclude:
        delete_document(document, dryrun)


def get_args():
  # Read command line arguments
  args_parser = argparse.ArgumentParser(
      formatter_class=argparse.RawTextHelpFormatter,
      description="""
      script to Cleanup Firestore.
      """,
      epilog="""
      Examples:

      python delete_firestore_documents_by_caseid_prefix.py -c=batch002_
      """)

  args_parser.add_argument('-i', dest="include", help="case_id prefix of documents you want to cleanup", action="append", default=[])
  args_parser.add_argument('-e', dest="exclude", help="case_id prefix of the document you want to keep after the operations", action="append", default=[])
  args_parser.add_argument('--dryrun', action='store_true',
                      help='Print the list of documents to be deleted instead of performing delete action '
                           'of running the commands.')
  return args_parser


if __name__ == "__main__":
  parser = get_args()
  args = parser.parse_args()

  include = args.include
  exclude = args.exclude
  if len(include) == 0 and len(exclude) == 0:
    raise Exception("case_id_prefix not specified neither for include nor for exclude list. Database cleanup skipped.")

  if args.dryrun:
    print(f"Performing dry run on firebase collection using case_id prefix: to include={include}, to exclude={exclude}")
  else:
    print(f"Deleting documents from firebase collection using case_id prefix: to include={include}, to exclude={exclude}")
  delete_firestore_documents_by_caseid_prefix(f"document",
                                              case_id_prefix_include=include,
                                              case_id_prefix_exclude=exclude,
                                              dryrun=args.dryrun)
