"""
Vector storage and similarity search.
"""

import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
import faiss

from .document_processor import Document, DocumentProcessor
from ..utils import logger, FileUtils


class VectorStore:
    """Manages vector embeddings and similarity search using FAISS."""

    def __init__(self,
                 model_name: str = "all-MiniLM-L6-v2",
                 vector_db_path: str = "./vector_db"):
        self.model_name = model_name
        self.vector_db_path = Path(vector_db_path)
        self.file_utils = FileUtils()

        # Ensure directory exists
        self.file_utils.ensure_directory(str(self.vector_db_path))

        # Initialize embedding model
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

        # Initialize FAISS index and document storage
        self.index = None
        self.documents = []
        self.file_hashes = {}  # Track file hashes for incremental updates

        # Load existing index if available
        self.load_index()

    def save_index(self):
        """Save FAISS index and metadata to disk."""
        if self.index is not None:
            try:
                # Save FAISS index
                faiss.write_index(self.index, str(self.vector_db_path / "faiss.index"))

                # Save documents metadata
                with open(self.vector_db_path / "documents.pkl", "wb") as f:
                    pickle.dump(self.documents, f)

                # Save file hashes
                with open(self.vector_db_path / "file_hashes.json", "w") as f:
                    json.dump(self.file_hashes, f, indent=2)

                logger.info(f"Index saved with {len(self.documents)} documents")

            except Exception as e:
                logger.error(f"Error saving index: {e}")

    def load_index(self):
        """Load FAISS index and metadata from disk."""
        index_path = self.vector_db_path / "faiss.index"
        docs_path = self.vector_db_path / "documents.pkl"
        hashes_path = self.vector_db_path / "file_hashes.json"

        if index_path.exists() and docs_path.exists():
            try:
                # Load FAISS index
                self.index = faiss.read_index(str(index_path))

                # Load documents
                with open(docs_path, "rb") as f:
                    self.documents = pickle.load(f)

                # Load file hashes
                if hashes_path.exists():
                    with open(hashes_path, "r") as f:
                        self.file_hashes = json.load(f)

                logger.info(f"Loaded existing index with {len(self.documents)} documents")

            except Exception as e:
                logger.error(f"Error loading index: {e}")
                self._initialize_empty_index()
        else:
            self._initialize_empty_index()

    def _initialize_empty_index(self):
        """Initialize empty FAISS index."""
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
        self.documents = []
        self.file_hashes = {}
        logger.info("Initialized empty vector index")

    def add_documents(self, documents: List[Document]):
        """Add documents to the vector store."""
        if not documents:
            return

        # Extract text content for embedding
        texts = [doc.content for doc in documents]

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} document chunks...")
        embeddings = self.model.encode(texts, show_progress_bar=True)

        # Normalize embeddings for cosine similarity
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))

        # Store documents
        self.documents.extend(documents)

        logger.info(f"Added {len(documents)} documents to index")

    def remove_documents_by_file(self, file_path: str):
        """Remove all documents from a specific file."""
        # FAISS doesn't support deletion easily, so we'll rebuild the index
        remaining_docs = [doc for doc in self.documents if doc.file_path != file_path]

        if len(remaining_docs) != len(self.documents):
            logger.info(f"Removing documents from file: {file_path}")

            # Rebuild index with remaining documents
            self._initialize_empty_index()
            if remaining_docs:
                self.add_documents(remaining_docs)

    def search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Search for similar documents."""
        if self.index is None or self.index.ntotal == 0:
            logger.warning("No documents in index for search")
            return []

        # Generate query embedding
        query_embedding = self.model.encode([query])
        query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)

        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), k)

        # Return documents with scores
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and idx < len(self.documents):
                results.append((self.documents[idx], float(score)))

        logger.debug(f"Search for '{query}' returned {len(results)} results")
        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        file_count = len({doc.file_path for doc in self.documents})

        return {
            "total_documents": len(self.documents),
            "total_files": file_count,
            "embedding_dimension": self.embedding_dim,
            "model_name": self.model_name,
            "index_size": self.index.ntotal if self.index else 0
        }


class RAGIndexer:
    """Manages incremental indexing of documents."""

    def __init__(self,
                 data_folder: str,
                 vector_store: VectorStore,
                 chunk_size: int = 512,
                 chunk_overlap: int = 50):
        self.data_folder = Path(data_folder)
        self.vector_store = vector_store
        self.processor = DocumentProcessor(chunk_size, chunk_overlap)

    def index_new_and_changed_files(self) -> Dict[str, int]:
        """Index only new or changed files."""
        if not self.data_folder.exists():
            logger.error(f"Data folder not found: {self.data_folder}")
            return {"new_files": 0, "updated_files": 0, "unchanged_files": 0}

        all_files = self.processor.scan_directory(str(self.data_folder))
        stats = {"new_files": 0, "updated_files": 0, "unchanged_files": 0}

        for file_path in all_files:
            current_hash = self.processor.file_utils.get_file_hash(file_path)
            stored_hash = self.vector_store.file_hashes.get(file_path)

            if stored_hash != current_hash:
                if stored_hash is None:
                    logger.info(f"Processing new file: {file_path}")
                    stats["new_files"] += 1
                else:
                    logger.info(f"Processing updated file: {file_path}")
                    stats["updated_files"] += 1
                    # Remove old documents from this file
                    self.vector_store.remove_documents_by_file(file_path)

                # Process and add documents
                documents = self.processor.process_file(file_path)
                if documents:
                    self.vector_store.add_documents(documents)
                    self.vector_store.file_hashes[file_path] = current_hash
            else:
                stats["unchanged_files"] += 1

        # Save the updated index
        self.vector_store.save_index()

        logger.info(f"Indexing complete: {stats}")
        return stats

    def force_reindex_all(self) -> int:
        """Force reindex all files in the data folder."""
        logger.info("Force reindexing all files...")

        # Clear existing index
        self.vector_store._initialize_empty_index()

        all_files = self.processor.scan_directory(str(self.data_folder))
        total_docs = 0

        for file_path in all_files:
            logger.info(f"Processing: {file_path}")
            documents = self.processor.process_file(file_path)
            if documents:
                self.vector_store.add_documents(documents)
                self.vector_store.file_hashes[file_path] = self.processor.file_utils.get_file_hash(file_path)
                total_docs += len(documents)

        self.vector_store.save_index()
        logger.info(f"Reindexing complete: {total_docs} documents processed")
        return total_docs
