"""
Vector Clustering & Unmet Need Extraction Module.
Clusters unmapped high-intent posts to discover emerging friction themes.
"""
from typing import Any, Dict, List
import re
from collections import Counter
from src.storage.vector_store import VectorStoreManager


class VectorClusterer:
    def __init__(self, vector_manager: VectorStoreManager):
        self.vector_manager = vector_manager

    def discover_unmet_needs(self, min_cluster_size: int = 2) -> List[Dict[str, Any]]:
        """
        Extract document payloads from vector store, cluster text by shared keywords/ngram patterns,
        and generate automated titles and summaries for emerging friction areas.
        """
        count = self.vector_manager.count()
        if count == 0:
            return []

        # Retrieve documents from ChromaDB collection
        docs_res = self.vector_manager.collection.get()
        documents = docs_res.get("documents", [])
        metadatas = docs_res.get("metadatas", [])
        ids = docs_res.get("ids", [])

        # Extract n-grams / keyword frequency clusters
        ngram_counter = Counter()
        doc_clusters: Dict[str, List[Dict[str, Any]]] = {}

        for doc_id, doc, meta in zip(ids, documents, metadatas):
            words = [w.lower() for w in re.findall(r'\w+', doc) if len(w) > 3]
            for i in range(len(words) - 1):
                ngram = f"{words[i]} {words[i+1]}"
                if any(kw in ngram for kw in ["size", "price", "quality", "fit", "discount", "review", "photo", "fabric"]):
                    ngram_counter[ngram] += 1
                    if ngram not in doc_clusters:
                        doc_clusters[ngram] = []
                    doc_clusters[ngram].append({"id": doc_id, "text": doc, "metadata": meta})

        clusters: List[Dict[str, Any]] = []

        for ngram, freq in ngram_counter.most_common(5):
            if freq >= min_cluster_size:
                sample_texts = [item["text"] for item in doc_clusters[ngram][:3]]
                clusters.append({
                    "cluster_theme": ngram.title(),
                    "frequency": freq,
                    "summary": f"Emerging user friction topic around '{ngram}'.",
                    "sample_quotes": sample_texts
                })

        return clusters
