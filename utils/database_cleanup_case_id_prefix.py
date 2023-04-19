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


def delete_firestore_documents_by_caseid_prefix(collection_id, case_id_prefix, dryrun=False):
  docs = db.collection(collection_id).stream()

  for doc in docs:
    document = Document.from_dict(doc.to_dict())
    case_id = document.case_id
    if case_id is not None and case_id.startswith(case_id_prefix):
      print(f" ---> Document uid={document.uid}, case_id={document.case_id}")
      if not dryrun:
        print(f"      Deleting uid={document.uid}, url={document.url}")
        document.delete_by_id(document.uid)



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

  args_parser.add_argument('-c', dest="case_id_prefix", help="case_id prefix to filter")
  args_parser.add_argument('-dry', dest="case_id_prefix", help="case_id prefix to filter")
  args_parser.add_argument('--dryrun', action='store_true',
                      help='Print the list of documents to be deleted instead of performing delete action '
                           'of running the commands.')
  return args_parser

if __name__ == "__main__":
  parser = get_args()
  args = parser.parse_args()

  if args.case_id_prefix is None:
    raise Exception("case_id_prefix is not defined. Database cleanup skipped.")

  if args.dryrun:
    print(f"Performing dry run on firebase collection using case_id prefix=[{args.case_id_prefix}]")
  else:
    print(f"Deleting documents from firebase collection using case_id prefix=[{args.case_id_prefix}]")
  delete_firestore_documents_by_caseid_prefix(f"document", args.case_id_prefix, dryrun=args.dryrun)
