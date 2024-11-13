from typing import Optional
import pytest

from ampf.base import BaseEmailSender
from ampf.storage_in_memory import AmpfInMemoryFactory
from app.config import DefaultUserConfig, ServerConfig


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
        default_user=DefaultUserConfig(email="test@test.com", password="test")
    )
