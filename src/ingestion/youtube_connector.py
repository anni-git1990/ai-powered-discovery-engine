"""
YouTube Fashion Haul Video Comments Connector.
Contains expanded, realistic public user video comment feedback.
"""
from datetime import datetime, timezone
import hashlib
from typing import List
from src.ingestion.base import BaseConnector
from src.ingestion.datasets import YOUTUBE_COMMENTS
from src.models.schemas import RawPost, SourcePlatform


class YouTubeConnector(BaseConnector):
    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def fetch_posts(self, limit: int = 200) -> List[RawPost]:
        """Fetch YouTube haul/review video comments."""
        sample_yt_comments = YOUTUBE_COMMENTS

        posts: List[RawPost] = []
        for idx, text in enumerate(sample_yt_comments[:limit]):
            post_id = f"youtube_{idx + 1:04d}"
            author_hash = hashlib.md5(f"yt_user_{idx}".encode()).hexdigest()[:10]
            posts.append(
                RawPost(
                    post_id=post_id,
                    source_platform=SourcePlatform.YOUTUBE,
                    author_hash=author_hash,
                    timestamp=datetime.now(timezone.utc),
                    raw_text=text,
                    cleaned_text=text,
                    upvotes=idx * 8 + 5,
                    replies=idx % 3,
                    url=f"https://youtube.com/watch?v=fashionhaul&lc={post_id}"
                )
            )
        return posts

