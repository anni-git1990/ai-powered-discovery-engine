"""
Unit tests for Phase 4 Analytics Engine: Scoring, Aggregation, and Vector Clustering.
"""
from datetime import datetime, timezone
import pytest

from src.models.schemas import (
    RawPost,
    AnalyzedInsight,
    SourcePlatform,
    WishlistMotivation,
    PrimaryBlocker,
    UserSegment
)
from src.storage.db import DuckDBManager
from src.storage.vector_store import VectorStoreManager
from src.analytics.scoring import OpportunityScorer
from src.analytics.aggregations import WarehouseAggregator
from src.analytics.clustering import VectorClusterer


@pytest.fixture
def populated_db():
    db = DuckDBManager(db_path=":memory:")

    posts = [
        RawPost(
            post_id="p_1",
            source_platform=SourcePlatform.PLAY_STORE,
            author_hash="h1",
            timestamp=datetime.now(timezone.utc),
            raw_text="Size M feels tight",
            cleaned_text="Size M feels tight"
        ),
        RawPost(
            post_id="p_2",
            source_platform=SourcePlatform.REDDIT,
            author_hash="h2",
            timestamp=datetime.now(timezone.utc),
            raw_text="Waiting for discount sale",
            cleaned_text="Waiting for discount sale"
        )
    ]

    for p in posts:
        db.insert_raw_post(p)

    insights = [
        AnalyzedInsight(
            insight_id="i_1",
            post_id="p_1",
            wishlist_motivation=WishlistMotivation.HIGH_BUYING_INTENT,
            intent_score=0.8,
            primary_blocker=PrimaryBlocker.SIZE_FIT_UNCERTAINTY,
            secondary_blockers=[PrimaryBlocker.REVIEW_TRUST_DEFICIT],
            user_segment=UserSegment.FIT_CONSCIOUS_BUYER,
            extracted_quotes=["Size M feels tight"],
            confidence_score=0.9
        ),
        AnalyzedInsight(
            insight_id="i_2",
            post_id="p_2",
            wishlist_motivation=WishlistMotivation.PRICE_DISCOUNT_WATCH,
            intent_score=0.7,
            primary_blocker=PrimaryBlocker.PRICE_VALUE_SKEPTICISM,
            secondary_blockers=[],
            user_segment=UserSegment.BUDGET_SENSITIVE_SAVER,
            extracted_quotes=["Waiting for discount sale"],
            confidence_score=0.85
        )
    ]

    for i in insights:
        db.insert_analyzed_insight(i)

    yield db
    db.close()


def test_opportunity_scorer(populated_db):
    scorer = OpportunityScorer(db_manager=populated_db)
    opps = scorer.compute_opportunity_scores()

    assert len(opps) == 2

    # SIZE_FIT_UNCERTAINTY score: freq=1, avg_intent=0.8, severity=2.5 -> score = 2.0
    size_opp = next(o for o in opps if o.primary_blocker == PrimaryBlocker.SIZE_FIT_UNCERTAINTY)
    assert size_opp.frequency_count == 1
    assert size_opp.avg_intent_score == 0.8
    assert size_opp.severity_weight == 2.5
    assert size_opp.opportunity_score == 2.0
    assert size_opp.survey_respondent_count == 450
    assert size_opp.evidence_strength == "Needs Interview Validation"
    assert size_opp.priority_rank == "P3"



def test_warehouse_aggregator(populated_db):
    aggregator = WarehouseAggregator(db_manager=populated_db)

    mot_bd = aggregator.get_motivation_breakdown()
    assert len(mot_bd) == 2

    block_bd = aggregator.get_blocker_breakdown()
    assert len(block_bd) == 2

    funnel = aggregator.get_conversion_funnel_summary()
    assert funnel["total_raw_posts"] == 2
    assert funnel["total_analyzed_insights"] == 2
    assert funnel["high_intent_count"] == 2
    assert funnel["high_intent_dropoff_pct"] == 100.0


def test_vector_clusterer():
    vs = VectorStoreManager(persist_directory=":memory:", collection_name="test_cluster_coll")
    vs.add_documents(
        ids=["c1", "c2", "c3"],
        documents=[
            "Size M fitting and size mismatch issues on Myntra",
            "Size M fitting and size chart is wrong",
            "Waiting for discount price drops"
        ]
    )

    clusterer = VectorClusterer(vector_manager=vs)
    unmet_needs = clusterer.discover_unmet_needs(min_cluster_size=2)

    assert len(unmet_needs) >= 1
    assert "Size" in unmet_needs[0]["cluster_theme"] or "Fit" in unmet_needs[0]["cluster_theme"]
