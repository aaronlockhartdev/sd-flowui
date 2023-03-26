from os import environ as env

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import api

app = FastAPI()

app.include_router(api.router, prefix="/v1")

app.mount("/", StaticFiles(directory=env["STATIC_DIR"], html=True))
