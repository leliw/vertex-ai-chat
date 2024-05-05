from pydantic import BaseModel
from verrtex_ai.vertex_ai_factory import VertexAiFactory
from vertexai.generative_models import Content, Part


class ChatMessage(BaseModel):
    author: str
    content: str


class ChatService:
    """Service for chat."""

    def __init__(self):
        self.factory = VertexAiFactory()

    def get_answer(
        self, history: list[ChatMessage], message: ChatMessage
    ) -> tuple[ChatMessage, list[ChatMessage]]:
        """Get an answer from the model."""
        text, chat_history = self.model_get_answer(history, message.content)
        answer = ChatMessage(author="ai", content=text)
        return (answer, chat_history)

    def model_get_answer(
        self, history: list[ChatMessage], question: str
    ) -> tuple[str, list[ChatMessage]]:
        """Get an answer from the model."""
        in_history = [self._chat_message_to_content(m) for m in history]
        chat = self.factory.get_chat(history=in_history)
        responses = chat.send_message(question, stream=True)
        ret = ""
        for response in responses:
            ret += response.text
        out_history = [self._content_to_chat_message(m) for m in chat.history]
        return (ret, out_history)

    def _chat_message_to_content(self, message: ChatMessage) -> Content:
        """Convert ChatMessage to Content."""
        return Content(
            role=message.author if message.author == "user" else "model",
            parts=[Part.from_text(message.content)],
        )

    def _content_to_chat_message(self, content: Content) -> ChatMessage:
        """Convert Content to ChatMessage."""
        return ChatMessage(
            author=content.role if content.role == "user" else "ai",
            content=content.parts[0].text,
        )
