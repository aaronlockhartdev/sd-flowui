from fastapi import APIRouter

from api.routers import graph

router = APIRouter()

router.include_router(graph.router)