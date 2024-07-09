import json
import os
from pathlib import Path

from pydantic import BaseModel


class LocalBlobStorage:
    def __init__(self, bucket_name: str, default_ext: str = None):
        self.bucket_name = bucket_name
        self.default_ext = default_ext
        self._root_dir_path = Path(self.bucket_name)
        os.makedirs(self._root_dir_path, exist_ok=True)

    def _split_to_folders(self, file_name: str) -> list[str]:
        folders = file_name.split("/")
        file_name = folders.pop()
        sub_folder = file_name[0:2]
        return [*folders, sub_folder, file_name]

    def _create_file_path(self, file_name: str, ext: str = None) -> Path:
        ext = ext or self.default_ext
        if ext:
            file_name = f"{file_name}.{ext}"
        return self._root_dir_path.joinpath(*self._split_to_folders(file_name))

    def upload_blob(
        self, file_name: str, data: bytes, metadata: dict | BaseModel = None
    ) -> None:
        file_path = self._create_file_path(file_name)
        os.makedirs(file_path.parent, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(data)
        if metadata:
            file_path = self._create_file_path(file_name, ext="json")
            with open(file_path, "wt", encoding="utf8") as f:
                if isinstance(metadata, BaseModel):
                    f.write(metadata.model_dump_json(indent=4))
                else:
                    json.dump(metadata, f, indent=4, ensure_ascii=False)

    def download_blob(self, file_name: str) -> bytes:
        file_path = self._create_file_path(file_name)
        try:
            with open(file_path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def get_metadata(self, file_name: str, clazz: BaseModel = None) -> dict | BaseModel:
        file_path = self._create_file_path(file_name, ext="json")
        try:
            with open(file_path, "rt", encoding="utf8") as f:
                d = json.load(f)
            if clazz:
                return clazz.model_validate(d)
            else:
                return d
        except FileNotFoundError:
            return None