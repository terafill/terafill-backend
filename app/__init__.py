import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from fastapi.responses import JSONResponse

ENV = os.getenv("ENV", "LOCAL")

env2config = {
    "DEV": ".env.dev",
    "PROD": ".env.prod",
    "LOCAL": ".env.local",
}

if int(os.getenv("LOAD_ENV_FROM_FILE", 1)):
    load_dotenv(env2config[ENV])

# from fastapi.openapi.docs import get_swagger_ui_html

from .utils.logging import logger

# from . import models, views
# from .database import Base, engine
from .views import (
    user,
    auth,
    icon,
)

from . import utils
from .utils.otel import trace

# from .database import SessionLocal
import app.utils.errors as internal_exceptions


app = FastAPI()


# Base.metadata.create_all(bind=engine)

app.include_router(user.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(icon.router, prefix="/api/v1")


def get_allowed_origins():
    origin_list_str = os.getenv("ALLOWED_ORIGINS")
    if origin_list_str is None:
        raise Exception("No Allowed origins found!")
    origin_list = origin_list_str.split(",")
    return origin_list


# Add the CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# FastAPIInstrumentor.instrument_app(app, tracer_provider=trace.get_tracer_provider())
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)


@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    # tracer = trace.get_tracer(__name__)

    # with tracer.start_as_current_span("middleware_span"):
    start_time = time.time()

    try:
        # request.state.db = SessionLocal()
        response = await call_next(request)
        # request.state.db.close()
    except Exception as e:
        logger.exception(f"An unexpected exception occurred: {e}", exc_info=True)

        # Create an HTTP 500 response
        response = JSONResponse(
            content={"message": "Internal Server Error"}, status_code=500
        )
        # request.state.db.close()

    end_time = time.time() - start_time
    response.headers["Server-Timing"] = f"total;dur={str(end_time * 1000)}"

    return response
