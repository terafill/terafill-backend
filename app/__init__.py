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

# from . import models, views
from .database import Base, engine
from .views import (
    vault,
    # item,
    user,
    # master_password
    auth,
    icon,
)

from . import utils
from .utils.otel import trace
import app.utils.errors as internal_exceptions


app = FastAPI()


Base.metadata.create_all(bind=engine)

# app.include_router(item.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
app.include_router(vault.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(icon.router, prefix="/api/v1")
# app.include_router(master_password.router, prefix="/api/v1")


# Add the CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://khlffdhmbhlkkmcgmhbhjpjidllcdgmb",
        "https://dev.terafill.com",
        "https://dev.api.terafill.com",
        "https://www.terafill.com",
        "https://terafill.com",
        # "*"
        "http://localhost:3000",
        # "http://localhost:3004",
        # "https://keylance-backend-svc-dev.up.railway.app",
        # "https://keylance-dc9c3k23s-harshitsaini.vercel.app"
        # "https://www.keylance.io",
        # "https://keylance.io",
        "https://keylance-harshitsaini.vercel.app",
        "https://keylance.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


FastAPIInstrumentor.instrument_app(app, tracer_provider=trace.get_tracer_provider())


@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    start_time = time.time()

    try:
        response = await call_next(request)
    except Exception as e:
        # Log the exception for debugging or monitoring purposes
        print(f"An unexpected error occurred: {e}")

        # Create an HTTP 500 response
        response = JSONResponse(
            content={"message": "Internal Server Error"}, status_code=500
        )

    end_time = time.time() - start_time
    response.headers["Server-Timing"] = f"total;dur={str(end_time * 1000)}"

    return response
