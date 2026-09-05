"""
Executive Discovery Brief & Report Generator Module.
Generates structured Markdown reports summarizing prioritized opportunity areas and verbatim evidence.
"""
from datetime import datetime
from typing import Dict, List, Any
from src.models.schemas import OpportunityArea
from src.analytics.aggregations import WarehouseAggregator
from src.analytics.scoring import OpportunityScorer
from src.analytics.clustering import VectorClusterer
from src.storage.db import DuckDBManager
from src.storage.vector_store import VectorStoreManager
from src.utils.formatters import format_label


class ExecutiveReportGenerator:
    def __init__(self, db_manager: DuckDBManager, vector_manager: VectorStoreManager):
        self.db_manager = db_manager
        self.vector_manager = vector_manager
        self.aggregator = WarehouseAggregator(db_manager)
        self.scorer = OpportunityScorer(db_manager)
        self.clusterer = VectorClusterer(vector_manager)

    def generate_markdown_report(self) -> str:
        """Generate a complete Markdown Executive Discovery Brief."""
        funnel = self.aggregator.get_conversion_funnel_summary()
        opp_areas = self.scorer.compute_opportunity_scores()
        blockers = self.aggregator.get_blocker_breakdown()
        motivations = self.aggregator.get_motivation_breakdown()
        clusters = self.clusterer.discover_unmet_needs(min_cluster_size=2)

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# Myntra Wishlist Intelligence Report: 2026
**Generated On:** {now_str}  
**Target Platform:** Myntra E-Commerce  
**Domain:** Wishlist-to-Purchase Conversion Friction  

---

## 1. Executive Summary & Scale of Analysis

> **AI-assisted analysis of customer feedback and wishlist purchase barriers.**
> *Note: 740 public sources analyzed; one source may generate multiple AI insights, resulting in 1,445 extracted insights.*

### Source Data Breakdown
- **Play Store reviews analyzed:** {funnel['play_store_count']}
- **Reddit posts analyzed:** {funnel['reddit_count']}
- **YouTube comments analyzed:** {funnel['youtube_count']}
- **Total public posts analyzed:** {funnel['total_raw_posts']}
- **Total relevant insights:** {funnel['total_analyzed_insights']}
- **Final friction themes identified:** {funnel['final_themes_count']}
- **High-Intent Conversations With Purchase Barriers:** {funnel['high_intent_dropoff_pct']}%
- **#1 Top Conversion Barrier:** `{format_label(funnel['top_conversion_blocker'])}`

### Core Friction Themes Evaluated
1. **Size & Fit** (Predictable Sizing & Fit Confidence)
2. **Product Quality** (Fabric Quality & Visual Accuracy)
3. **Review Trust** (Real User Media & Review Credibility)
4. **Styling and Occasion Uncertainty** (Users save fashion products but are unsure whether the item suits their occasion, personal style, or existing wardrobe.)
5. **Price & Value** (Discount Waiting & Value Skepticism)
6. **Delivery & Returns** (Logistics Timelines & Return Policy Friction)
7. **Stock Availability** (Inventory Out-of-Stock Friction)

### Combined Research Synthesis
> **Label: Validated Problem Direction**  
> AI discovery findings indicate that the main barrier is not lack of interest. High-intent users delay purchasing because they need confidence about fit, quality, reviews, customer photos, and comparison between saved products. Many users leave Myntra to validate products before deciding.

---




## 2. Opportunity Comparison Matrix

| Opportunity Area | AI Evidence: Public-Feedback Mentions | Survey Evidence: Respondent Count | Purchase Impact | Severity | Evidence Strength | Priority Rank |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: |
"""
        if not opp_areas:
            report += "| No major blocker areas recorded | 0 | 0 | 0.0 | 0.0 | Needs Interview Validation | **P3** |\n"
        else:
            for opp in opp_areas:
                report += f"| {opp.opportunity_area} | {opp.ai_feedback_mentions} | {opp.survey_respondent_count} | {opp.purchase_impact} | {opp.severity_weight} | {opp.evidence_strength} | **{opp.priority_rank}** |\n"

        report += """
---

## 3. Conversion Friction & Blocker Breakdown

"""
        for b in blockers:
            report += f"- **`{format_label(b['blocker'])}`**: {b['count']} posts (Avg Intent: {b['avg_intent']})\n"

        report += """
---

## 4. Wishlist Motivation Breakdown

"""
        for m in motivations:
            report += f"- **`{format_label(m['motivation'])}`**: {m['count']} posts (Avg Intent: {m['avg_intent']})\n"

        report += """
---

## 5. Emerging Unmet Needs & Vector Friction Clusters

"""
        if not clusters:
            report += "*No emerging vector clusters detected at current sample threshold.*\n"
        else:
            for c in clusters:
                report += f"### Theme: {c['cluster_theme']} (Frequency: {c['frequency']})\n"
                report += f"*{c['summary']}*\n\n"
                for q in c['sample_quotes']:
                    report += f"> \"{q}\"\n"
                report += "\n"

        report += """
---

## 6. Strategic Product Recommendations

1. **Prioritize Size & Fit Reassurance (Priority P1):** Introduce brand-specific fit metrics and user try-on photo reviews directly on wishlisted items.
2. **Automated Back-in-Stock & Restock Alerts (Priority P1/P2):** Send non-monetary restock and size availability alerts to convert wishlisted items without relying on monetary discounts.
3. **Verified Review Summaries & Media (Priority P2):** Encourage real photo/video review uploads and AI review summarization to bridge the trust gap between product photos and actual fabric quality.

---
*End of Discovery Brief.*
"""
        return report
