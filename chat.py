#!/usr/bin/env python3
"""
Simple RAG CLI Chat Interface with Streaming Support
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cli import CLIInterface, CommandHandler, ConnectionHandler, IndexingHandler
from src.core import LocalAIClient, RAGIndexer, RAGSystem, VectorStore
from src.utils import config


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Simple RAG Chat CLI with Multi-Provider AI Support"
    )
    parser.add_argument(
        "--reindex", action="store_true", help="Force reindex all documents"
    )
    parser.add_argument(
        "--no-chat", action="store_true", help="Only index documents, don't start chat"
    )
    parser.add_argument(
        "--provider",
        choices=["lmstudio", "ollama", "openai_compatible"],
        help="AI provider to use (overrides config)",
    )
    parser.add_argument("--model", help="Model name to use (overrides config)")

    args = parser.parse_args()

    # Initialize CLI interface
    cli = CLIInterface()
    cli.print_banner()

    # Initialize handlers
    indexing_handler = IndexingHandler(cli)
    connection_handler = ConnectionHandler(cli)

    # Initialize AI client with provider selection
    provider = args.provider or config.get("ai_provider", "lmstudio")
    model = args.model or config.get("ai_model")

    # For backward compatibility, check legacy config if new config not set
    if provider == "lmstudio" and not config.get("ai_api_url"):
        api_url = config.get("lmstudio_url")
        api_key = config.get("lmstudio_key")
    else:
        api_url = config.get("ai_api_url")
        api_key = config.get("ai_api_key")

    ai_client = LocalAIClient(
        provider=provider, api_url=api_url, api_key=api_key, model=model
    )

    cli.console.print(f"[blue]🤖 Using AI Provider: {provider.upper()}[/blue]")
    if model:
        cli.console.print(f"[blue]📱 Model: {model}[/blue]")

    # Check AI provider connection (only if we're going to chat)
    if not args.no_chat:
        if not connection_handler.test_ai_connection(ai_client):
            cli.console.print(
                "[yellow]⚠️  Continuing without AI provider - indexing only[/yellow]"
            )
            args.no_chat = True

    # Initialize vector store and indexer
    cli.console.print("[yellow]📚 Initializing document indexing...[/yellow]")

    vector_store = VectorStore(
        model_name=config.get("embedding_model"),
        vector_db_path=config.get("vector_db_path"),
    )

    indexer = RAGIndexer(
        data_folder=config.get("data_folder"),
        vector_store=vector_store,
        chunk_size=config.get("chunk_size"),
        chunk_overlap=config.get("chunk_overlap"),
    )

    # Handle indexing
    indexing_success = indexing_handler.handle_indexing(indexer, args.reindex)

    if args.no_chat or not indexing_success:
        cli.console.print(
            "[green]✅ Indexing complete. Run without --no-chat to start chat.[/green]"
        )
        return

    # Show index statistics
    index_stats = vector_store.get_stats()
    cli.console.print("\n[blue]📊 Index statistics:[/blue]")
    cli.console.print(
        f"[blue]   • Total documents: {index_stats['total_documents']}[/blue]"
    )
    cli.console.print(f"[blue]   • Total files: {index_stats['total_files']}[/blue]")
    cli.console.print(f"[blue]   • Embedding model: {index_stats['model_name']}[/blue]")

    # Initialize RAG system and start chat
    rag_system = RAGSystem(vector_store, ai_client)
    chat_handler = CommandHandler(rag_system, cli)

    cli.console.print(
        f"\n[green]🚀 Starting chat with {provider.upper()} streaming enabled[/green]"
    )
    chat_handler.handle_chat_session()


if __name__ == "__main__":
    main()
