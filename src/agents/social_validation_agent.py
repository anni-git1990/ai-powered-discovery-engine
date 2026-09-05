"""
Social Validation & External Research Agent.
Detects off-platform research behaviors (YouTube, Instagram, Reddit, cross-platform price checks).
"""
from typing import Any, Dict, Optional
from src.agents.base_agent import BaseAgent
from src.models.schemas import RawPost


class SocialValidationAgent(BaseAgent):
    def process(self, post: RawPost) -> Dict[str, Any]:
        """Identify external validation channels mentioned in post."""
        text = post.cleaned_text.lower()
        channel: Optional[str] = None

        if "youtube" in text or "video" in text or "haul" in text or "try-on" in text:
            channel = "YOUTUBE_HAUL_SEARCH"
        elif "instagram" in text or "reel" in text or "influencer" in text:
            channel = "INSTAGRAM_LOOKUP"
        elif "reddit" in text or "subreddit" in text or "thread" in text:
            channel = "REDDIT_ADVICE"
        elif "amazon" in text or "flipkart" in text or "brand site" in text:
            channel = "CROSS_PLATFORM_PRICE_CHECK"

        return {
            "external_validation_channel": channel
        }
