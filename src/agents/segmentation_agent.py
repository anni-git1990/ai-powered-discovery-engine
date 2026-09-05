"""
User Segmentation & Persona Agent.
Assigns user post to demographic/behavioral shopping personas.
"""
from typing import Any, Dict
from src.agents.base_agent import BaseAgent
from src.models.schemas import RawPost, UserSegment


class SegmentationAgent(BaseAgent):
    def process(self, post: RawPost) -> Dict[str, Any]:
        """Classify user post into target persona segment."""
        text = post.cleaned_text.lower()

        if any(k in text for k in ["discount", "price", "sale", "mrp", "coupon", "cheap", "eors", "bogo"]):
            segment = UserSegment.BUDGET_SENSITIVE_SAVER
        elif any(k in text for k in ["size", "fit", "fitting", "tight", "loose", "chota", "bada", "mismatch"]):
            segment = UserSegment.FIT_CONSCIOUS_BUYER
        elif any(k in text for k in ["ootd", "wedding", "trend", "occasion", "party", "style"]):
            segment = UserSegment.TREND_OCCASION_SHOPPER
        elif any(k in text for k in ["quality", "fabric", "material", "premium", "durability"]):
            segment = UserSegment.QUALITY_SEEKER
        else:
            segment = UserSegment.GENERAL_SHOPPER

        return {
            "user_segment": segment
        }
