"""
Config module to setup common environment
"""
import os
from common.config import PROCESS_TASK_API_PATH

PORT = os.environ.get("PORT") or 80

# URL of Process Task API
API_DOMAIN = os.getenv("API_DOMAIN")
PROCESS_TASK_URL = f"https://{API_DOMAIN}/{PROCESS_TASK_API_PATH}"

assert API_DOMAIN, "API_DOMAIN is not defined."
assert PROCESS_TASK_API_PATH, "PROCESS_TASK_API_PATH is not defined."
