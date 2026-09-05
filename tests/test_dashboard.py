"""
Unit tests for Phase 5 Dashboard and Report Generator.
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
from src.dashboard.report_generator import ExecutiveReportGenerator


from src.utils.formatters import format_label


def test_executive_report_generator():
    db = DuckDBManager(db_path=":memory:")
    vs = VectorStoreManager(persist_directory=":memory:", collection_name="test_report_coll")

    post = RawPost(
        post_id="rep_1",
        source_platform=SourcePlatform.PLAY_STORE,
        author_hash="h1",
        timestamp=datetime.now(timezone.utc),
        raw_text="Size M mismatch on Myntra",
        cleaned_text="Size M mismatch on Myntra"
    )
    db.insert_raw_post(post)

    insight = AnalyzedInsight(
        insight_id="i_rep_1",
        post_id="rep_1",
        wishlist_motivation=WishlistMotivation.HIGH_BUYING_INTENT,
        intent_score=0.85,
        primary_blocker=PrimaryBlocker.SIZE_FIT_UNCERTAINTY,
        secondary_blockers=[],
        user_segment=UserSegment.FIT_CONSCIOUS_BUYER,
        extracted_quotes=["Size M mismatch on Myntra"],
        confidence_score=0.95
    )
    db.insert_analyzed_insight(insight)

    generator = ExecutiveReportGenerator(db_manager=db, vector_manager=vs)
    report = generator.generate_markdown_report()

    assert "# Myntra Wishlist Intelligence Report: 2026" in report
    assert "Opportunity Comparison Matrix" in report
    assert "AI Evidence: Public-Feedback Mentions" in report
    assert "Survey Evidence: Respondent Count" in report
    assert "Purchase Impact" in report
    assert "Severity" in report
    assert "Evidence Strength" in report
    assert "Priority Rank" in report
    assert "Size & Fit Friction" in report

    db.close()



def test_format_label():
    assert format_label("SIZE_FIT_UNCERTAINTY") == "Size & Fit"
    assert format_label(PrimaryBlocker.SIZE_FIT_UNCERTAINTY) == "Size & Fit"

    assert format_label(WishlistMotivation.PRICE_DISCOUNT_WATCH) == "Price & Discount Watch"
    assert format_label(SourcePlatform.PLAY_STORE) == "Play Store"
    assert format_label(UserSegment.BUDGET_SENSITIVE_SAVER) == "Budget-Sensitive Saver"
    assert format_label(None) == ""


