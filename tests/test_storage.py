"""
Unit tests for DuckDB relational storage and ChromaDB vector store.
"""
from datetime import datetime
import pytest

from src.models.schemas import (
    SourcePlatform,
    WishlistMotivation,
    PrimaryBlocker,
    UserSegment,
    RawPost,
    AnalyzedInsight,
    OpportunityArea
)
from src.storage.db import DuckDBManager
from src.storage.vector_store import VectorStoreManager


def test_duckdb_manager_crud_operations():
    db = DuckDBManager(db_path=":memory:")

    # 1. Insert RawPost
    post = RawPost(
        post_id="p_100",
        source_platform=SourcePlatform.PLAY_STORE,
        author_hash="author_xyz",
        timestamp=datetime(2026, 8, 17, 10, 0, 0),
        raw_text="The app wishlisting works fine but prices change rapidly.",
        cleaned_text="The app wishlisting works fine but prices change rapidly.",
        upvotes=5,
        replies=1
    )
    db.insert_raw_post(post)

    fetched_post = db.get_raw_post("p_100")
    assert fetched_post is not None
    assert fetched_post.post_id == "p_100"
    assert fetched_post.source_platform == SourcePlatform.PLAY_STORE
    assert fetched_post.cleaned_text == "The app wishlisting works fine but prices change rapidly."

    # 2. Insert AnalyzedInsight
    insight = AnalyzedInsight(
        insight_id="i_100",
        post_id="p_100",
        wishlist_motivation=WishlistMotivation.PRICE_DISCOUNT_WATCH,
        intent_score=0.75,
        primary_blocker=PrimaryBlocker.PRICE_VALUE_SKEPTICISM,
        secondary_blockers=[PrimaryBlocker.REVIEW_TRUST_DEFICIT],
        user_segment=UserSegment.BUDGET_SENSITIVE_SAVER,
        extracted_quotes=["prices change rapidly"],
        confidence_score=0.92
    )
    db.insert_analyzed_insight(insight)

    fetched_insight = db.get_insight_by_id("i_100")
    assert fetched_insight is not None
    assert fetched_insight.insight_id == "i_100"
    assert fetched_insight.wishlist_motivation == WishlistMotivation.PRICE_DISCOUNT_WATCH
    assert fetched_insight.primary_blocker == PrimaryBlocker.PRICE_VALUE_SKEPTICISM

    # 3. Insert OpportunityArea
    opp = OpportunityArea(
        opportunity_id="opp_100",
        title="Price Sensitivity in Sale Events",
        primary_blocker=PrimaryBlocker.PRICE_VALUE_SKEPTICISM,
        frequency_count=40,
        avg_intent_score=0.7,
        severity_weight=2.0,
        opportunity_score=56.0,
        prioritization_level="P1"
    )
    db.insert_opportunity_area(opp)

    all_posts = db.get_all_raw_posts()
    assert len(all_posts) == 1

    all_insights = db.get_all_analyzed_insights()
    assert len(all_insights) == 1
    assert all_insights[0].insight_id == "i_100"

    db.close()


def test_vector_store_manager_operations():
    vs = VectorStoreManager(
        persist_directory=":memory:",
        collection_name="test_collection"
    )

    ids = ["doc_1", "doc_2"]
    documents = [
        "Uncertainty regarding size M vs L for ethnic wear on Myntra",
        "Waiting for Diwali sale discounts before completing purchase"
    ]
    metadatas = [
        {"blocker": "SIZE_FIT_UNCERTAINTY", "source": "REDDIT"},
        {"blocker": "PRICE_VALUE_SKEPTICISM", "source": "YOUTUBE"}
    ]

    vs.add_documents(ids=ids, documents=documents, metadatas=metadatas)

    assert vs.count() == 2

    # Query similarity
    results = vs.query(query_texts=["fitting and size issue"], n_results=1)
    assert len(results["ids"][0]) == 1
    assert results["ids"][0][0] == "doc_1"
