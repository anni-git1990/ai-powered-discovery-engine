"""
Unified Command-Line Interface (CLI) for AI-Powered Discovery Engine.
"""
import argparse
import sys
from pathlib import Path

# Ensure stdout handles UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure root directory is on PYTHONPATH
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.ingestion.pipeline import IngestionPipeline
from src.agents.orchestrator import AgentOrchestrator
from src.analytics.scoring import OpportunityScorer
from src.dashboard.report_generator import ExecutiveReportGenerator
from src.storage.db import DuckDBManager
from src.storage.vector_store import VectorStoreManager
from src.utils.security_audit import PIIAuditor


def run_pipeline_cmd(args):
    print("\n🚀 Starting End-to-End Discovery Engine Pipeline...")
    db_path = args.db_path
    db = DuckDBManager(db_path=db_path)
    vs = VectorStoreManager(persist_directory=args.chroma_path)

    # Step 1: Ingestion & Preprocessing
    print("\n[1/3] Ingesting multi-source public reviews & scrubbing PII...")
    pipeline = IngestionPipeline(db_manager=db, vector_manager=vs)
    processed, dupes = pipeline.run(limit_per_source=args.limit)
    print(f"      -> Ingested: {processed} posts | Duplicates Skipped: {dupes}")

    # Step 2: Multi-Agent AI Processing
    print("\n[2/3] Executing Multi-Agent AI Engine (Intent, Blocker, Persona Classification)...")
    orchestrator = AgentOrchestrator(db_manager=db)
    raw_posts = db.get_all_raw_posts()
    insights = orchestrator.process_batch(raw_posts)
    print(f"      -> Generated {len(insights)} Analyzed Insights")

    # Step 3: Analytics & Opportunity Scoring
    print("\n[3/3] Calculating Opportunity Scores (F * Avg_Intent * Severity)...")
    scorer = OpportunityScorer(db_manager=db)
    opps = scorer.compute_opportunity_scores()
    print(f"      -> Calculated {len(opps)} Prioritized Opportunity Areas")

    for o in opps:
        print(f"         [{o.prioritization_level}] {o.title} (Score: {o.opportunity_score})")

    db.close()
    print("\n✅ End-to-End Pipeline Execution Completed Successfully!\n")


def export_report_cmd(args):
    print("\n📄 Generating Executive Discovery Brief...")
    db = DuckDBManager(db_path=args.db_path)
    vs = VectorStoreManager(persist_directory=args.chroma_path)

    report_gen = ExecutiveReportGenerator(db, vs)
    markdown_report = report_gen.generate_markdown_report()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_report)

    print(f"✅ Report saved to: {output_path.resolve()}\n")
    db.close()


def audit_pii_cmd(args):
    print("\n🔒 Running Security & Privacy PII Audit...")
    db = DuckDBManager(db_path=args.db_path)
    auditor = PIIAuditor(db_manager=db)
    res = auditor.run_audit()

    print(f"      -> Status: {res['status']}")
    print(f"      -> Scanned: {res['total_records_scanned']} posts")
    print(f"      -> Violations Found: {res['pii_violations_found']}")

    if res['pii_violations_found'] == 0:
        print("✅ PII Audit Passed Cleanly! Zero unscrubbed PII leaks detected.\n")
    else:
        print("❌ PII Audit Failed! Violations detected.")
        sys.exit(1)

    db.close()


def main():
    parser = argparse.ArgumentParser(description="AI-Powered Discovery Engine CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Subcommand: run-pipeline
    p_pipe = subparsers.add_parser("run-pipeline", help="Run full discovery pipeline")
    p_pipe.add_argument("--db-path", default="data/discovery_engine.duckdb", help="Path to DuckDB database")
    p_pipe.add_argument("--chroma-path", default="data/chroma_db", help="Path to ChromaDB vector store")
    p_pipe.add_argument("--limit", type=int, default=20, help="Posts limit per source")

    # Subcommand: export-report
    p_rep = subparsers.add_parser("export-report", help="Export Executive Discovery Report")
    p_rep.add_argument("--db-path", default="data/discovery_engine.duckdb", help="Path to DuckDB database")
    p_rep.add_argument("--chroma-path", default="data/chroma_db", help="Path to ChromaDB vector store")
    p_rep.add_argument("--output", default="reports/executive_discovery_brief.md", help="Output markdown path")

    # Subcommand: audit-pii
    p_audit = subparsers.add_parser("audit-pii", help="Run PII security compliance audit")
    p_audit.add_argument("--db-path", default="data/discovery_engine.duckdb", help="Path to DuckDB database")

    args = parser.parse_args()

    if args.command == "run-pipeline":
        run_pipeline_cmd(args)
    elif args.command == "export-report":
        export_report_cmd(args)
    elif args.command == "audit-pii":
        audit_pii_cmd(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
