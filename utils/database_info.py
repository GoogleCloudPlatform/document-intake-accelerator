import os
import firebase_admin
from firebase_admin import credentials, firestore

PROJECT_ID = os.getenv("PROJECT_ID", None)
DATABASE_PREFIX = os.getenv("DATABASE_PREFIX", "")

# Initializing Firebase client.
firebase_admin.initialize_app(credentials.ApplicationDefault(), {
    "projectId": PROJECT_ID,
})
db = firestore.client()

def delete_firestore_collection(collection_id):
  delete_collection(db.collection(collection_id), 150)


def delete_collection(coll_ref, batch_size):
  docs = coll_ref.limit(batch_size).stream()
  deleted = 0

  for doc in docs:
    doc.reference.delete()
    deleted = deleted + 1

  if deleted >= batch_size:
    print(f"Processed batch of {batch_size}")
    return delete_collection(coll_ref, batch_size)


def get_count():
  ct = 0
  docs = db.collection(u"document").stream()
  for doc in docs:
    a = doc.to_dict()
    url = a["url"]
    print(f"----- {url}")
    #print("loop")
    b = a["system_status"]
    ct = ct + 1

  return ct

if __name__ == "__main__":
  count = get_count()
  print(f"==> Total count = {count}")
