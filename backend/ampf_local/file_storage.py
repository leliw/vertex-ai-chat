from abc import ABC
import os
from pathlib import Path

type StrPath = str | Path


class FileStorage(ABC):
    def __init__(
        self,
        root_dir: StrPath,
        subfolder_characters: int = None,
        default_ext: str = None,
    ):
        self.subfolder_characters = subfolder_characters
        self.default_ext = default_ext
        if isinstance(root_dir, Path):
            self._root_dir_path = root_dir
        else:
            self._root_dir_path = Path(root_dir)
        os.makedirs(self._root_dir_path, exist_ok=True)

    def _split_to_folders(self, file_name: str) -> list[str]:
        """Adds extra subfolder if subfolder_characters is set"""
        folders = file_name.split("/")
        if self.subfolder_characters:
            file_name = folders.pop()
            sub_folder = file_name[0 : self.subfolder_characters]
            return [*folders, sub_folder, file_name]
        else:
            return folders

    def _create_file_path(self, file_name: str, ext: str = None) -> Path:
        ext = ext or self.default_ext
        if ext:
            file_name = f"{file_name}.{ext}"
        path = self._root_dir_path.joinpath(*self._split_to_folders(file_name))
        os.makedirs(path.parent, exist_ok=True)
        return path
