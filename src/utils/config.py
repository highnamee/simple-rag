"""
Configuration management utilities.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv


class Config:
    """Configuration manager for the RAG system."""

    def __init__(self, env_file: str = ".env"):
        """Initialize config by loading environment variables."""
        load_dotenv(env_file)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        return {
            # AI Provider settings
            'ai_provider': os.getenv('AI_PROVIDER', 'lmstudio').lower(),
            'ai_api_url': os.getenv('AI_API_URL', self._get_default_url()),
            'ai_api_key': os.getenv('AI_API_KEY'),
            'ai_model': os.getenv('AI_MODEL'),

            # Legacy LMStudio settings (for backward compatibility)
            'lmstudio_url': os.getenv('LMSTUDIO_API_URL', 'http://localhost:1234/v1'),
            'lmstudio_key': os.getenv('LMSTUDIO_API_KEY', 'lm-studio'),

            # Data and storage
            'data_folder': os.getenv('DATA_FOLDER', './data'),
            'vector_db_path': os.getenv('VECTOR_DB_PATH', './vector_db'),
            'chunk_size': int(os.getenv('CHUNK_SIZE', '512')),
            'chunk_overlap': int(os.getenv('CHUNK_OVERLAP', '50')),
            'embedding_model': os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        }

    def _get_default_url(self) -> str:
        """Get default API URL based on provider."""
        provider = os.getenv('AI_PROVIDER', 'lmstudio').lower()
        if provider == 'ollama':
            return 'http://localhost:11434'
        elif provider == 'lmstudio':
            return 'http://localhost:1234/v1'
        else:
            return 'http://localhost:8000/v1'

    def get(self, key: str, default=None):
        """Get configuration value by key."""
        return self._config.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()

    def update(self, key: str, value: Any):
        """Update configuration value."""
        self._config[key] = value


# Global config instance
config = Config()
