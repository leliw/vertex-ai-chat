from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field

from vertexai.generative_models import Content, Part


class ChatMessageFile(BaseModel):
    name: Optional[str] = Field("")
    url: str
    mime_type: str


class ChatMessage(BaseModel):
    author: Literal["user", "ai"]
    content: str
    files: Optional[list[ChatMessageFile]] = Field([])

    def to_content(self) -> Content:
        """Convert ChatMessage to Content."""
        parts = [Part.from_text(self.content)]
        for file in self.files:
            parts.append(
                Part.from_uri(
                    uri=file.url,
                    mime_type=file.mime_type,
                )
            )
        return Content(
            role=self.author if self.author == "user" else "model",
            parts=parts,
        )

    @classmethod
    def from_content(cls, content: Content, file_names: dict[str, str]) -> ChatMessage:
        """Convert Content to ChatMessage."""
        files = []
        for part in content.parts:
            if part.file_data:
                files.append(
                    ChatMessageFile(
                        name=file_names.get(part.file_data.file_uri, ""),
                        url=part.file_data.file_uri,
                        mime_type=part.file_data.mime_type,
                    )
                )
        return ChatMessage(
            author=content.role if content.role == "user" else "ai",
            content=content.parts[0].text,
            files=files,
        )
