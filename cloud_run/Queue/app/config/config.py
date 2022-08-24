"""
Config module to setup common environment
"""
import os
from common.config import PROCESS_TASK_API_PATH

# URL of Process Task API
API_DOMAIN = os.getenv("API_DOMAIN")
PROCESS_TASK_URL= f"https://{API_DOMAIN}/{PROCESS_TASK_API_PATH}"
