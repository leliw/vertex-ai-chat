from typing import Iterator, List, Mapping, Optional

from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask


class StreamedException(BaseModel):
    """Data streamed to client when any exception occured"""

    error: str
    args: Optional[List[str]] = None

    @classmethod
    def from_exception(cls, e: Exception):
        args = []
        for a in e.args:
            if isinstance(a, str):
                args.append(a)
            else:
                args.append(str(a))
        return StreamedException(error=type(e).__name__, args=args)


class JsonStreamingResponse[T: BaseModel](StreamingResponse):
    """Streams Pydantic objects to client as JSON.

    Stream contain array of JSON objects (exept "[" and "]").
    Each object is in one line. Each line starts with "," (except first line).
    """

    def __init__(
        self,
        content: Iterator[T],
        status_code: int = 200,
        headers: Mapping[str, str] = None,
        background: BackgroundTask = None,
    ):
        media_type = "text/event-stream"
        super().__init__(
            self.objects_to_text(content), status_code, headers, media_type, background
        )

    def objects_to_text(self, responses: Iterator[T]) -> Iterator[str]:
        """Converts object iterator to JSON string iterator of these objects."""
        try:
            for i, r in enumerate(responses):
                yield self.object_to_text(i, r)
        except Exception as e:
            yield self.object_to_text(i, StreamedException.from_exception(e))

    def object_to_text(self, i: int, o: T) -> str:
        """Converts object to JSON string."""
        return f"{',' if i > 0 else ''}{o.model_dump_json()}\n"
