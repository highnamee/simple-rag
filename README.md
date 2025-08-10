# Simple RAG (Retrieval-Augmented Generation) System

A lightweight RAG system with incremental indexing and streaming CLI chat interface, designed to work with LMStudio for local AI inference.

## Features

- **Real-time Markdown Streaming**: Live formatting of responses with code blocks as they arrive
- **Incremental Indexing**: Only processes new and changed files
- **Multi-format Support**: Supports `.txt`, `.md`, `.py`, `.js`, `.json`, `.csv`, `.html`, `.xml` files
- **Vector Search**: Uses FAISS for efficient similarity search
- **Local AI**: Integrates with LMStudio for private, offline AI inference
- **Rich CLI Interface**: Beautiful command-line chat with live markdown rendering
- **Persistent Storage**: Saves embeddings and metadata between sessions

## Prerequisites

1. **Local AI Provider** (choose one):

   **LMStudio**: Download and install [LMStudio](https://lmstudio.ai/)

   - Load a language model (e.g., Llama, Mistral, etc.)
   - Start the local server (default: http://localhost:1234)

   **Ollama**: Download and install [Ollama](https://ollama.ai/)

   - Pull a model: `ollama pull llama2`
   - Server runs automatically (default: http://localhost:11434)

   **Other OpenAI-compatible APIs**: Any local AI server that supports OpenAI-compatible endpoints

2. **Python 3.8+**: Required for the application

## Installation

1. Clone or download this project
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure settings (optional):
   - Edit `.env` file to customize paths, AI provider, and parameters
   - Choose your AI provider: `AI_PROVIDER=lmstudio` or `AI_PROVIDER=ollama`
   - Default data folder: `./data`
   - Default vector database: `./vector_db`

## Usage

### 1. Add Documents

Place your documents in the `data` folder:

```
data/
├── document1.txt
├── document2.md
├── research/
│   ├── paper1.pdf  # Not supported yet
│   └── notes.txt
└── code/
    └── script.py
```

### 2. Start the Chat Interface

```bash
python chat.py
```

This will:

- Index new/changed documents automatically
- Connect to your configured AI provider (LMStudio, Ollama, etc.)
- Start the interactive chat session

### 3. Chat Commands

In the interactive chat:

- Ask questions naturally: "What is the main topic of document1?"
- `/help` - Show available commands
- `/clear` - Clear conversation history
- `/history` - Show conversation history
- `/stats` - Show index statistics
- `quit`/`exit` - Exit the chat

### 4. Command Line Options

```bash
# Start the streaming chat (auto-detects provider from config)
python chat.py

# Use a specific AI provider
python chat.py --provider ollama
python chat.py --provider lmstudio

# Use a specific model
python chat.py --model llama2
python chat.py --provider ollama --model codellama

# Force reindex all documents
python chat.py --reindex

# Only index documents, don't start chat
python chat.py --no-chat

# Combine options
python chat.py --provider ollama --model llama2 --reindex
```

## Configuration

Edit `.env` file to customize:

```env
# AI Provider Settings (choose one)
AI_PROVIDER=lmstudio           # Options: lmstudio, ollama, openai_compatible
# AI_API_URL=http://localhost:1234/v1    # Auto-detected if not set
# AI_API_KEY=your-api-key                # Optional for local providers
# AI_MODEL=llama2                        # Optional: specific model name

# Data and storage paths
DATA_FOLDER=./data
VECTOR_DB_PATH=./vector_db

# Document processing
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Embedding model
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## How It Works

1. **Document Processing**: Files are split into overlapping chunks for better context
2. **Embedding Generation**: Uses Sentence Transformers to create vector embeddings
3. **Vector Storage**: FAISS index stores embeddings for fast similarity search
4. **Incremental Updates**: Only processes files that have changed since last run
5. **Retrieval**: Finds most relevant document chunks for user queries
6. **Streaming Generation**: Your chosen AI provider (LMStudio, Ollama, etc.) streams responses in real-time with proper formatting

## File Structure

```
simple-rag/
├── chat.py                    # Main CLI application with streaming
├── requirements.txt           # Python dependencies
├── .env                      # Configuration file
├── data/                     # Your documents go here
├── vector_db/                # Vector database storage
└── src/
    ├── core/                 # Core RAG components
    │   ├── document_processor.py  # Document loading and chunking
    │   ├── vector_store.py        # Vector storage and search
    │   └── rag_system.py          # RAG orchestration and LMStudio client
    ├── utils/                # Utility modules
    │   ├── config.py             # Configuration management
    │   ├── logger.py             # Logging utilities
    │   ├── file_utils.py         # File operations
    │   └── text_processor.py     # Text processing utilities
    └── cli/                  # CLI interface
        ├── interface.py          # Rich CLI with streaming display
        └── handlers.py           # Command and interaction handlers
```

## Supported File Types

- Text files: `.txt`, `.md`
- Code files: `.py`, `.js`, `.html`, `.xml`
- Data files: `.json`, `.csv`

## Troubleshooting

### AI Provider Connection Issues

**LMStudio:**

- Ensure LMStudio is running with a model loaded
- Check that the server is accessible at http://localhost:1234
- Verify no firewall is blocking the connection

**Ollama:**

- Ensure Ollama is installed and running
- Check that a model is available: `ollama list`
- Verify the server is accessible at http://localhost:11434

**General:**

- Try switching providers: `python chat.py --provider ollama`
- Check your `.env` configuration
- Test connection manually: `curl http://localhost:1234/v1/models` (LMStudio)

### Indexing Issues

- Check that documents are in supported formats
- Ensure the data folder exists and is readable
- Look for encoding issues with non-UTF-8 files

### Memory Issues

- Reduce `CHUNK_SIZE` for large documents
- Use smaller embedding models if needed
- Process fewer files at once

## Dependencies

- `sentence-transformers`: For generating embeddings
- `faiss-cpu`: For vector similarity search
- `requests`: For LMStudio API communication
- `rich`: For beautiful CLI interface
- `python-dotenv`: For configuration management
- `colorama`: For cross-platform colored output

## License

This project is open source. Feel free to modify and adapt for your needs.

## Future Enhancements

- Support for PDF files
- Web interface
- Multiple embedding model options
- Advanced chunking strategies
- Metadata filtering
- Export/import functionality
