"""
Purchase Blocker & Friction Extraction Agent.
Extracts primary and secondary purchase blockers along with verbatim quotes.
"""
from typing import Any, Dict, List
import re
from src.agents.base_agent import BaseAgent
from src.models.schemas import RawPost, PrimaryBlocker


class BlockerAgent(BaseAgent):
    def process(self, post: RawPost) -> Dict[str, Any]:
        """Extract conversion blockers and verbatim quotes from user post."""
        text = post.cleaned_text.lower()
        blockers: List[PrimaryBlocker] = []
        quotes: List[str] = []

        # 1. Size & Fit Uncertainty
        if any(k in text for k in ["size", "fit", "fitting", "chota", "bada", "mismatch", "tight", "loose", "true to size"]):
            blockers.append(PrimaryBlocker.SIZE_FIT_UNCERTAINTY)
            quotes.append(post.cleaned_text)

        # 2. Price Value Skepticism
        if any(k in text for k in ["price", "mrp", "discount", "expensive", "inflated", "overpriced", "paisa vasool"]):
            blockers.append(PrimaryBlocker.PRICE_VALUE_SKEPTICISM)
            quotes.append(post.cleaned_text)

        # 3. Quality & Fabric Concern
        if any(k in text for k in ["quality", "fabric", "material", "thin", "cheap", "bakwas", "poor quality"]):
            blockers.append(PrimaryBlocker.QUALITY_FABRIC_CONCERN)
            quotes.append(post.cleaned_text)

        # 4. Review Trust Deficit
        if any(k in text for k in ["review", "photo", "picture", "different in photo", "real video", "try-on"]):
            blockers.append(PrimaryBlocker.REVIEW_TRUST_DEFICIT)
            quotes.append(post.cleaned_text)

        # 5. Delivery & Return Friction
        if any(k in text for k in ["delivery", "return", "exchange", "refund", "timeframe", "days to deliver"]):
            blockers.append(PrimaryBlocker.DELIVERY_RETURN_FRICTION)
            quotes.append(post.cleaned_text)

        # 6. Inventory Stock Out
        if any(k in text for k in ["out of stock", "stock out", "sold out", "unavailable"]):
            blockers.append(PrimaryBlocker.INVENTORY_STOCK_OUT)
            quotes.append(post.cleaned_text)

        # Determine primary and secondary blockers
        if not blockers:
            primary = PrimaryBlocker.NONE
            secondary = []
        else:
            primary = blockers[0]
            secondary = list(set(blockers[1:]))

        return {
            "primary_blocker": primary,
            "secondary_blockers": secondary,
            "extracted_quotes": list(set(quotes))
        }
