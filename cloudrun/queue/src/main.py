"""
  Sample Service Microservice
"""
import uvicorn
import asyncio
import time
import config
from common.utils.logging_handler import Logger
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Request, status
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
