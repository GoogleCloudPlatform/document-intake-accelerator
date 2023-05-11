import os
import sys

from google.cloud import secretmanager

sys.path.append(os.path.join(os.path.dirname(__file__), '../common/src'))
from common.utils.iap import send_iap_request

UPLOAD_API_PATH = "/upload_service/v1"
PROCESS_TASK_API_PATH = f"{UPLOAD_API_PATH}/process_task"
API_DOMAIN = os.getenv("API_DOMAIN")
URL = f"{API_DOMAIN}/{PROCESS_TASK_API_PATH}".replace("//", "/")
PROJECT_ID = os.getenv("PROJECT_ID")
SECRET = os.getenv("IAP_SECRET_NAME", "cda-iap-secret")

print(f"PROJECT_ID={PROJECT_ID}")
PROCESS_TASK_URL = f"https://{URL}"
request_body = {
  "configs": [
    {
      "case_id": "0c686978-d4c2-11ed-a058-728a2958591a",
      "uid": "FEmexRROipau8DoauAOp",
      "gcs_url": f"https://storage.cloud.google.com/{PROJECT_ID}-document-upload/0c686978-d4c2-11ed-a058-728a2958591a/FEmexRROipau8DoauAOp/form.pdf",
      "context": "california"
    }
  ]
}


def send_request():
  response = send_iap_request(PROCESS_TASK_URL, method="POST", json=request_body)
  print(response)


if __name__ == "__main__":
  send_request()

