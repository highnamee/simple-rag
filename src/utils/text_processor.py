"""
Text processing utilities.
"""

from typing import List


class TextProcessor:
    """Utility class for text processing operations."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks with smart boundaries."""
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # If we're not at the end, try to break at a boundary
            if end < len(text):
                boundary_end = self._find_boundary(text, start, end)
                if boundary_end > start:
                    end = boundary_end

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start position with overlap
            start = max(start + self.chunk_size - self.chunk_overlap, end)

        return chunks

    def _find_boundary(self, text: str, start: int, end: int) -> int:
        """Find the best boundary for text chunking."""
        # Look for sentence endings first
        sentence_endings = [". ", "! ", "? ", "\n\n"]
        best_break = -1

        for ending in sentence_endings:
            pos = text.rfind(ending, start, end)
            if pos > best_break:
                best_break = pos + len(ending)

        # If no sentence ending found, look for word boundary
        if best_break == -1:
            pos = text.rfind(" ", start, end)
            if pos > start:
                best_break = pos + 1

        return best_break if best_break > start else end

    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        lines = [line.strip() for line in text.split("\n")]
        cleaned_lines = []

        for line in lines:
            if line:  # Skip empty lines
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def extract_keywords(self, text: str, max_words: int = 10) -> List[str]:
        """Extract potential keywords from text (simple approach)."""
        import re

        # Simple keyword extraction - just get common words
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())

        # Filter out common stop words
        stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "up",
            "about",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "among",
            "this",
            "that",
            "these",
            "those",
            "his",
            "her",
            "their",
            "what",
            "which",
            "who",
            "when",
            "where",
            "why",
            "how",
            "all",
            "any",
            "both",
            "each",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "only",
            "own",
            "same",
            "also",
            "just",
            "than",
            "too",
            "very",
            "can",
            "will",
            "should",
            "could",
            "would",
            "may",
            "might",
            "must",
            "shall",
        }

        keywords = [word for word in words if word not in stop_words]

        # Get unique keywords maintaining order
        unique_keywords = []
        seen = set()
        for word in keywords:
            if word not in seen:
                unique_keywords.append(word)
                seen.add(word)
                if len(unique_keywords) >= max_words:
                    break

        return unique_keywords
