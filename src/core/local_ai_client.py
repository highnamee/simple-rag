"""
Generic Local AI client supporting multiple providers (LMStudio, Ollama, etc.)
"""

import requests
import json
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from ..utils import logger


class AIProvider(Enum):
    """Supported AI providers."""
    LMSTUDIO = "lmstudio"
    OLLAMA = "ollama"
    OPENAI_COMPATIBLE = "openai_compatible"


@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str  # "system", "user", or "assistant"
    content: str


class LocalAIClient:
    """Generic client for local AI providers (LMStudio, Ollama, etc.)."""

    def __init__(self,
                 provider: str = "lmstudio",
                 api_url: str = None,
                 api_key: str = None,
                 model: str = None):
        """
        Initialize the local AI client.

        Args:
            provider: AI provider type ('lmstudio', 'ollama', 'openai_compatible')
            api_url: API endpoint URL
            api_key: API key (optional for local providers)
            model: Default model name
        """
        self.provider = AIProvider(provider.lower())
        self.model = model

        # Set default URLs and keys based on provider
        if self.provider == AIProvider.LMSTUDIO:
            self.api_url = api_url or "http://localhost:1234/v1"
            self.api_key = api_key or "lm-studio"  # LMStudio doesn't really need this
        elif self.provider == AIProvider.OLLAMA:
            self.api_url = api_url or "http://localhost:11434"
            self.api_key = api_key  # Ollama doesn't need API key
        else:  # OpenAI compatible
            self.api_url = api_url or "http://localhost:8000/v1"
            self.api_key = api_key or "local-api-key"

        self.api_url = self.api_url.rstrip('/')

        # Setup session
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

        # Add auth header only if API key is provided
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def test_connection(self) -> bool:
        """Test if the AI provider is available."""
        try:
            if self.provider == AIProvider.OLLAMA:
                # Ollama uses different endpoint structure
                response = self.session.get(f"{self.api_url}/api/tags", timeout=5)
            else:
                # LMStudio and OpenAI-compatible use /models
                response = self.session.get(f"{self.api_url}/models", timeout=5)

            return response.status_code == 200
        except Exception as e:
            logger.error(f"{self.provider.value} connection test failed: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        try:
            if self.provider == AIProvider.OLLAMA:
                response = self.session.get(f"{self.api_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return [model["name"] for model in data.get("models", [])]
            else:
                response = self.session.get(f"{self.api_url}/models")
                if response.status_code == 200:
                    data = response.json()
                    return [model["id"] for model in data.get("data", [])]

            return []
        except Exception as e:
            logger.error(f"Error getting models from {self.provider.value}: {e}")
            return []

    def chat_completion(self,
                       messages: List[ChatMessage],
                       model: Optional[str] = None,
                       temperature: float = 0.7,
                       max_tokens: int = 1000,
                       stream: bool = False) -> Optional[str]:
        """Send chat completion request."""

        # Convert messages to dict format
        message_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]

        if self.provider == AIProvider.OLLAMA:
            return self._ollama_chat_completion(message_dicts, model, temperature, max_tokens, stream)
        else:
            return self._openai_compatible_chat_completion(message_dicts, model, temperature, max_tokens, stream)

    def _ollama_chat_completion(self, messages: List[Dict], model: str, temperature: float, max_tokens: int, stream: bool):
        """Handle Ollama-specific chat completion."""
        payload = {
            "model": model or self.model or "llama2",
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            response = self.session.post(
                f"{self.api_url}/api/chat",
                json=payload,
                timeout=60,
                stream=stream
            )
            response.raise_for_status()

            if stream:
                return response
            else:
                data = response.json()
                return data.get("message", {}).get("content", "")

        except Exception as e:
            logger.error(f"Error in Ollama chat completion: {e}")
            return None

    def _openai_compatible_chat_completion(self, messages: List[Dict], model: str, temperature: float, max_tokens: int, stream: bool):
        """Handle OpenAI-compatible chat completion (LMStudio, etc.)."""
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        # Add model if specified
        if model or self.model:
            payload["model"] = model or self.model

        try:
            response = self.session.post(
                f"{self.api_url}/chat/completions",
                json=payload,
                timeout=60,
                stream=stream
            )
            response.raise_for_status()

            if stream:
                return response
            else:
                data = response.json()
                return data["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Error in {self.provider.value} chat completion: {e}")
            return None

    def chat_completion_stream(self,
                              messages: List[ChatMessage],
                              model: Optional[str] = None,
                              temperature: float = 0.7,
                              max_tokens: int = 1000):
        """Stream chat completion response."""

        response = self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )

        if response is None:
            return

        try:
            if self.provider == AIProvider.OLLAMA:
                # Ollama streams JSON objects, one per line
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if "message" in data and "content" in data["message"]:
                                content = data["message"]["content"]
                                if content:
                                    yield content
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
            else:
                # OpenAI-compatible streaming (LMStudio)
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            line = line[6:]  # Remove 'data: ' prefix
                            if line.strip() == '[DONE]':
                                break
                            try:
                                data = json.loads(line)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")


# Legacy alias for backward compatibility
LMStudioClient = LocalAIClient
