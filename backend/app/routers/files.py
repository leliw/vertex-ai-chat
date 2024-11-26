from typing import Annotated, List
from fastapi import APIRouter, Depends, File, UploadFile

from app.dependencies import ServerConfigDep, FactoryDep, UserEmailDep
from app.file.file_service import FileService

router = APIRouter(tags=["files"])


def get_file_service(
    config: ServerConfigDep, factory: FactoryDep, user_email: UserEmailDep
) -> FileService:
    return FileService(config, factory, user_email)


FileServiceDep = Annotated[FileService, Depends(get_file_service)]


@router.post("")
def add_files(service: FileServiceDep, files: List[UploadFile] = File(...)):
    for file in files:
        service.upload_file(file)


@router.delete("/{file_name}", tags=["files"])
def delete_file(service: FileServiceDep, file_name: str):
    service.delete_file(file_name)
