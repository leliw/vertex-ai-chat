from pydantic import BaseModel


class ChatMessage(BaseModel):
    author: str
    content: str


class ChatService:
    def __init__(self):
        self.messages: list[ChatMessage] = []

    def add_message(self, message: ChatMessage):
        self.messages.append(message)
    
    def get_messages(self) -> list[ChatMessage]:
        return self.messages

    def get_answer(self, message: ChatMessage) -> ChatMessage:
        self.messages.append(message)
        answer = ChatMessage(author="ai", content=f"Hello, you said: {message.content}")
        self.messages.append(answer)
        return answer
    