from __future__ import annotations
import logging
from typing import Any, Generator
from google.generativeai import GenerativeModel, ChatSession
from google.generativeai.types import content_types, generation_types


class AIAgent:
    """Standard AI Agent"""

    _logger = logging.getLogger(__name__)

    def __init__(
        self,
        model_name: str,
        system_instruction: str = None,
        generation_config: dict[str, Any] = None,
        safety_settings: dict = None,
    ) -> None:
        self._logger.debug(
            f"Initializing AI Agent with model {model_name}\n{system_instruction}"
        )
        self.model_name = model_name
        self.system_instruction = system_instruction
        self.generation_config = generation_config or {
            "max_output_tokens": 8192,
            "temperature": 0,
        }
        self.safety_settings = (
            safety_settings
            or {
                # f_r_o_m google.generativeai.types import HarmCategory, HarmBlockThreshold
                # HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                # HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                # HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                # HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        )
        self.model = None

    def _initialize_model(self):
        """Initialize the model."""
        return GenerativeModel(
            self.model_name,
            system_instruction=[self.system_instruction]
            if self.system_instruction
            else None,
        )

    def generate_content(
        self, prompt: content_types.ContentsType
    ) -> generation_types.GenerateContentResponse:
        """Send a prompt to the model and get the response."""
        if not self.model:
            self.model = self._initialize_model()
        return self.model.generate_content(
            prompt,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
            stream=False,
        )

    def run(self, prompt: str) -> str:
        """Run the model with the given prompt and return the response."""
        response = self.generate_content([prompt])
        try:
            return response.text
        except ValueError as e:
            self._logger.error(f"Error running AI Agent: {e}")
            self._logger.error(response)
            return ""

    def start_chat(
        self,
        history: list[content_types.StrictContentType] = None,
        enable_automatic_function_calling=False,
    ) -> AIAgentChatSession:
        """Start chat session."""
        return AIAgentChatSession(
            ai_agent=self,
            chat_session=self._initialize_model().start_chat(
                history=history,
                enable_automatic_function_calling=enable_automatic_function_calling,
            ),
        )


class AIAgentChatSession:
    """AI Agent Chat Session"""

    def __init__(self, ai_agent: AIAgent, chat_session: ChatSession):
        self.ai_agent = ai_agent
        self.chat_session = chat_session

    def send_message(self, message: str) -> str:
        """Send a message to the chat session."""
        response = self.chat_session.send_message(message)
        if response.text:
            return response.text

    def send_message_streaming(
        self, message: str
    ) -> Generator[generation_types.GenerateContentResponse]:
        """Send a message to the chat session and stream response."""
        for chunk in self.chat_session.send_message(message, stream=True):
            yield chunk

    def get_history(self) -> list[content_types.StrictContentType]:
        """Returns chat history which can be used to create next sesssion"""
        return self.chat_session.history
