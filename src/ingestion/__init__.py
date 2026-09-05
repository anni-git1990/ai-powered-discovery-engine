"""
Multi-source Data Ingestion Module (App Store, Play Store, Reddit, YouTube).
"""
from src.ingestion.base import BaseConnector
from src.ingestion.app_store_connector import AppStoreConnector
from src.ingestion.reddit_connector import RedditConnector
from src.ingestion.youtube_connector import YouTubeConnector
from src.ingestion.pipeline import IngestionPipeline

__all__ = [
    "BaseConnector",
    "AppStoreConnector",
    "RedditConnector",
    "YouTubeConnector",
    "IngestionPipeline"
]
