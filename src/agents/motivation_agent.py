"""
Wishlist Motivation & Purchase Intent Agent.
Classifies wishlist motivation and calculates purchase intent score.
"""
from typing import Any, Dict
from src.agents.base_agent import BaseAgent
from src.models.schemas import RawPost, WishlistMotivation


class MotivationAgent(BaseAgent):
    def process(self, post: RawPost) -> Dict[str, Any]:
        """Classify wishlist motivation and assign purchase intent score."""
        text = post.cleaned_text.lower()

        # Rule-assisted classification heuristics
        if any(k in text for k in ["buy right now", "buying it right now", "buying today", "buying now", "order today"]):
            motivation = WishlistMotivation.HIGH_BUYING_INTENT
            intent_score = 0.95
        elif any(k in text for k in ["waiting for discount", "waiting for sale", "price drop", "eors", "bogo", "coupon"]):
            motivation = WishlistMotivation.PRICE_DISCOUNT_WATCH
            intent_score = 0.75
        elif any(k in text for k in ["compare", "confused between", "which one", "options"]):
            motivation = WishlistMotivation.COMPARISON_DECISION
            intent_score = 0.65
        elif any(k in text for k in ["ootd", "wedding", "styling", "outfit", "match", "occasion"]):
            motivation = WishlistMotivation.STYLING_OCCASION_MATCHING
            intent_score = 0.60
        elif any(k in text for k in ["bookmarking", "dream", "mood board", "aesthetic", "wishlist saved since last month"]):
            motivation = WishlistMotivation.LOW_INTENT_BOOKMARKING
            intent_score = 0.20
        elif "wishlist" in text or "saved" in text:
            motivation = WishlistMotivation.HIGH_BUYING_INTENT
            intent_score = 0.80
        else:
            motivation = WishlistMotivation.HIGH_BUYING_INTENT
            intent_score = 0.70

        return {
            "wishlist_motivation": motivation,
            "intent_score": round(intent_score, 2)
        }
