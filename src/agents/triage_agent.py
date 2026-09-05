"""
Ingestion & Triage Agent.
Evaluates whether a post is relevant to fashion, e-commerce, and wishlist behavior.
"""
from typing import Any, Dict
from src.agents.base_agent import BaseAgent
from src.models.schemas import RawPost


class TriageAgent(BaseAgent):
    RELEVANCE_KEYWORDS = [
        "wishlist", "wishlisted", "wishlisting", "saved", "cart", "myntra",
        "size", "fit", "fitting", "price", "discount", "sale", "eors", "bogo",
        "mrp", "quality", "fabric", "material", "return", "exchange", "delivery",
        "ootd", "haul", "dress", "shirt", "kurtis", "jacket", "jeans", "top", "blazer", "lehenga"
    ]

    def process(self, post: RawPost) -> Dict[str, Any]:
        """Assess post relevance and determine if it should be processed further."""
        text_lower = post.cleaned_text.lower()
        matched_keywords = [kw for kw in self.RELEVANCE_KEYWORDS if kw in text_lower]

        score = min(1.0, len(matched_keywords) * 0.25)
        is_relevant = score >= 0.25 or len(post.cleaned_text.split()) >= 3

        return {
            "is_relevant": is_relevant,
            "relevance_score": round(score, 2),
            "matched_keywords": matched_keywords
        }
