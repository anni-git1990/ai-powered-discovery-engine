"""
Script to ingest sample reviews, run multi-agent AI classification, and display results.
"""
from src.ingestion.pipeline import IngestionPipeline
from src.agents.orchestrator import AgentOrchestrator
from src.storage.db import DuckDBManager
from src.storage.vector_store import VectorStoreManager


def main():
    print("================================================================================")
    print("          AI-POWERED DISCOVERY ENGINE - REVIEWS & INSIGHTS INSPECTOR           ")
    print("================================================================================\n")

    # 1. Initialize Storage
    db_manager = DuckDBManager(db_path=":memory:")
    vector_manager = VectorStoreManager(persist_directory=":memory:", collection_name="demo_collection")

    # 2. Run Ingestion & Preprocessing Pipeline
    print("[1/3] Ingesting reviews & applying PII sanitization + slang normalization...")
    pipeline = IngestionPipeline(db_manager=db_manager, vector_manager=vector_manager)
    processed_count, duplicate_count = pipeline.run(limit_per_source=3)

    print(f"      -> Ingested & Processed: {processed_count} posts")
    print(f"      -> Duplicate Posts Skipped: {duplicate_count}\n")

    # 3. Run Multi-Agent AI Processing Engine
    print("[2/3] Running Multi-Agent AI Engine (Intent, Blocker, Persona Classification)...")
    orchestrator = AgentOrchestrator(db_manager=db_manager)
    raw_posts = db_manager.get_all_raw_posts()
    insights = orchestrator.process_batch(raw_posts)
    print(f"      -> Generated {len(insights)} Analyzed Insights\n")

    # 4. Display Formatted Reviews & AI Insights
    print("================================================================================")
    print("                          INGESTED REVIEWS & AI INSIGHTS                        ")
    print("================================================================================\n")

    for idx, (post, insight) in enumerate(zip(raw_posts, insights), 1):
        print(f"--- [Review #{idx}] --- ({post.source_platform.value}) --- ID: {post.post_id}")
        print(f"  • Raw User Input     : {post.raw_text}")
        print(f"  • Sanitized Text     : {post.cleaned_text}")
        print(f"  • Wishlist Motivation: {insight.wishlist_motivation.value} (Intent Score: {insight.intent_score})")
        print(f"  • Primary Blocker    : {insight.primary_blocker.value}")
        if insight.secondary_blockers:
            sec_str = ", ".join([b.value for b in insight.secondary_blockers])
            print(f"  • Secondary Blockers : {sec_str}")
        if insight.external_validation_channel:
            print(f"  • Social Validation  : {insight.external_validation_channel}")
        print(f"  • User Persona       : {insight.user_segment.value}")
        if insight.extracted_quotes:
            print(f"  • Verbatim Quote     : \"{insight.extracted_quotes[0]}\"")
        print()

    db_manager.close()
    print("================================================================================")
    print("Inspection complete! All reviews and insights successfully extracted.")
    print("================================================================================")


if __name__ == "__main__":
    main()
