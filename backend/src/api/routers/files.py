from fastapi import APIRouter

import api.services as services

router = APIRouter(prefix="/files", tags=["graph"])


@router.get("/data/structure")
def read_data_structure():
    return services.file_watcher.dir_structure
