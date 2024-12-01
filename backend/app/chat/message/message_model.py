from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field

from google.generativeai.types.content_types import ContentDict
from google.generativeai.types.file_types import FileDataDict


class ChatMessageFile(BaseModel):
    """File in chat message."""

    name: str
    mime_type: str


class ChatMessage(BaseModel):
    """One chat message."""

    author: Literal["user", "ai"]
    content: str
    files: Optional[list[ChatMessageFile]] = Field([])

    def to_content(self) -> ContentDict:
        """Convert ChatMessage to ContentDict."""
        parts = [self.content]
        for file in self.files:
            parts.append(
                FileDataDict(
                    uri=file.url,
                    mime_type=file.mime_type,
                )
            )
        return ContentDict(
            role=self.author if self.author == "user" else "model",
            parts=parts,
        )

    @classmethod
    def from_content(
        cls, content: ContentDict, file_names: dict[str, str]
    ) -> ChatMessage:
        """Convert ContentDict to ChatMessage."""
        files = []
        for part in content.parts:
            if part.file_data.file_uri:
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
