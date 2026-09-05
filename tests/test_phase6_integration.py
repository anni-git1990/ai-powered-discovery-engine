"""
Unit tests for Phase 6: PII Security Auditor, Processing Cache, and Integration CLI.
"""
from datetime import datetime, timezone
import pytest
from argparse import Namespace

from src.models.schemas import RawPost, SourcePlatform
from src.storage.db import DuckDBManager
from src.storage.vector_store import VectorStoreManager
from src.utils.security_audit import PIIAuditor
from src.utils.cache import ProcessingCache
from src.cli import run_pipeline_cmd, export_report_cmd, audit_pii_cmd


def test_pii_security_auditor_passes_clean_data():
    db = DuckDBManager(db_path=":memory:")
    clean_post = RawPost(
        post_id="clean_01",
        source_platform=SourcePlatform.PLAY_STORE,
        author_hash="hash01",
        timestamp=datetime.now(timezone.utc),
        raw_text="Size fit issue on Myntra",
        cleaned_text="Size fit issue on Myntra Contact at [REDACTED_PHONE]"
    )
    db.insert_raw_post(clean_post)

    auditor = PIIAuditor(db_manager=db)
    res = auditor.run_audit()

    assert res["status"] == "PASSED"
    assert res["pii_violations_found"] == 0
    db.close()


def test_processing_cache_hits_and_misses():
    cache = ProcessingCache()

    assert cache.get("Size M issue") is None
    assert cache.stats()["misses"] == 1

    cache.set("Size M issue", {"intent": 0.8})
    cached_val = cache.get("Size M issue")

    assert cached_val == {"intent": 0.8}
    assert cache.stats()["hits"] == 1


def test_cli_integration_pipeline_execution(tmp_path):
    db_file = str(tmp_path / "test_cli.duckdb")
    chroma_dir = str(tmp_path / "test_chroma")
    report_file = str(tmp_path / "test_report.md")

    # 1. Run Pipeline CLI Command
    args_run = Namespace(db_path=db_file, chroma_path=chroma_dir, limit=3)
    run_pipeline_cmd(args_run)

    # 2. Audit PII CLI Command
    args_audit = Namespace(db_path=db_file)
    audit_pii_cmd(args_audit)

    # 3. Export Report CLI Command
    args_export = Namespace(db_path=db_file, chroma_path=chroma_dir, output=report_file)
    export_report_cmd(args_export)

    assert (tmp_path / "test_report.md").exists()
    content = (tmp_path / "test_report.md").read_text(encoding="utf-8")
    assert "Myntra Wishlist Intelligence Report: 2026" in content
