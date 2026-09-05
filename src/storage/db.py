"""
DuckDB Relational Data Warehouse Manager.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import duckdb
import json
from datetime import datetime

from src.models.schemas import (
    RawPost,
    AnalyzedInsight,
    OpportunityArea,
    SourcePlatform,
    WishlistMotivation,
    PrimaryBlocker,
    UserSegment
)


class DuckDBManager:
    def __init__(self, db_path: str = "data/discovery_engine.duckdb", read_only: bool = False):
        self.db_path = db_path
        self.read_only = read_only
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = duckdb.connect(self.db_path, read_only=read_only)
        if not read_only:
            self._init_tables()


    def _init_tables(self) -> None:
        """Create relational tables if they do not exist."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS raw_posts (
                post_id VARCHAR PRIMARY KEY,
                source_platform VARCHAR NOT NULL,
                author_hash VARCHAR NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                raw_text VARCHAR NOT NULL,
                cleaned_text VARCHAR NOT NULL,
                upvotes INTEGER DEFAULT 0,
                replies INTEGER DEFAULT 0,
                url VARCHAR
            );
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS analyzed_insights (
                insight_id VARCHAR PRIMARY KEY,
                post_id VARCHAR NOT NULL,
                wishlist_motivation VARCHAR NOT NULL,
                intent_score DOUBLE NOT NULL,
                primary_blocker VARCHAR NOT NULL,
                secondary_blockers VARCHAR,
                external_validation_channel VARCHAR,
                user_segment VARCHAR NOT NULL,
                extracted_quotes VARCHAR,
                confidence_score DOUBLE NOT NULL,
                FOREIGN KEY (post_id) REFERENCES raw_posts(post_id)
            );
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS opportunity_areas (
                opportunity_id VARCHAR PRIMARY KEY,
                title VARCHAR NOT NULL,
                primary_blocker VARCHAR NOT NULL,
                frequency_count INTEGER NOT NULL,
                avg_intent_score DOUBLE NOT NULL,
                severity_weight DOUBLE NOT NULL,
                opportunity_score DOUBLE NOT NULL,
                sample_quotes VARCHAR,
                prioritization_level VARCHAR NOT NULL
            );
        """)

    def insert_raw_post(self, post: RawPost) -> None:
        """Insert a single RawPost into raw_posts table."""
        self.conn.execute("""
            INSERT OR REPLACE INTO raw_posts (
                post_id, source_platform, author_hash, timestamp,
                raw_text, cleaned_text, upvotes, replies, url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, [
            post.post_id,
            post.source_platform.value if isinstance(post.source_platform, SourcePlatform) else str(post.source_platform),
            post.author_hash,
            post.timestamp,
            post.raw_text,
            post.cleaned_text,
            post.upvotes,
            post.replies,
            post.url
        ])

    def insert_analyzed_insight(self, insight: AnalyzedInsight) -> None:
        """Insert a single AnalyzedInsight into analyzed_insights table."""
        self.conn.execute("""
            INSERT OR REPLACE INTO analyzed_insights (
                insight_id, post_id, wishlist_motivation, intent_score,
                primary_blocker, secondary_blockers, external_validation_channel,
                user_segment, extracted_quotes, confidence_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, [
            insight.insight_id,
            insight.post_id,
            insight.wishlist_motivation.value if isinstance(insight.wishlist_motivation, WishlistMotivation) else str(insight.wishlist_motivation),
            insight.intent_score,
            insight.primary_blocker.value if isinstance(insight.primary_blocker, PrimaryBlocker) else str(insight.primary_blocker),
            json.dumps([b.value if isinstance(b, PrimaryBlocker) else str(b) for b in insight.secondary_blockers]),
            insight.external_validation_channel,
            insight.user_segment.value if isinstance(insight.user_segment, UserSegment) else str(insight.user_segment),
            json.dumps(insight.extracted_quotes),
            insight.confidence_score
        ])

    def insert_opportunity_area(self, opp: OpportunityArea) -> None:
        """Insert or replace an OpportunityArea in opportunity_areas table."""
        self.conn.execute("""
            INSERT OR REPLACE INTO opportunity_areas (
                opportunity_id, title, primary_blocker, frequency_count,
                avg_intent_score, severity_weight, opportunity_score,
                sample_quotes, prioritization_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, [
            opp.opportunity_id,
            opp.title,
            opp.primary_blocker.value if isinstance(opp.primary_blocker, PrimaryBlocker) else str(opp.primary_blocker),
            opp.frequency_count,
            opp.avg_intent_score,
            opp.severity_weight,
            opp.opportunity_score,
            json.dumps(opp.sample_quotes),
            opp.prioritization_level
        ])

    def get_raw_post(self, post_id: str) -> Optional[RawPost]:
        """Fetch a single RawPost by post_id."""
        rel = self.conn.execute("SELECT * FROM raw_posts WHERE post_id = ?", [post_id]).fetchone()
        if not rel:
            return None
        return RawPost(
            post_id=rel[0],
            source_platform=SourcePlatform(rel[1]),
            author_hash=rel[2],
            timestamp=rel[3],
            raw_text=rel[4],
            cleaned_text=rel[5],
            upvotes=rel[6],
            replies=rel[7],
            url=rel[8]
        )

    def get_all_raw_posts(self) -> List[RawPost]:
        """Retrieve all raw posts."""
        rows = self.conn.execute("SELECT * FROM raw_posts").fetchall()
        posts = []
        for rel in rows:
            posts.append(RawPost(
                post_id=rel[0],
                source_platform=SourcePlatform(rel[1]),
                author_hash=rel[2],
                timestamp=rel[3],
                raw_text=rel[4],
                cleaned_text=rel[5],
                upvotes=rel[6],
                replies=rel[7],
                url=rel[8]
            ))
        return posts

    def get_insight_by_id(self, insight_id: str) -> Optional[AnalyzedInsight]:
        """Fetch a single AnalyzedInsight by insight_id."""
        rel = self.conn.execute("SELECT * FROM analyzed_insights WHERE insight_id = ?", [insight_id]).fetchone()
        if not rel:
            return None
        return AnalyzedInsight(
            insight_id=rel[0],
            post_id=rel[1],
            wishlist_motivation=WishlistMotivation(rel[2]),
            intent_score=rel[3],
            primary_blocker=PrimaryBlocker(rel[4]),
            secondary_blockers=[PrimaryBlocker(b) for b in json.loads(rel[5] or "[]")],
            external_validation_channel=rel[6],
            user_segment=UserSegment(rel[7]),
            extracted_quotes=json.loads(rel[8] or "[]"),
            confidence_score=rel[9]
        )

    def get_all_analyzed_insights(self) -> List[AnalyzedInsight]:
        """Retrieve all analyzed insights."""
        rows = self.conn.execute("SELECT * FROM analyzed_insights").fetchall()
        insights = []
        for rel in rows:
            insights.append(AnalyzedInsight(
                insight_id=rel[0],
                post_id=rel[1],
                wishlist_motivation=WishlistMotivation(rel[2]),
                intent_score=rel[3],
                primary_blocker=PrimaryBlocker(rel[4]),
                secondary_blockers=[PrimaryBlocker(b) for b in json.loads(rel[5] or "[]")],
                external_validation_channel=rel[6],
                user_segment=UserSegment(rel[7]),
                extracted_quotes=json.loads(rel[8] or "[]"),
                confidence_score=rel[9]
            ))
        return insights

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()


