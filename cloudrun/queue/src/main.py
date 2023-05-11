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
  Sample Service Microservice
"""
import uvicorn
from fastapi import FastAPI
from fastapi import status

import config
from routes import queue

# app = FastAPI(docs_url="/docs", redoc_url="/redoc", openapi_url="/openapi.json")
app = FastAPI(title="Queue Task Dispatcher")


@app.get("/ping")
def health_check():
  return True


@app.post("/")
def health_check_post():
  return True


@app.get("/hello")
def hello():
  return "Hello World."


@app.get("/", tags=["Index"], status_code=status.HTTP_200_OK)
async def index():
  return {"message": "GET request received!"}


app.include_router(queue.router)

if __name__ == "__main__":
  uvicorn.run(
      "main:app",
      host="0.0.0.0",
      port=int(config.PORT),
      log_level="info",
      reload=True)
