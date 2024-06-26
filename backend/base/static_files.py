"""This module provides a function to return static files or index.html from a base directory."""

import os
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import HTMLResponse


def static_file_response(base_dir: str, uri_path: str) -> HTMLResponse:
    """Return a static files (if exists) or index.html (if exists) from the base_dir"""
    file_path = Path(base_dir) / uri_path
    if file_path.exists() and file_path.is_file():
        return HTMLResponse(
            content=get_file_content(file_path),
            status_code=200,
            headers=get_file_headers(file_path),
        )
    index_path = Path(base_dir) / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Page not found")
    return HTMLResponse(content=index_path.read_text(), status_code=200)


def get_file_content(file_path: Path):
    """Return the file content"""
    file_extension = os.path.splitext(file_path)[1]
    if file_extension in [
        ".js",
        ".css",
        ".html",
        ".json",
        ".yaml",
        ".yml",
        ".xml",
        ".csv",
        ".txt",
    ]:
        return file_path.read_text()
    else:
        return file_path.read_bytes()


def get_file_headers(file_path: Path) -> dict[str, str]:
    """Return the file headers (Content-Type) based on the file extension"""
    file_extension = os.path.splitext(file_path)[1]
    match file_extension:
        case ".js":
            media_type = "text/javascript"
        case ".css":
            media_type = "text/css"
        case ".ico":
            media_type = "image/x-icon"
        case ".png":
            media_type = "image/png"
        case ".jpg":
            media_type = "image/jpeg"
        case ".jpeg":
            media_type = "image/jpeg"
        case ".svg":
            media_type = "image/svg+xml"
        case _:
            media_type = "text/html"
    return {"Content-Type": media_type}
