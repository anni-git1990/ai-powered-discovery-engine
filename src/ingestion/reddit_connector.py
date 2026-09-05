"""
Reddit Subreddit Comments & Posts Connector.
Contains expanded, realistic public user fashion discussion threads.
"""
from datetime import datetime, timezone
import hashlib
from typing import List
from src.ingestion.base import BaseConnector
from src.ingestion.datasets import REDDIT_POSTS
from src.models.schemas import RawPost, SourcePlatform


class RedditConnector(BaseConnector):
    def __init__(self, subreddits: List[str] = None):
        self.subreddits = subreddits or ["IndianFashionAddicts", "ShoppingDealsIndia", "DesiFragranceAddicts"]

    def fetch_posts(self, limit: int = 200) -> List[RawPost]:
        """Fetch fashion shopping posts/comments from Reddit."""
        sample_reddit_posts = REDDIT_POSTS

        posts: List[RawPost] = []
        for idx, text in enumerate(sample_reddit_posts[:limit]):
            post_id = f"reddit_{idx + 1:04d}"
            author_hash = hashlib.md5(f"reddit_user_{idx}".encode()).hexdigest()[:10]
            posts.append(
                RawPost(
                    post_id=post_id,
                    source_platform=SourcePlatform.REDDIT,
                    author_hash=author_hash,
                    timestamp=datetime.now(timezone.utc),
                    raw_text=text,
                    cleaned_text=text,
                    upvotes=idx * 4 + 2,
                    replies=idx % 4 + 1,
                    url=f"https://reddit.com/r/IndianFashionAddicts/comments/{post_id}"
                )
            )
        return posts

