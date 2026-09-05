"""
Taxonomy schemas and data models for AI-Powered Discovery Engine.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class SourcePlatform(str, Enum):
    PLAY_STORE = "PLAY_STORE"
    APP_STORE = "APP_STORE"
    REDDIT = "REDDIT"
    YOUTUBE = "YOUTUBE"
    FORUM = "FORUM"


class WishlistMotivation(str, Enum):
    HIGH_BUYING_INTENT = "HIGH_BUYING_INTENT"
    PRICE_DISCOUNT_WATCH = "PRICE_DISCOUNT_WATCH"
    STYLING_OCCASION_MATCHING = "STYLING_OCCASION_MATCHING"
    COMPARISON_DECISION = "COMPARISON_DECISION"
    LOW_INTENT_BOOKMARKING = "LOW_INTENT_BOOKMARKING"


class PrimaryBlocker(str, Enum):
    SIZE_FIT_UNCERTAINTY = "SIZE_FIT_UNCERTAINTY"
    PRICE_VALUE_SKEPTICISM = "PRICE_VALUE_SKEPTICISM"
    QUALITY_FABRIC_CONCERN = "QUALITY_FABRIC_CONCERN"
    REVIEW_TRUST_DEFICIT = "REVIEW_TRUST_DEFICIT"
    STYLING_OCCASION_UNCERTAINTY = "STYLING_OCCASION_UNCERTAINTY"
    DELIVERY_RETURN_FRICTION = "DELIVERY_RETURN_FRICTION"
    INVENTORY_STOCK_OUT = "INVENTORY_STOCK_OUT"
    EVENT_TIMING_POSTPONEMENT = "EVENT_TIMING_POSTPONEMENT"
    NONE = "NONE"



class UserSegment(str, Enum):
    BUDGET_SENSITIVE_SAVER = "BUDGET_SENSITIVE_SAVER"
    FIT_CONSCIOUS_BUYER = "FIT_CONSCIOUS_BUYER"
    TREND_OCCASION_SHOPPER = "TREND_OCCASION_SHOPPER"
    QUALITY_SEEKER = "QUALITY_SEEKER"
    GENERAL_SHOPPER = "GENERAL_SHOPPER"


class RawPost(BaseModel):
    post_id: str = Field(..., description="Unique identifier for the raw post")
    source_platform: SourcePlatform = Field(..., description="Platform from which post was scraped")
    author_hash: str = Field(..., description="Anonymized author hash or handle ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of post creation")
    raw_text: str = Field(..., description="Original raw text of the post/review")
    cleaned_text: str = Field(..., description="Sanitized text with PII removed and slang normalized")
    upvotes: int = Field(default=0, ge=0, description="Upvotes/likes count")
    replies: int = Field(default=0, ge=0, description="Reply/comment count")
    url: Optional[str] = Field(default=None, description="Optional post URL")

    @field_validator("cleaned_text")
    def text_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Cleaned text must not be empty")
        return v.strip()


class AnalyzedInsight(BaseModel):
    insight_id: str = Field(..., description="Unique identifier for analyzed insight")
    post_id: str = Field(..., description="Foreign reference to RawPost post_id")
    wishlist_motivation: WishlistMotivation = Field(..., description="Classified wishlist motivation")
    intent_score: float = Field(..., ge=0.0, le=1.0, description="Purchase intent score from 0.0 to 1.0")
    primary_blocker: PrimaryBlocker = Field(..., description="Primary purchase blocker identified")
    secondary_blockers: List[PrimaryBlocker] = Field(default_factory=list, description="Secondary purchase blockers")
    external_validation_channel: Optional[str] = Field(default=None, description="External search channel mentioned")
    user_segment: UserSegment = Field(default=UserSegment.GENERAL_SHOPPER, description="Assigned user persona segment")
    extracted_quotes: List[str] = Field(default_factory=list, description="Verbatim quote snippets justifying insight")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Model classification confidence score")


class OpportunityArea(BaseModel):
    opportunity_id: str = Field(..., description="Unique identifier for opportunity area")
    title: str = Field(..., description="Descriptive title of the opportunity area")
    primary_blocker: PrimaryBlocker = Field(..., description="Associated primary blocker category")
    frequency_count: int = Field(..., ge=0, description="Total count of occurrences")
    avg_intent_score: float = Field(..., ge=0.0, le=1.0, description="Average intent score of affected users")
    severity_weight: float = Field(..., ge=0.0, description="Severity weight multiplier")
    opportunity_score: float = Field(..., ge=0.0, description="Calculated opportunity score (Freq * Intent * Severity)")
    sample_quotes: List[str] = Field(default_factory=list, description="Representative sample verbatim quotes")
    prioritization_level: str = Field(default="P2", description="Prioritization tier (P1, P2, P3)")
    survey_respondent_count: int = Field(default=0, ge=0, description="Survey evidence respondent count")
    evidence_strength: str = Field(default="Partially Supported", description="Evidence strength label")
    priority_rank: str = Field(default="P2", description="Priority rank (P1, P2, P3)")

    @property
    def opportunity_area(self) -> str:
        return self.title

    @property
    def ai_feedback_mentions(self) -> int:
        return self.frequency_count

    @property
    def purchase_impact(self) -> float:
        return self.avg_intent_score

    def calculate_score(self) -> float:
        self.opportunity_score = round(self.frequency_count * self.avg_intent_score * self.severity_weight, 2)
        if self.opportunity_score >= 300.0:
            self.prioritization_level = "P1"
            self.priority_rank = "P1"
            self.evidence_strength = "Strongly Supported"
        elif self.opportunity_score >= 50.0:
            self.prioritization_level = "P2"
            self.priority_rank = "P2"
            self.evidence_strength = "Partially Supported"
        else:
            self.prioritization_level = "P3"
            self.priority_rank = "P3"
            self.evidence_strength = "Needs Interview Validation"
        return self.opportunity_score



