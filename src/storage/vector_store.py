"""
ChromaDB Vector Store Manager.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings


class VectorStoreManager:
    def __init__(
        self,
        persist_directory: str = "data/chroma_db",
        collection_name: str = "fashion_wishlist_embeddings"
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        if persist_directory == ":memory:":
            self.client = chromadb.Client()
        else:
            Path(persist_directory).mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=persist_directory)

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        embeddings: Optional[List[List[float]]] = None
    ) -> None:
        """Add documents and optional embeddings/metadata to the ChromaDB collection."""
        kwargs: Dict[str, Any] = {
            "ids": ids,
            "documents": documents
        }
        if metadatas is not None:
            kwargs["metadatas"] = metadatas
        if embeddings is not None:
            kwargs["embeddings"] = embeddings

        self.collection.add(**kwargs)

    def query(
        self,
        query_texts: List[str],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform semantic similarity search against stored embeddings."""
        kwargs: Dict[str, Any] = {
            "query_texts": query_texts,
            "n_results": n_results
        }
        if where is not None:
            kwargs["where"] = where

        return self.collection.query(**kwargs)

    def get_by_id(self, doc_id: str) -> Dict[str, Any]:
        """Fetch document payload by id."""
        return self.collection.get(ids=[doc_id])

    def count(self) -> int:
        """Return total document count in collection."""
        return self.collection.count()
