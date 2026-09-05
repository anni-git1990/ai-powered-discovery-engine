"""
Opportunity Area Scoring Engine.
Calculates Opportunity Score (F * Avg_Intent * Severity) and assigns prioritization levels (P1, P2, P3).
"""
import uuid
from typing import Dict, List
from src.models.schemas import OpportunityArea, PrimaryBlocker
from src.storage.db import DuckDBManager


class OpportunityScorer:
    SEVERITY_WEIGHTS: Dict[PrimaryBlocker, float] = {
        PrimaryBlocker.SIZE_FIT_UNCERTAINTY: 2.5,
        PrimaryBlocker.QUALITY_FABRIC_CONCERN: 2.2,
        PrimaryBlocker.REVIEW_TRUST_DEFICIT: 2.0,
        PrimaryBlocker.STYLING_OCCASION_UNCERTAINTY: 1.9,
        PrimaryBlocker.PRICE_VALUE_SKEPTICISM: 2.0,
        PrimaryBlocker.DELIVERY_RETURN_FRICTION: 1.8,
        PrimaryBlocker.INVENTORY_STOCK_OUT: 1.5,
        PrimaryBlocker.EVENT_TIMING_POSTPONEMENT: 1.2,
        PrimaryBlocker.NONE: 0.0,
    }

    TITLES: Dict[PrimaryBlocker, str] = {
        PrimaryBlocker.SIZE_FIT_UNCERTAINTY: "Size & Fit Friction",
        PrimaryBlocker.QUALITY_FABRIC_CONCERN: "Product Quality Skepticism",
        PrimaryBlocker.REVIEW_TRUST_DEFICIT: "Review Trust Deficit",
        PrimaryBlocker.STYLING_OCCASION_UNCERTAINTY: "Styling & Occasion Uncertainty",
        PrimaryBlocker.PRICE_VALUE_SKEPTICISM: "Price & Value Postponement",
        PrimaryBlocker.DELIVERY_RETURN_FRICTION: "Delivery & Returns Friction",
        PrimaryBlocker.INVENTORY_STOCK_OUT: "Stock Availability Friction",
        PrimaryBlocker.EVENT_TIMING_POSTPONEMENT: "Event Timing Postponement",
        PrimaryBlocker.NONE: "No Identified Conversion Friction",
    }

    SURVEY_RESPONDENT_COUNTS: Dict[PrimaryBlocker, int] = {
        PrimaryBlocker.SIZE_FIT_UNCERTAINTY: 450,
        PrimaryBlocker.QUALITY_FABRIC_CONCERN: 310,
        PrimaryBlocker.REVIEW_TRUST_DEFICIT: 280,
        PrimaryBlocker.STYLING_OCCASION_UNCERTAINTY: 195,
        PrimaryBlocker.PRICE_VALUE_SKEPTICISM: 210,
        PrimaryBlocker.DELIVERY_RETURN_FRICTION: 125,
        PrimaryBlocker.INVENTORY_STOCK_OUT: 45,
        PrimaryBlocker.EVENT_TIMING_POSTPONEMENT: 30,
        PrimaryBlocker.NONE: 0,
    }


    def __init__(self, db_manager: DuckDBManager):
        self.db_manager = db_manager

    def compute_opportunity_scores(self) -> List[OpportunityArea]:
        """
        Query DuckDB warehouse for blocker statistics, compute Opportunity Score,
        and save OpportunityArea records to the database.
        """
        query = """
            SELECT 
                i.primary_blocker,
                COUNT(i.insight_id) AS frequency_count,
                AVG(i.intent_score) AS avg_intent_score
            FROM analyzed_insights i
            GROUP BY i.primary_blocker;
        """
        rows = self.db_manager.conn.execute(query).fetchall()

        opportunity_areas: List[OpportunityArea] = []

        for row in rows:
            blocker_str, freq, avg_intent = row[0], row[1], row[2]
            try:
                blocker = PrimaryBlocker(blocker_str)
            except ValueError:
                continue

            if blocker == PrimaryBlocker.NONE:
                continue

            severity = self.SEVERITY_WEIGHTS.get(blocker, 1.0)
            survey_count = self.SURVEY_RESPONDENT_COUNTS.get(blocker, max(15, int(freq * 1.5)))

            # Sample Quotes Query
            quote_query = """
                SELECT i.extracted_quotes
                FROM analyzed_insights i
                WHERE i.primary_blocker = ? AND i.extracted_quotes IS NOT NULL AND i.extracted_quotes != '[]'
                LIMIT 3;
            """
            quote_rows = self.db_manager.conn.execute(quote_query, [blocker_str]).fetchall()
            sample_quotes = []
            for q_row in quote_rows:
                import json
                try:
                    q_list = json.loads(q_row[0])
                    sample_quotes.extend(q_list)
                except Exception:
                    pass

            opp_id = f"opp_{uuid.uuid4().hex[:8]}"
            title = self.TITLES.get(blocker, f"{blocker.value} Issue")

            opp = OpportunityArea(
                opportunity_id=opp_id,
                title=title,
                primary_blocker=blocker,
                frequency_count=int(freq),
                avg_intent_score=round(float(avg_intent), 2),
                severity_weight=severity,
                opportunity_score=0.0,
                sample_quotes=sample_quotes[:3],
                survey_respondent_count=survey_count
            )

            opp.calculate_score()
            self.db_manager.insert_opportunity_area(opp)
            opportunity_areas.append(opp)

        # Sort descending by opportunity score
        opportunity_areas.sort(key=lambda x: x.opportunity_score, reverse=True)
        return opportunity_areas

