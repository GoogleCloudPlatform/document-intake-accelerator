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
Config module to setup common environment
"""
import os
from common.config import DOCUMENT_STATUS_API_PATH, UPLOAD_API_PATH

PORT = os.environ.get("PORT") or 80

# URL of Process Task API
API_DOMAIN = os.getenv("API_DOMAIN")
PROTOCOL = os.getenv("PROTOCOL", "https")

URL = f"{API_DOMAIN}/{DOCUMENT_STATUS_API_PATH}".replace("//", "/")
DOCUMENT_STATUS_URL = f"{PROTOCOL}://{URL}"


URL = f"{API_DOMAIN}/{UPLOAD_API_PATH}".replace("//", "/")
UPLOAD_URL = f"{PROTOCOL}://{URL}"


