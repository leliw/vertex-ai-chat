from typing import List, Optional
import pytest

from ampf.auth.auth_model import TokenExp
from ampf.base import BaseEmailSender
from ampf.storage_in_memory import AmpfInMemoryFactory
from app.config import DefaultUserConfig, ServerConfig
from haintech.ai.base.base_ai_text_embedding_model import BaseAITextEmbeddingModel


@pytest.fixture
def factory():
    """Return an instance of the in-memory factory."""
    return AmpfInMemoryFactory()


class TestEmailSender(BaseEmailSender):
    """A test email sender that stores sent emails in memory."""

    def __init__(self):
        self.sent_emails = []

    def send(
        self,
        sender: str,
        recipient: str,
        subject: str,
        body: str,
        attachment_path: Optional[str] = None,
    ) -> None:
        self.sent_emails.append(
            {
                "sender": sender,
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "attachment_path": attachment_path,
            }
        )


@pytest.fixture
def email_sender():
    """Return an instance of the test email sender."""
    return TestEmailSender()


@pytest.fixture
def test_config():
    """Return a test configuration."""
    return ServerConfig(
        default_user=DefaultUserConfig(email="test@test.com", password="test"),
        file_storage_bucket="vertex-ai-chat-dev-unit-tests",
    )


@pytest.fixture
def tokens(factory, client):
    """Login and return tokens."""
    # Clear token_black_list
    factory.create_compact_storage("token_black_list", TokenExp, "token").drop()
    # Login
    response = client.post(
        "/api/login",
        data={"username": "test@test.com", "password": "test"},
    )
    r = response.json()
    yield r
    # Logout
    client.post(
        "/api/logout", headers={"Authorization": f"Bearer {r['refresh_token']}"}
    )


@pytest.fixture
def auth_header(tokens):
    yield {"Authorization": f"Bearer {tokens['access_token']}"}


class MockAITextEmbeddingModel(BaseAITextEmbeddingModel):
    async def get_embedding(self, text: str) -> List[float]:
        return [0.1] * 256

@pytest.fixture
def embedding_model():
    return MockAITextEmbeddingModel()