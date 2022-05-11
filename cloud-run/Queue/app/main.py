

# pylint:disable=E0401
from fastapi import FastAPI, status
from fastapi.openapi.utils import get_openapi
from app.routers import queue

app = FastAPI(docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Queue Microservice",
        version="3.0.0",
        description="Queue Microservice OpenAPI schema",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.include_router(
    queue.router
)

@app.get("/", tags=["Index"], status_code=status.HTTP_200_OK)
async def index():
    return {"message": "Message Received!"}
