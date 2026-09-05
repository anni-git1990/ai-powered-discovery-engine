"""
Multi-Agent Orchestrator & Insight Synthesizer.
Coordinates execution across specialized agents and produces validated AnalyzedInsight outputs.
"""
import uuid
from typing import List, Optional
from src.agents.triage_agent import TriageAgent
from src.agents.motivation_agent import MotivationAgent
from src.agents.blocker_agent import BlockerAgent
from src.agents.social_validation_agent import SocialValidationAgent
from src.agents.segmentation_agent import SegmentationAgent
from src.models.schemas import RawPost, AnalyzedInsight
from src.storage.db import DuckDBManager


class AgentOrchestrator:
    def __init__(self, db_manager: Optional[DuckDBManager] = None):
        self.triage_agent = TriageAgent()
        self.motivation_agent = MotivationAgent()
        self.blocker_agent = BlockerAgent()
        self.social_agent = SocialValidationAgent()
        self.segmentation_agent = SegmentationAgent()
        self.db_manager = db_manager

    def process_post(self, post: RawPost) -> Optional[AnalyzedInsight]:
        """Run multi-agent classification pipeline on a single RawPost."""
        # 1. Triage Check
        triage_res = self.triage_agent.process(post)
        if not triage_res["is_relevant"]:
            return None

        # 2. Run Parallel / Sub-agent Processors
        motivation_res = self.motivation_agent.process(post)
        blocker_res = self.blocker_agent.process(post)
        social_res = self.social_agent.process(post)
        segment_res = self.segmentation_agent.process(post)

        # 3. Synthesize AnalyzedInsight Payload
        insight_id = f"insight_{uuid.uuid4().hex[:8]}"
        insight = AnalyzedInsight(
            insight_id=insight_id,
            post_id=post.post_id,
            wishlist_motivation=motivation_res["wishlist_motivation"],
            intent_score=motivation_res["intent_score"],
            primary_blocker=blocker_res["primary_blocker"],
            secondary_blockers=blocker_res["secondary_blockers"],
            external_validation_channel=social_res["external_validation_channel"],
            user_segment=segment_res["user_segment"],
            extracted_quotes=blocker_res["extracted_quotes"],
            confidence_score=round(triage_res["relevance_score"], 2)
        )

        # 4. Save to Database if db_manager provided
        if self.db_manager is not None:
            self.db_manager.insert_analyzed_insight(insight)

        return insight

    def process_batch(self, posts: List[RawPost]) -> List[AnalyzedInsight]:
        """Process a list of raw posts and return analyzed insights."""
        insights: List[AnalyzedInsight] = []
        for post in posts:
            res = self.process_post(post)
            if res is not None:
                insights.append(res)
        return insights
