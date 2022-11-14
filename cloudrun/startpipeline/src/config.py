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
from common.config import DOCUMENT_STATUS_API_PATH

PORT = os.environ.get("PORT") or 80

# URL of Process Task API
API_DOMAIN = os.getenv("API_DOMAIN")
URL = f"{API_DOMAIN}/{DOCUMENT_STATUS_API_PATH}".replace("//", "/")

# FIXME: Use HTTPS instead of HTTP
DOCUMENT_STATUS_URL = f"http://{URL}"
assert API_DOMAIN, "API_DOMAIN is not defined."

