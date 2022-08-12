"""
Config module to setup common environment
"""
import os

# URL of Process Task API
API_DOMAIN = os.getenv("API_DOMAIN")
PROCESS_TASK_URL= f"https://{API_DOMAIN}/upload_service/v1/process_task"
