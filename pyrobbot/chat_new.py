"""Chat implementation using either OpenAI or Gemini API."""

import os
from typing import Generator, Optional, Union

from pyrobbot import gemini_utils
from .chat_config_new import ChatConfig

class Chat:
    """A chat session that can use either OpenAI or Gemini."""

    def __init__(
        self,
        config: Optional[ChatConfig] = None,
        system_message: Optional[str] = None
    ):
        """Initialize chat session."""
        self.config = config or ChatConfig()
        self.system_message = system_message
        self._initialize_chat()

    def _initialize_chat(self):
        """Initialize the appropriate chat client."""
        if self.config.provider == "gemini":
            api_key = self.config.get_api_key()
            if not api_key:
                api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("No Gemini API key provided")
            
            gemini_utils.initialize_gemini(api_key)
            self.chat = gemini_utils.get_gemini_chat(
                model=self.config.gemini_config.model,
                temperature=self.config.gemini_config.temperature,
                top_p=self.config.gemini_config.top_p,
                top_k=self.config.gemini_config.top_k,
                max_output_tokens=self.config.gemini_config.max_output_tokens
            )
            
            # Set system message if provided
            if self.system_message:
                self.chat.send_message(self.system_message)
        else:
            raise NotImplementedError("Only Gemini provider is currently supported")

    def send_message(
        self,
        message: str,
        stream: bool = False
    ) -> Union[str, Generator[str, None, None]]:
        """Send a message to the chat and get the response."""
        try:
            return gemini_utils.get_chat_response(
                self.chat,
                message,
                stream=stream
            )
        except Exception as e:
            raise Exception(f"Failed to get chat response: {str(e)}")

    def reset(self):
        """Reset the chat session."""
        self._initialize_chat()