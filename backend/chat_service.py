from verrtex_ai.vertex_ai_factory import ChatMessage, VertexAiFactory


class ChatService:
    """Service for chat."""

    def __init__(self):
        self.factory = VertexAiFactory()

    def get_answer(
        self, history: list[ChatMessage], message: ChatMessage
    ) -> tuple[ChatMessage, list[ChatMessage]]:
        """Get an answer from the model."""
        text, history = self.model_get_answer(history, message.content)
        answer = ChatMessage(author="ai", content=text)
        return (answer, history)

    def model_get_answer(
        self, history: list[ChatMessage], question: str
    ) -> tuple[str, list[ChatMessage]]:
        """Get an answer from the model."""
        chat = self.factory.get_chat(history=history)
        responses = chat.send_message(question, stream=True)
        ret = ""
        for response in responses:
            ret += response.text
        print(chat.history)
        return (ret, chat.history)
