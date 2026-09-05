"""
Unit tests and evaluation benchmark for Multi-Agent AI Processing Engine.
"""
from datetime import datetime, timezone
import pytest

from src.agents.triage_agent import TriageAgent
from src.agents.motivation_agent import MotivationAgent
from src.agents.blocker_agent import BlockerAgent
from src.agents.social_validation_agent import SocialValidationAgent
from src.agents.segmentation_agent import SegmentationAgent
from src.agents.orchestrator import AgentOrchestrator
from src.models.schemas import (
    RawPost,
    SourcePlatform,
    WishlistMotivation,
    PrimaryBlocker,
    UserSegment
)
from src.storage.db import DuckDBManager


def test_triage_agent_evaluates_relevance():
    agent = TriageAgent()
    relevant_post = RawPost(
        post_id="p1",
        source_platform=SourcePlatform.REDDIT,
        author_hash="h1",
        timestamp=datetime.now(timezone.utc),
        raw_text="Myntra size mismatch is frustrating",
        cleaned_text="Myntra size mismatch is frustrating"
    )
    irrelevant_post = RawPost(
        post_id="p2",
        source_platform=SourcePlatform.PLAY_STORE,
        author_hash="h2",
        timestamp=datetime.now(timezone.utc),
        raw_text="Random app error loading home page",
        cleaned_text="a b"
    )

    assert agent.process(relevant_post)["is_relevant"] is True
    assert agent.process(irrelevant_post)["is_relevant"] is False


def test_motivation_agent_classifies_intent():
    agent = MotivationAgent()

    high_intent_post = RawPost(
        post_id="p3",
        source_platform=SourcePlatform.PLAY_STORE,
        author_hash="h3",
        timestamp=datetime.now(timezone.utc),
        raw_text="buying it right now",
        cleaned_text="buying it right now"
    )
    discount_post = RawPost(
        post_id="p4",
        source_platform=SourcePlatform.REDDIT,
        author_hash="h4",
        timestamp=datetime.now(timezone.utc),
        raw_text="waiting for EORS sale discount",
        cleaned_text="waiting for EORS sale discount"
    )

    res_high = agent.process(high_intent_post)
    assert res_high["wishlist_motivation"] == WishlistMotivation.HIGH_BUYING_INTENT
    assert res_high["intent_score"] >= 0.9

    res_disc = agent.process(discount_post)
    assert res_disc["wishlist_motivation"] == WishlistMotivation.PRICE_DISCOUNT_WATCH


def test_blocker_agent_extracts_primary_and_secondary_blockers():
    agent = BlockerAgent()
    post = RawPost(
        post_id="p5",
        source_platform=SourcePlatform.REDDIT,
        author_hash="h5",
        timestamp=datetime.now(timezone.utc),
        raw_text="Size M feels tight and price is too high for poor fabric quality",
        cleaned_text="Size M feels tight and price is too high for poor fabric quality"
    )

    res = agent.process(post)
    assert res["primary_blocker"] == PrimaryBlocker.SIZE_FIT_UNCERTAINTY
    assert PrimaryBlocker.PRICE_VALUE_SKEPTICISM in res["secondary_blockers"]
    assert PrimaryBlocker.QUALITY_FABRIC_CONCERN in res["secondary_blockers"]
    assert len(res["extracted_quotes"]) > 0


def test_social_validation_and_segmentation_agents():
    social_agent = SocialValidationAgent()
    seg_agent = SegmentationAgent()

    post = RawPost(
        post_id="p6",
        source_platform=SourcePlatform.YOUTUBE,
        author_hash="h6",
        timestamp=datetime.now(timezone.utc),
        raw_text="Searching YouTube try-on haul for BOGO discount sale Kurtis",
        cleaned_text="Searching YouTube try-on haul for BOGO discount sale Kurtis"
    )

    soc_res = social_agent.process(post)
    assert soc_res["external_validation_channel"] == "YOUTUBE_HAUL_SEARCH"

    seg_res = seg_agent.process(post)
    assert seg_res["user_segment"] == UserSegment.BUDGET_SENSITIVE_SAVER


def test_agent_orchestrator_end_to_end_insight_generation():
    db = DuckDBManager(db_path=":memory:")
    orchestrator = AgentOrchestrator(db_manager=db)

    posts = [
        RawPost(
            post_id="p10",
            source_platform=SourcePlatform.REDDIT,
            author_hash="h10",
            timestamp=datetime.now(timezone.utc),
            raw_text="Wishlisted 5 Kurtis on Myntra, waiting for size L fitting reviews",
            cleaned_text="Wishlisted 5 Kurtis on Myntra, waiting for size L fitting reviews"
        ),
        RawPost(
            post_id="p11",
            source_platform=SourcePlatform.PLAY_STORE,
            author_hash="h11",
            timestamp=datetime.now(timezone.utc),
            raw_text="Price dropped on my wishlisted dress, buying today!",
            cleaned_text="Price dropped on my wishlisted dress, buying today!"
        )
    ]

    for p in posts:
        db.insert_raw_post(p)

    insights = orchestrator.process_batch(posts)
    assert len(insights) == 2

    # Check persistence in DuckDB
    fetched_insight = db.get_insight_by_id(insights[0].insight_id)
    assert fetched_insight is not None
    assert fetched_insight.post_id == "p10"
    db.close()
