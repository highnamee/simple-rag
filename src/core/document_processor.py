"""
Document processing and management.
"""

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from ..utils import FileUtils, TextProcessor, logger


@dataclass
class Document:
    """Represents a document with metadata."""

    file_path: str
    content: str
    chunk_id: str
    file_hash: str
    chunk_index: int
    total_chunks: int
    created_at: str
    file_size: int
    file_type: str


class DocumentProcessor:
    """Handles document loading and chunking."""

    SUPPORTED_EXTENSIONS = {
        ".txt",
        ".md",
        ".py",
        ".js",
        ".json",
        ".csv",
        ".html",
        ".xml",
    }

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.text_processor = TextProcessor(chunk_size, chunk_overlap)
        self.file_utils = FileUtils()

    def process_file(self, file_path: str) -> List[Document]:
        """Process a single file into Document objects."""
        path_obj = Path(file_path)

        # Check if file extension is supported
        if path_obj.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            logger.warning(f"Unsupported file type: {file_path}")
            return []

        # Load file content
        content = self.file_utils.read_text_file(file_path)
        if not content or not content.strip():
            logger.warning(f"Empty or unreadable file: {file_path}")
            return []

        # Clean content
        content = self.text_processor.clean_text(content)

        # Get file metadata
        file_hash = self.file_utils.get_file_hash(file_path)
        file_info = self.file_utils.get_file_info(file_path)

        # Chunk the content
        chunks = self.text_processor.chunk_text(content)
        documents = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{file_hash}_{i}"

            doc = Document(
                file_path=str(file_path),
                content=chunk,
                chunk_id=chunk_id,
                file_hash=file_hash,
                chunk_index=i,
                total_chunks=len(chunks),
                created_at=datetime.now().isoformat(),
                file_size=file_info.get("size", 0),
                file_type=file_info.get("extension", ""),
            )
            documents.append(doc)

        logger.info(f"Processed {file_path}: {len(chunks)} chunks created")
        return documents

    def scan_directory(self, directory: str) -> List[str]:
        """Recursively scan directory for supported files."""
        if not Path(directory).exists():
            logger.error(f"Directory not found: {directory}")
            return []

        files = self.file_utils.scan_directory(
            directory, list(self.SUPPORTED_EXTENSIONS)
        )
        logger.info(f"Found {len(files)} supported files in {directory}")
        return files
