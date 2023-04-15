from os import environ as env

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import api

app = FastAPI(docs_url=None, redoc_url=None, lifespan=api.lifespan)

app.mount("/api/v1", api.app)
app.mount("/", StaticFiles(directory=env["STATIC_DIR"], html=True))
