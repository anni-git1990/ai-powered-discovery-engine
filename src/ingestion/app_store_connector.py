"""
Google Play Store & App Store Review Connector.
Contains expanded, realistic public user feedback for Myntra fashion wishlist behavior.
"""
from datetime import datetime, timezone
import hashlib
from typing import List
from src.ingestion.base import BaseConnector
from src.ingestion.datasets import PLAY_STORE_REVIEWS
from src.models.schemas import RawPost, SourcePlatform


class AppStoreConnector(BaseConnector):
    def __init__(self, app_id: str = "com.myntra.android"):
        self.app_id = app_id

    def fetch_posts(self, limit: int = 200) -> List[RawPost]:
        """Fetch reviews for Myntra app with expanded fashion domain feedback."""
        sample_reviews = PLAY_STORE_REVIEWS

        posts: List[RawPost] = []
        for idx, text in enumerate(sample_reviews[:limit]):
            post_id = f"playstore_{idx + 1:04d}"
            author_hash = hashlib.md5(f"app_user_{idx}".encode()).hexdigest()[:10]
            posts.append(
                RawPost(
                    post_id=post_id,
                    source_platform=SourcePlatform.PLAY_STORE,
                    author_hash=author_hash,
                    timestamp=datetime.now(timezone.utc),
                    raw_text=text,
                    cleaned_text=text,
                    upvotes=idx * 3 + 1,
                    replies=idx % 3
                )
            )
        return posts

