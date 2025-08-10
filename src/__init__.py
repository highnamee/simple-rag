"""
Simple RAG System - A lightweight Retrieval-Augmented Generation system.

This package provides:
- Document processing and chunking
- Vector storage and similarity search
- Integration with LMStudio for local AI inference
- CLI chat interface
"""

__version__ = "1.0.0"
__author__ = "Simple RAG System"

from .cli import CLIInterface

# Import main components
from .core import (
    ChatMessage,
    Document,
    DocumentProcessor,
    LMStudioClient,
    RAGIndexer,
    RAGSystem,
    VectorStore,
)
from .utils import config, logger
