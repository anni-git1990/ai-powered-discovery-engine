"""
Backend REST API Service using FastAPI.
Provides HTTP API endpoints for frontend consumption, programmatic queries, and Swagger UI documentation.
"""
from typing import Any, Dict, List
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from src.ingestion.pipeline import IngestionPipeline
from src.agents.orchestrator import AgentOrchestrator
from src.storage.db import DuckDBManager
from src.storage.vector_store import VectorStoreManager
from src.analytics.aggregations import WarehouseAggregator
from src.analytics.scoring import OpportunityScorer
from src.analytics.clustering import VectorClusterer
from src.dashboard.report_generator import ExecutiveReportGenerator

app = FastAPI(
    title="Myntra Wishlist Discovery Engine REST API",
    description="Backend API service for analyzing fashion wishlist-to-purchase behavior, conversion blockers, and opportunity metrics.",
    version="1.0.0"
)

# Enable CORS for external frontend frameworks (e.g. Next.js / React / Vue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    return DuckDBManager(db_path=":memory:")


def get_vector_store():
    return VectorStoreManager(persist_directory=":memory:", collection_name="api_collection")


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "service": "AI-Powered Discovery Engine Backend API",
        "version": "1.0.0",
        "docs_url": "http://localhost:8000/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


@app.get("/api/funnel", tags=["Analytics"])
def get_funnel_metrics():
    db = get_db()
    vs = get_vector_store()
    pipeline = IngestionPipeline(db_manager=db, vector_manager=vs)
    pipeline.run(limit_per_source=100)
    orchestrator = AgentOrchestrator(db_manager=db)
    orchestrator.process_batch(db.get_all_raw_posts())

    aggregator = WarehouseAggregator(db)
    summary = aggregator.get_conversion_funnel_summary()
    db.close()
    return summary


@app.get("/api/opportunity-matrix", tags=["Analytics"])
def get_opportunity_matrix():
    db = get_db()
    vs = get_vector_store()
    pipeline = IngestionPipeline(db_manager=db, vector_manager=vs)
    pipeline.run(limit_per_source=100)
    orchestrator = AgentOrchestrator(db_manager=db)
    orchestrator.process_batch(db.get_all_raw_posts())

    scorer = OpportunityScorer(db)
    opps = scorer.compute_opportunity_scores()
    db.close()
    return [opp.model_dump() for opp in opps]


@app.get("/api/blockers", tags=["Analytics"])
def get_blockers_breakdown():
    db = get_db()
    vs = get_vector_store()
    pipeline = IngestionPipeline(db_manager=db, vector_manager=vs)
    pipeline.run(limit_per_source=100)
    orchestrator = AgentOrchestrator(db_manager=db)
    orchestrator.process_batch(db.get_all_raw_posts())

    aggregator = WarehouseAggregator(db)
    breakdown = aggregator.get_blocker_breakdown()
    db.close()
    return breakdown


@app.get("/api/insights", tags=["Insights"])
def get_insights(min_intent: float = Query(0.0, ge=0.0, le=1.0)):
    db = get_db()
    vs = get_vector_store()
    pipeline = IngestionPipeline(db_manager=db, vector_manager=vs)
    pipeline.run(limit_per_source=100)
    orchestrator = AgentOrchestrator(db_manager=db)
    orchestrator.process_batch(db.get_all_raw_posts())

    query_sql = f"""
        SELECT p.source_platform, i.wishlist_motivation, i.intent_score, 
               i.primary_blocker, i.user_segment, p.cleaned_text
        FROM raw_posts p
        JOIN analyzed_insights i ON p.post_id = i.post_id
        WHERE i.intent_score >= {min_intent}
    """
    rows = db.conn.execute(query_sql).fetchall()
    insights_list = []
    for r in rows:
        insights_list.append({
            "source_platform": r[0],
            "wishlist_motivation": r[1],
            "intent_score": r[2],
            "primary_blocker": r[3],
            "user_segment": r[4],
            "sanitized_text": r[5]
        })
    db.close()
    return insights_list
