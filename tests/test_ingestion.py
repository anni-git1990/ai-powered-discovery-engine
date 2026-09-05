"""
Unit tests for Ingestion Connectors and Unified Pipeline.
"""
from src.ingestion.app_store_connector import AppStoreConnector
from src.ingestion.reddit_connector import RedditConnector
from src.ingestion.youtube_connector import YouTubeConnector
from src.ingestion.pipeline import IngestionPipeline
from src.storage.db import DuckDBManager
from src.storage.vector_store import VectorStoreManager


def test_connectors_fetch_valid_raw_posts():
    app_connector = AppStoreConnector()
    reddit_connector = RedditConnector()
    yt_connector = YouTubeConnector()

    app_posts = app_connector.fetch_posts(limit=5)
    reddit_posts = reddit_connector.fetch_posts(limit=5)
    yt_posts = yt_connector.fetch_posts(limit=5)

    assert len(app_posts) == 5
    assert len(reddit_posts) == 5
    assert len(yt_posts) == 5

    assert app_posts[0].source_platform.value == "PLAY_STORE"
    assert reddit_posts[0].source_platform.value == "REDDIT"
    assert yt_posts[0].source_platform.value == "YOUTUBE"


def test_ingestion_pipeline_end_to_end():
    db = DuckDBManager(db_path=":memory:")
    vs = VectorStoreManager(persist_directory=":memory:", collection_name="test_pipeline_coll")

    pipeline = IngestionPipeline(db_manager=db, vector_manager=vs)
    processed, duplicates = pipeline.run(limit_per_source=10)

    assert processed > 0
    assert duplicates >= 0

    all_posts = db.get_all_raw_posts()
    assert len(all_posts) == processed

    assert vs.count() == processed
    db.close()
