"""
Unit tests for Taxonomy Schemas and Pydantic Models.
"""
from datetime import datetime
import pytest
from pydantic import ValidationError

from src.models.schemas import (
    SourcePlatform,
    WishlistMotivation,
    PrimaryBlocker,
    UserSegment,
    RawPost,
    AnalyzedInsight,
    OpportunityArea
)


def test_raw_post_valid_instantiation():
    post = RawPost(
        post_id="post_001",
        source_platform=SourcePlatform.REDDIT,
        author_hash="hash_abc123",
        timestamp=datetime(2026, 8, 17, 12, 0, 0),
        raw_text="Is this Myntra dress size true to fit?",
        cleaned_text="Is this Myntra dress size true to fit?",
        upvotes=15,
        replies=3
    )
    assert post.post_id == "post_001"
    assert post.source_platform == SourcePlatform.REDDIT
    assert post.cleaned_text == "Is this Myntra dress size true to fit?"
    assert post.upvotes == 15


def test_raw_post_empty_cleaned_text_raises_validation_error():
    with pytest.raises(ValidationError):
        RawPost(
            post_id="post_002",
            source_platform=SourcePlatform.PLAY_STORE,
            author_hash="hash_def456",
            raw_text="Hello",
            cleaned_text="   "
        )


def test_analyzed_insight_creation():
    insight = AnalyzedInsight(
        insight_id="insight_001",
        post_id="post_001",
        wishlist_motivation=WishlistMotivation.HIGH_BUYING_INTENT,
        intent_score=0.9,
        primary_blocker=PrimaryBlocker.SIZE_FIT_UNCERTAINTY,
        secondary_blockers=[PrimaryBlocker.REVIEW_TRUST_DEFICIT],
        user_segment=UserSegment.FIT_CONSCIOUS_BUYER,
        extracted_quotes=["Not sure about size M vs L"],
        confidence_score=0.95
    )
    assert insight.insight_id == "insight_001"
    assert insight.wishlist_motivation == WishlistMotivation.HIGH_BUYING_INTENT
    assert insight.primary_blocker == PrimaryBlocker.SIZE_FIT_UNCERTAINTY
    assert PrimaryBlocker.REVIEW_TRUST_DEFICIT in insight.secondary_blockers
    assert insight.intent_score == 0.9


def test_opportunity_area_score_calculation():
    opp = OpportunityArea(
        opportunity_id="opp_001",
        title="Size & Fit Uncertainty in Kurtis",
        primary_blocker=PrimaryBlocker.SIZE_FIT_UNCERTAINTY,
        frequency_count=30,
        avg_intent_score=0.8,
        severity_weight=2.5,
        opportunity_score=0.0,
        sample_quotes=["Size is confusing"],
        survey_respondent_count=450
    )
    score = opp.calculate_score()
    assert score == 60.0
    assert opp.prioritization_level == "P2"
    assert opp.priority_rank == "P2"
    assert opp.evidence_strength == "Partially Supported"
    assert opp.opportunity_area == "Size & Fit Uncertainty in Kurtis"
    assert opp.ai_feedback_mentions == 30
    assert opp.purchase_impact == 0.8
    assert opp.survey_respondent_count == 450

    opp_low = OpportunityArea(
        opportunity_id="opp_002",
        title="Event Postponement",
        primary_blocker=PrimaryBlocker.EVENT_TIMING_POSTPONEMENT,
        frequency_count=5,
        avg_intent_score=0.4,
        severity_weight=1.2,
        opportunity_score=0.0
    )
    # 5 * 0.4 * 1.2 = 2.4 -> P3
    score_low = opp_low.calculate_score()
    assert score_low == 2.4
    assert opp_low.prioritization_level == "P3"
    assert opp_low.priority_rank == "P3"
    assert opp_low.evidence_strength == "Needs Interview Validation"

