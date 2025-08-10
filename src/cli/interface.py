"""
CLI interface utilities and formatting.
"""

from typing import Any, Dict

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from ..utils import logger


class CLIInterface:
    """Rich CLI interface for the RAG system."""

    def __init__(self):
        self.console = Console()

    def print_banner(self):
        """Print application banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                       Simple RAG Chat                        ║
║           Retrieval-Augmented Generation System              ║
╚══════════════════════════════════════════════════════════════╝
        """
        self.console.print(banner, style="bold blue")

    def print_status(self, message: str, style: str = "yellow"):
        """Print status message."""
        self.console.print(f"\n{message}", style=style)

    def print_success(self, message: str):
        """Print success message."""
        self.console.print(f"✅ {message}", style="green")

    def print_error(self, message: str):
        """Print error message."""
        self.console.print(f"❌ {message}", style="red")

    def print_warning(self, message: str):
        """Print warning message."""
        self.console.print(f"⚠️  {message}", style="yellow")

    def print_info(self, message: str):
        """Print info message."""
        self.console.print(f"ℹ️  {message}", style="blue")

    def get_user_input(self, prompt: str = "You") -> str:
        """Get user input with formatted prompt."""
        return Prompt.ask(f"\n[bold blue]{prompt}[/bold blue]", console=self.console)

    def display_response(self, response: str, title: str = "Response"):
        """Display AI response in a formatted panel."""
        self.console.print("\n[bold green]Assistant[/bold green]:")
        self.console.print(Panel(Markdown(response), title=title, border_style="green"))

    def display_streaming_response(self, response_stream, title: str = "Response"):
        """Display streaming AI response with real-time character-by-character updates."""
        from rich.live import Live
        from rich.text import Text

        self.console.print("\n[bold green]Assistant[/bold green]:")

        full_response = ""

        # Create a live display that updates in real-time
        with Live(
            Panel(Text(""), title=title, border_style="green"),
            console=self.console,
            refresh_per_second=20,
            transient=False,
        ) as live:
            try:
                for chunk in response_stream:
                    if chunk:
                        full_response += chunk
                        # Update the live display immediately with each chunk
                        live.update(
                            Panel(
                                Text(full_response), title=title, border_style="green"
                            )
                        )
            except Exception as e:
                live.stop()
                self.print_error(f"Error during streaming: {e}")
                return

        # Show final formatted version with markdown
        if full_response.strip():
            self.console.print("\n" + "─" * 50)
            self.console.print(
                Panel(
                    Markdown(full_response), title="Final Response", border_style="blue"
                )
            )
        else:
            self.print_error("No response received from streaming")

    def display_streaming_response_simple(self, response_stream):
        """Display streaming response with real-time markdown formatting."""
        self.console.print("\n[bold green]Assistant[/bold green]:")

        full_response = ""
        try:
            # Use Live display for real-time markdown rendering
            with Live(console=self.console, refresh_per_second=10) as live:
                for chunk in response_stream:
                    if chunk:
                        full_response += chunk
                        # Update the live display with formatted markdown
                        try:
                            # Create a panel with the current response formatted as markdown
                            formatted_panel = Panel(
                                Markdown(full_response),
                                title="🤖 AI Response",
                                border_style="green",
                                padding=(0, 1),
                            )
                            live.update(formatted_panel)
                        except Exception:
                            # Fallback to plain text if markdown fails
                            plain_panel = Panel(
                                full_response,
                                title="🤖 AI Response",
                                border_style="green",
                                padding=(0, 1),
                            )
                            live.update(plain_panel)

            # Add some spacing after completion
            self.console.print("")

        except Exception as e:
            self.console.print(f"\n[red]Error during streaming: {e}[/red]")
            return ""

        return full_response

    def display_streaming_response_live(self, response_stream, title: str = "Response"):
        """Display streaming AI response with live character-by-character updates."""
        from rich.live import Live
        from rich.text import Text

        self.console.print("\n[bold green]Assistant[/bold green]:")

        full_response = ""
        response_text = Text()

        with Live(
            Panel(response_text, title=title, border_style="green"),
            console=self.console,
            refresh_per_second=10,
        ) as live:
            try:
                for chunk in response_stream:
                    if chunk:
                        full_response += chunk
                        response_text = Text(full_response)
                        live.update(
                            Panel(response_text, title=title, border_style="green")
                        )
            except Exception as e:
                self.print_error(f"Error during streaming: {e}")
                return

        # Final display with markdown formatting
        if full_response.strip():
            self.console.print(
                Panel(
                    Markdown(full_response),
                    title="Final Response",
                    border_style="green",
                )
            )
        else:
            self.print_error("No response received from streaming")

    def display_help(self):
        """Display help information."""
        help_text = """
Available commands:
• help - Show this help message
• clear - Clear conversation history
• stats - Show index statistics
• models - Show available LM models
• streaming - Toggle streaming mode on/off
• fancy - Toggle fancy streaming display
• quit/exit/bye - Exit the chat

Simply type your question to get an AI response based on your documents.
        """
        self.console.print(Panel(help_text, title="Help", border_style="blue"))

    def display_stats(self, stats: Dict[str, Any]):
        """Display index statistics."""
        stats_text = f"""
Total documents: {stats['total_documents']}
Total files: {stats['total_files']}
Embedding model: {stats['model_name']}
Embedding dimension: {stats['embedding_dimension']}
Index size: {stats['index_size']}
        """
        self.console.print(
            Panel(stats_text, title="Index Statistics", border_style="blue")
        )

    def display_indexing_stats(self, stats: Dict[str, int]):
        """Display indexing completion statistics."""
        self.print_success("Indexing complete:")
        self.console.print(f"   • New files: {stats['new_files']}", style="green")
        self.console.print(
            f"   • Updated files: {stats['updated_files']}", style="green"
        )
        self.console.print(
            f"   • Unchanged files: {stats['unchanged_files']}", style="green"
        )

    def display_models(self, models: list):
        """Display available models."""
        if models:
            self.print_success(f"Available models: {', '.join(models)}")
        else:
            self.print_warning("No models loaded in LMStudio")

    def confirm_action(self, message: str) -> bool:
        """Get user confirmation for an action."""
        response = Prompt.ask(f"{message} (y/n)", choices=["y", "n"], default="n")
        return response.lower() == "y"
