"""Stores data on disk in json files"""

import logging
import os
import json
from pathlib import Path
from typing import Iterator, Type

from pydantic import BaseModel

from ampf_base import BaseStorage
from .file_storage import StrPath

DEF_EXT = "json"


class JsonOneFileStorage[T: BaseModel](BaseStorage[T]):
    def __init__(
        self, clazz: Type[T], key_name: str = None, file_name: StrPath = "data.json"
    ):
        super().__init__(clazz, key_name)
        if isinstance(file_name, Path):
            file_name = (
                file_name
                if file_name.name.endswith(DEF_EXT)
                else Path(f"{str(file_name)}.{DEF_EXT}")
            )
            self.file_name = file_name
        else:
            file_name = (
                file_name if file_name.endswith(DEF_EXT) else f"{file_name}.{DEF_EXT}"
            )
            self.file_name = Path(file_name)
        os.makedirs(self.file_name.parent, exist_ok=True)
        self._log = logging.getLogger(__name__)

    def _load_data(self) -> dict[str, T]:
        try:
            return json.load(open(self.file_name, "r", encoding="utf-8"))
        except FileNotFoundError:
            return {}

    def _save_data(self, data: dict[str, T]) -> None:
        json.dump(
            data,
            open(self.file_name, "w", encoding="utf-8"),
            indent=2,
            ensure_ascii=False,
        )

    def put(self, key: str, value: T) -> None:
        data = self._load_data()
        data[key] = value.model_dump()
        self._save_data(data)

    def get(self, key: str) -> T:
        try:
            data = self._load_data()
            return self.clazz.model_validate(data[key])
        except KeyError:
            return None

    def keys(self) -> Iterator[str]:
        data = self._load_data()
        for k in data.keys():
            yield k

    def delete(self, key: str) -> None:
        data = self._load_data()
        data.pop(key, None)
        self._save_data(data)
