from typing import List
from fastapi import APIRouter, File, UploadFile

from app.dependencies import FileServiceDep

router = APIRouter(tags=["files"])


@router.post("")
def add_files(service: FileServiceDep, files: List[UploadFile] = File(...)):
    for file in files:
        service.upload_file(file)


@router.get("")
def get_all(service: FileServiceDep):
    return service.get_all_files()


@router.delete("/{file_name}", tags=["files"])
def delete_file(service: FileServiceDep, file_name: str):
    service.delete_file(file_name)
