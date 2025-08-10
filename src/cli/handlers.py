"""
Command handlers for the CLI interface.
"""

from pathlib import Path
from typing import List, Optional

from ..core import ChatMessage, RAGSystem
from ..utils import config, logger
from .interface import CLIInterface


class CommandHandler:
    """Handles CLI commands and user interactions."""

    def __init__(self, rag_system: RAGSystem, cli: CLIInterface):
        self.rag_system = rag_system
        self.cli = cli
        self.conversation_history: List[ChatMessage] = []

    def handle_chat_session(self):
        """Handle interactive chat session with streaming responses."""
        self.cli.console.print("\n[bold]💬 Chat Session Started[/bold]")
        self.cli.console.print("Type 'quit' or 'exit' to leave the chat")
        self.cli.console.print("Type '/help' for available commands\n")

        while True:
            try:
                # Get user input
                user_input = self.cli.console.input(
                    "\n[bold green]You:[/bold green] "
                ).strip()

                if not user_input:
                    continue

                # Handle special commands
                if user_input.lower() in ["quit", "exit"]:
                    self.cli.console.print("\n[yellow]Goodbye! 👋[/yellow]")
                    break

                if user_input == "/help":
                    self._show_help()
                    continue

                if user_input == "/clear":
                    self.conversation_history.clear()
                    self.cli.console.print(
                        "\n[yellow]Conversation history cleared! 🧹[/yellow]"
                    )
                    continue

                if user_input == "/history":
                    self._show_history()
                    continue

                if user_input == "/stats":
                    self._show_stats()
                    continue

                # Process chat message
                self._process_chat_message(user_input)

            except KeyboardInterrupt:
                self.cli.console.print(
                    "\n\n[yellow]Chat interrupted. Goodbye! 👋[/yellow]"
                )
                break
            except Exception as e:
                self.cli.console.print(f"\n[red]Error: {str(e)}[/red]")

    def _process_chat_message(self, user_input: str):
        """Process a single chat message with streaming response."""
        try:
            # Add user message to history
            user_message = ChatMessage(role="user", content=user_input)
            self.conversation_history.append(user_message)

            # Get response stream from RAG system
            response_stream = self.rag_system.chat_completion_stream(
                message=user_input,
                history=self.conversation_history[:-1],  # Exclude current message
            )

            # Display streaming response
            response_content = self.cli.display_streaming_response_simple(
                response_stream
            )

            # Add assistant response to history
            if response_content:
                assistant_message = ChatMessage(
                    role="assistant", content=response_content
                )
                self.conversation_history.append(assistant_message)

        except Exception as e:
            self.cli.console.print(f"\n[red]Error processing message: {str(e)}[/red]")

    def _show_help(self):
        """Show available commands."""
        help_text = """
[bold]Available Commands:[/bold]
• /help     - Show this help message
• /clear    - Clear conversation history
• /history  - Show conversation history
• /stats    - Show vector store statistics
• quit/exit - Leave the chat
        """
        self.cli.console.print(help_text)

    def _show_history(self):
        """Show conversation history."""
        if not self.conversation_history:
            self.cli.console.print("\n[yellow]No conversation history yet.[/yellow]")
            return

        self.cli.console.print("\n[bold]Conversation History:[/bold]")
        for i, msg in enumerate(self.conversation_history, 1):
            role_color = "green" if msg.role == "user" else "blue"
            self.cli.console.print(
                f"\n[{role_color}]{i}. {msg.role.title()}:[/{role_color}] {msg.content[:100]}{'...' if len(msg.content) > 100 else ''}"
            )

    def _show_stats(self):
        """Show vector store statistics."""
        try:
            stats = self.rag_system.vector_store.get_stats()
            self.cli.display_stats(stats)
        except Exception as e:
            self.cli.console.print(f"\n[red]Error getting stats: {str(e)}[/red]")

    def handle_question(self, question: str) -> str:
        """Handle single question with streaming response."""
        try:
            response_stream = self.rag_system.chat_completion_stream(
                message=question, history=[]
            )

            return self.cli.display_streaming_response_simple(response_stream)

        except Exception as e:
            error_msg = f"Error processing question: {str(e)}"
            self.cli.console.print(f"\n[red]{error_msg}[/red]")
            return error_msg


class IndexingHandler:
    """Handles document indexing operations."""

    def __init__(self, cli: CLIInterface):
        self.cli = cli

    def handle_indexing(self, indexer, force_reindex: bool = False) -> bool:
        """Handle document indexing process."""
        data_path = Path(config.get("data_folder"))

        # Check if data folder exists
        if not data_path.exists():
            self.cli.console.print(
                f"\n[yellow]📁 Creating data folder: {data_path}[/yellow]"
            )
            data_path.mkdir(parents=True, exist_ok=True)
            self.cli.console.print(
                "[yellow]Add your documents to the data folder and run indexing again[/yellow]"
            )
            return False

        # Perform indexing
        self.cli.console.print(
            "\n[yellow]🔄 Scanning for new and updated files...[/yellow]"
        )

        if force_reindex:
            total_docs = indexer.force_reindex_all()
            self.cli.console.print(
                f"\n[green]✅ Force reindexing complete: {total_docs} documents processed[/green]"
            )
        else:
            stats = indexer.index_new_and_changed_files()
            self.cli.display_indexing_stats(stats)

        return True


class ConnectionHandler:
    """Handles AI provider connection testing."""

    def __init__(self, cli: CLIInterface):
        self.cli = cli

    def test_ai_connection(self, client) -> bool:
        """Test AI provider connection and display results."""
        provider_name = client.provider.value.title()
        self.cli.console.print(
            f"\n[yellow]🔍 Checking {provider_name} connection...[/yellow]"
        )

        if client.test_connection():
            self.cli.console.print(
                f"[green]✅ {provider_name} API is accessible[/green]"
            )

            # Get available models
            models = client.get_available_models()
            if models:
                self.cli.console.print(
                    f"\n[blue]📱 Available models ({len(models)}):[/blue]"
                )
                for model in models[:5]:  # Show first 5 models
                    self.cli.console.print(f"[blue]   • {model}[/blue]")
                if len(models) > 5:
                    self.cli.console.print(
                        f"[blue]   ... and {len(models) - 5} more[/blue]"
                    )
            else:
                self.cli.console.print("[yellow]⚠️  No models found[/yellow]")
            return True
        else:
            self.cli.console.print(
                f"[red]❌ Cannot connect to {provider_name} API[/red]"
            )
            if client.provider.value == "lmstudio":
                self.cli.console.print(
                    "[red]   Make sure LMStudio is running on http://localhost:1234[/red]"
                )
            elif client.provider.value == "ollama":
                self.cli.console.print(
                    "[red]   Make sure Ollama is running on http://localhost:11434[/red]"
                )
            else:
                self.cli.console.print(
                    f"[red]   Make sure your AI provider is running on {client.api_url}[/red]"
                )
            return False

    # Legacy method for backward compatibility
    def test_lmstudio_connection(self, client) -> bool:
        """Legacy method - use test_ai_connection instead."""
        return self.test_ai_connection(client)
