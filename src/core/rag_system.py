"""
RAG system orchestration and Local AI integration.
"""

from typing import List, Optional

from ..utils import logger
from .local_ai_client import ChatMessage, LocalAIClient
from .vector_store import VectorStore


class RAGSystem:
    """Main RAG system that combines retrieval and generation."""

    def __init__(self, vector_store: VectorStore, ai_client: LocalAIClient):
        self.vector_store = vector_store
        self.ai_client = ai_client

        self.system_prompt = """You are a helpful AI assistant with access to a knowledge base.
When answering questions, use the provided context from the knowledge base to give accurate and relevant responses.
If the context doesn't contain enough information to answer the question, say so clearly.
Always ground your responses in the provided context when possible."""

    def retrieve_context(self, query: str, k: int = 5) -> str:
        """Retrieve relevant context for the query."""
        results = self.vector_store.search(query, k)

        if not results:
            return "No relevant context found in the knowledge base."

        context_parts = []
        for i, (doc, score) in enumerate(results, 1):
            # Include source information
            source_info = f"Source: {doc.file_path} (chunk {doc.chunk_index + 1}/{doc.total_chunks})"
            context_parts.append(f"Context {i} ({source_info}):\n{doc.content}")

        return "\n\n" + "\n\n".join(context_parts)

    def generate_response(
        self,
        query: str,
        context: str,
        conversation_history: List[ChatMessage] = None,
        stream: bool = False,
    ) -> Optional[str]:
        """Generate response using retrieved context."""

        # Build the prompt with context
        user_message = f"""Context from knowledge base:
{context}

Question: {query}

Please answer the question using the provided context. If the context doesn't contain enough information, please say so."""

        # Build message history
        messages = [ChatMessage(role="system", content=self.system_prompt)]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current query
        messages.append(ChatMessage(role="user", content=user_message))

        if stream:
            return self.ai_client.chat_completion_stream(messages)
        else:
            return self.ai_client.chat_completion(messages)

    def ask(self, query: str, k: int = 5, stream: bool = False):
        """Ask a question and get a response with context."""
        logger.info(f"Processing query: {query}")

        # Retrieve relevant context
        context = self.retrieve_context(query, k)

        # Generate response
        response = self.generate_response(query, context, stream=stream)

        return response, context

    def chat_completion_stream(
        self, message: str, history: List[ChatMessage] = None, k: int = 5
    ):
        """Stream chat completion with RAG context."""
        logger.info(f"Processing streaming chat: {message}")

        # Retrieve relevant context
        context = self.retrieve_context(message, k)

        # Build the prompt with context
        user_message = f"""Context from knowledge base:
{context}

Question: {message}

Please answer the question using the provided context. If the context doesn't contain enough information, please say so."""

        # Build message history
        messages = [ChatMessage(role="system", content=self.system_prompt)]

        # Add conversation history if provided
        if history:
            messages.extend(history)

        # Add current query
        messages.append(ChatMessage(role="user", content=user_message))

        # Return streaming response
        return self.ai_client.chat_completion_stream(messages)


# Legacy alias for backward compatibility
LMStudioClient = LocalAIClient
