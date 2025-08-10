"""
File and path utilities.
"""

import os
import hashlib
from pathlib import Path
from typing import List, Optional


class FileUtils:
    """Utility functions for file operations."""

    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """Calculate SHA-256 hash of file content."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    @staticmethod
    def ensure_directory(directory: str) -> Path:
        """Ensure directory exists, create if it doesn't."""
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def scan_directory(directory: str, extensions: List[str]) -> List[str]:
        """Recursively scan directory for files with specified extensions."""
        files = []
        ext_set = set(ext.lower() for ext in extensions)

        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                if Path(file_path).suffix.lower() in ext_set:
                    files.append(file_path)
        return files

    @staticmethod
    def read_text_file(file_path: str) -> Optional[str]:
        """Read text file with encoding fallback."""
        encodings = ['utf-8', 'latin-1', 'cp1252']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        # Last resort: read as binary and decode with errors='ignore'
        try:
            with open(file_path, 'rb') as f:
                return f.read().decode('utf-8', errors='ignore')
        except Exception:
            return None

    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """Get file information (size, extension, etc.)."""
        path = Path(file_path)
        if not path.exists():
            return {}

        stat = path.stat()
        return {
            'size': stat.st_size,
            'extension': path.suffix.lower(),
            'name': path.name,
            'parent': str(path.parent)
        }
