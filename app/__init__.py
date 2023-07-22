import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from . import utils

if int(os.getenv("LOAD_ENV_FROM_FILE", 1)):
    load_dotenv(".env.dev")
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
        "http://localhost:3000",
        "https://keylance-backend-svc-dev.up.railway.app",
        "https://keylance-dc9c3k23s-harshitsaini.vercel.app"
        "https://www.keylance.io",
        "https://keylance.io",
        "https://keylance.vercel.app",
        ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
