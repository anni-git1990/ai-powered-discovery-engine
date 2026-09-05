"""
Data Warehouse Aggregation Queries Module.
Extracts statistical metrics, distributions, and conversion funnel breakdowns from DuckDB.
"""
from typing import Any, Dict, List
from src.storage.db import DuckDBManager


class WarehouseAggregator:
    def __init__(self, db_manager: DuckDBManager):
        self.db_manager = db_manager

    def get_motivation_breakdown(self) -> List[Dict[str, Any]]:
        """Distribution of wishlist motivations across analyzed posts."""
        query = """
            SELECT 
                wishlist_motivation,
                COUNT(insight_id) AS count,
                ROUND(AVG(intent_score), 2) AS avg_intent
            FROM analyzed_insights
            GROUP BY wishlist_motivation
            ORDER BY count DESC;
        """
        rows = self.db_manager.conn.execute(query).fetchall()
        return [{"motivation": r[0], "count": r[1], "avg_intent": r[2]} for r in rows]

    def get_blocker_breakdown(self) -> List[Dict[str, Any]]:
        """Distribution of conversion blockers."""
        query = """
            SELECT 
                primary_blocker,
                COUNT(insight_id) AS count,
                ROUND(AVG(intent_score), 2) AS avg_intent
            FROM analyzed_insights
            GROUP BY primary_blocker
            ORDER BY count DESC;
        """
        rows = self.db_manager.conn.execute(query).fetchall()
        return [{"blocker": r[0], "count": r[1], "avg_intent": r[2]} for r in rows]

    def get_segment_breakdown(self) -> List[Dict[str, Any]]:
        """Distribution of user personas."""
        query = """
            SELECT 
                user_segment,
                COUNT(insight_id) AS count,
                ROUND(AVG(intent_score), 2) AS avg_intent
            FROM analyzed_insights
            GROUP BY user_segment
            ORDER BY count DESC;
        """
        rows = self.db_manager.conn.execute(query).fetchall()
        return [{"user_segment": r[0], "count": r[1], "avg_intent": r[2]} for r in rows]

    def get_platform_breakdown(self) -> List[Dict[str, Any]]:
        """Cross-platform review volume comparison."""
        query = """
            SELECT 
                p.source_platform,
                COUNT(p.post_id) AS total_posts,
                COUNT(i.insight_id) AS analyzed_insights
            FROM raw_posts p
            LEFT JOIN analyzed_insights i ON p.post_id = i.post_id
            GROUP BY p.source_platform
            ORDER BY total_posts DESC;
        """
        rows = self.db_manager.conn.execute(query).fetchall()
        return [{"platform": r[0], "total_posts": r[1], "analyzed_insights": r[2]} for r in rows]

    def get_conversion_funnel_summary(self) -> Dict[str, Any]:
        """Executive summary metrics for discovery dashboard including source platform breakdown."""
        total_posts_res = self.db_manager.conn.execute("SELECT COUNT(*) FROM raw_posts").fetchone()
        total_insights_res = self.db_manager.conn.execute("SELECT COUNT(*) FROM analyzed_insights").fetchone()
        play_store_res = self.db_manager.conn.execute("SELECT COUNT(*) FROM raw_posts WHERE source_platform IN ('PLAY_STORE', 'APP_STORE')").fetchone()
        reddit_res = self.db_manager.conn.execute("SELECT COUNT(*) FROM raw_posts WHERE source_platform = 'REDDIT'").fetchone()
        youtube_res = self.db_manager.conn.execute("SELECT COUNT(*) FROM raw_posts WHERE source_platform = 'YOUTUBE'").fetchone()
        themes_res = self.db_manager.conn.execute("SELECT COUNT(DISTINCT primary_blocker) FROM analyzed_insights WHERE primary_blocker != 'NONE'").fetchone()
        high_intent_res = self.db_manager.conn.execute("SELECT COUNT(*) FROM analyzed_insights WHERE intent_score >= 0.70").fetchone()
        top_blocker_res = self.db_manager.conn.execute("""
            SELECT primary_blocker, COUNT(*) AS cnt 
            FROM analyzed_insights 
            WHERE primary_blocker != 'NONE'
            GROUP BY primary_blocker 
            ORDER BY cnt DESC LIMIT 1;
        """).fetchone()

        total_posts = total_posts_res[0] if total_posts_res else 0
        total_insights = total_insights_res[0] if total_insights_res else 0
        play_store_count = play_store_res[0] if play_store_res else 0
        reddit_count = reddit_res[0] if reddit_res else 0
        youtube_count = youtube_res[0] if youtube_res else 0
        final_themes_count = themes_res[0] if themes_res else 0
        high_intent_count = high_intent_res[0] if high_intent_res else 0
        high_intent_dropoff_pct = round((high_intent_count / total_insights * 100), 1) if total_insights > 0 else 0.0
        top_blocker = top_blocker_res[0] if top_blocker_res else "NONE"

        return {
            "total_raw_posts": total_posts,
            "total_analyzed_insights": total_insights,
            "play_store_count": play_store_count,
            "reddit_count": reddit_count,
            "youtube_count": youtube_count,
            "final_themes_count": final_themes_count,
            "high_intent_count": high_intent_count,
            "high_intent_dropoff_pct": high_intent_dropoff_pct,
            "top_conversion_blocker": top_blocker
        }

