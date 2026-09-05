"""
Unified Ingestion & Preprocessing Pipeline Runner.
Coordinates data collection, PII sanitization, slang normalization, deduplication, and storage insertion.
"""
from typing import List, Tuple
from src.ingestion.app_store_connector import AppStoreConnector
from src.ingestion.reddit_connector import RedditConnector
from src.ingestion.youtube_connector import YouTubeConnector
from src.models.schemas import RawPost
from src.preprocessing.pii_sanitizer import PIISanitizer
from src.preprocessing.slang_normalizer import SlangNormalizer
from src.preprocessing.deduplicator import Deduplicator
from src.storage.db import DuckDBManager
from src.storage.vector_store import VectorStoreManager


class IngestionPipeline:
    def __init__(
        self,
        db_manager: DuckDBManager = None,
        vector_manager: VectorStoreManager = None
    ):
        self.db_manager = db_manager or DuckDBManager()
        self.vector_manager = vector_manager or VectorStoreManager()

        self.pii_sanitizer = PIISanitizer()
        self.slang_normalizer = SlangNormalizer()
        self.deduplicator = Deduplicator()

        self.connectors = [
            AppStoreConnector(),
            RedditConnector(),
            YouTubeConnector()
        ]

    def run(self, limit_per_source: int = 50) -> Tuple[int, int]:
        """
        Execute ingestion pipeline.
        Returns: (processed_count, skipped_duplicates_count)
        """
        raw_posts: List[RawPost] = []
        for connector in self.connectors:
            raw_posts.extend(connector.fetch_posts(limit=limit_per_source))

        processed_count = 0
        duplicate_count = 0

        vector_ids = []
        vector_docs = []
        vector_metadatas = []

        for post in raw_posts:
            # Step 1: PII Sanitization
            sanitized_text = self.pii_sanitizer.sanitize(post.raw_text)

            # Step 2: Slang Normalization
            normalized_text = self.slang_normalizer.normalize(sanitized_text)

            # Step 3: Deduplication Check
            if self.deduplicator.is_duplicate(normalized_text):
                duplicate_count += 1
                continue

            # Update cleaned text
            post.cleaned_text = normalized_text

            # Step 4: Persist to DuckDB
            self.db_manager.insert_raw_post(post)

            # Prepare for Vector Database insertion
            vector_ids.append(post.post_id)
            vector_docs.append(post.cleaned_text)
            vector_metadatas.append({
                "source": post.source_platform.value,
                "author_hash": post.author_hash,
                "upvotes": post.upvotes
            })

            processed_count += 1

        # Batch insert into Vector Store
        if vector_ids:
            self.vector_manager.add_documents(
                ids=vector_ids,
                documents=vector_docs,
                metadatas=vector_metadatas
            )

        return processed_count, duplicate_count
