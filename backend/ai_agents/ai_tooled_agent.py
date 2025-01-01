from typing import Any
import google.generativeai as genai
from google.generativeai.types import content_types

from .ai_agent import AIAgent, AIAgentChatSession


class AITooledAgent(AIAgent):
    """AI Tooled Agent"""

    def __init__(
        self,
        ai_model_name: str,
        system_instruction: str = None,
        generation_config: dict[str, Any] = None,
        safety_settings: dict = None,
        tools: list[content_types.FunctionLibraryType] = None,
    ) -> None:
        self.tools = tools
        self.function_declarations = []
        self.functions = {}
        super().__init__(
            ai_model_name, system_instruction, generation_config, safety_settings
        )

    def _initialize_model(self):
        """Initialize model with tools."""
        return genai.GenerativeModel(
            self.ai_model_name,
            system_instruction=[self.system_instruction]
            if self.system_instruction
            else None,
            tools=self.tools,
        )

    def run(self, prompt: str) -> str:
        """Run the model with the given prompt and return the response."""
        chat = self.start_chat()
        return chat.send_message(prompt)

    def start_chat(
        self,
        history: list[content_types.StrictContentType] = None,
        enable_automatic_function_calling=True,
    ) -> AIAgentChatSession:
        """Start chat session."""
        if not enable_automatic_function_calling:
            raise ValueError(
                "AITooledAgent requires enable_automatic_function_calling=True!"
            )
        return super().start_chat(
            history=history,
            enable_automatic_function_calling=enable_automatic_function_calling,
        )
