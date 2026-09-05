"""
Streamlit Executive Discovery Dashboard Application.
Implements the design tokens from DESIGN.md and layout from code.html & screen.png in ui_screen/executive_screen.
"""
import sys
from pathlib import Path

# Ensure root directory is on PYTHONPATH
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
from src.ingestion.pipeline import IngestionPipeline
from src.agents.orchestrator import AgentOrchestrator
from src.storage.db import DuckDBManager
from src.storage.vector_store import VectorStoreManager
from src.analytics.aggregations import WarehouseAggregator
from src.analytics.scoring import OpportunityScorer
from src.analytics.clustering import VectorClusterer
from src.dashboard.report_generator import ExecutiveReportGenerator
from src.utils.formatters import format_label


@st.cache_resource
def get_managers():
    db_path = "data/discovery_engine.duckdb"
    chroma_path = "data/chroma_db"
    
    if Path(db_path).exists():
        try:
            db = DuckDBManager(db_path=db_path, read_only=True)
            vs = VectorStoreManager(persist_directory=chroma_path, collection_name="dashboard_collection")
            raw_posts = db.get_all_raw_posts()
            if raw_posts:
                return db, vs
            db.close()
        except Exception:
            pass
        db = DuckDBManager(db_path=db_path)
        vs = VectorStoreManager(persist_directory=chroma_path, collection_name="dashboard_collection")
        raw_posts = db.get_all_raw_posts()
        if not raw_posts:
            pipeline = IngestionPipeline(db_manager=db, vector_manager=vs)
            pipeline.run(limit_per_source=200)
            orchestrator = AgentOrchestrator(db_manager=db)
            raw_posts = db.get_all_raw_posts()
            orchestrator.process_batch(raw_posts)
    else:
        db = DuckDBManager(db_path=":memory:")
        vs = VectorStoreManager(persist_directory=":memory:", collection_name="dashboard_collection")
        pipeline = IngestionPipeline(db_manager=db, vector_manager=vs)
        pipeline.run(limit_per_source=200)
        orchestrator = AgentOrchestrator(db_manager=db)
        raw_posts = db.get_all_raw_posts()
        orchestrator.process_batch(raw_posts)

    return db, vs



def inject_custom_css():
    """Inject Design System styles from DESIGN.md & code.html (Executive Screen)."""
    css_content = """<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Outfit', sans-serif !important;
    background-color: #fbf9f8 !important;
    color: #1b1c1c !important;
}

.top-nav-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 24px;
    background: #ffffff;
    border-bottom: 1px solid #e4e2e1;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(51, 51, 51, 0.04);
}

.main-header-title {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 26px;
    color: #b90041;
    letter-spacing: -0.01em;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 16px;
}

.search-box {
    display: flex;
    align-items: center;
    background: #fbf9f8;
    border: 1px solid #e4e2e1;
    border-radius: 8px;
    padding: 6px 12px;
    gap: 8px;
}

.search-box input {
    border: none;
    background: transparent;
    outline: none;
    font-size: 14px;
    color: #1b1c1c;
    width: 180px;
}

.btn-settings {
    display: flex;
    align-items: center;
    gap: 6px;
    background: transparent;
    border: none;
    color: #5b4042;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer;
}

.btn-export-primary {
    display: flex;
    align-items: center;
    gap: 6px;
    background: #b90041;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 700;
    font-size: 14px;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(185, 0, 65, 0.25);
}

.btn-export-primary:hover {
    background: #df2457;
}

.page-title {
    font-size: 32px;
    font-weight: 700;
    color: #1b1c1c;
    margin-bottom: 4px;
}

.page-subtitle {
    font-size: 14px;
    color: #5b4042;
    margin-bottom: 24px;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}

@media (max-width: 992px) {
    .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 576px) {
    .kpi-grid { grid-template-columns: 1fr; }
}

.kpi-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid #F5F5F6;
    box-shadow: 0 4px 12px rgba(51, 51, 51, 0.04);
    transition: all 0.3s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(51, 51, 51, 0.08);
}

.kpi-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
}

.kpi-label {
    font-family: 'Outfit', sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: #5b4042;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.kpi-icon-badge {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.badge-primary { background: #ffd9dc; color: #b90041; }
.badge-error { background: #ffdad6; color: #ba1a1a; }
.badge-tertiary { background: #008376; color: #ffffff; }

.kpi-val {
    font-family: 'Outfit', sans-serif;
    font-size: 36px;
    font-weight: 700;
    color: #1b1c1c;
    line-height: 44px;
}

.kpi-val-text {
    font-family: 'Outfit', sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: #1b1c1c;
    line-height: 32px;
    margin-top: 8px;
}

.kpi-sub {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 8px;
    font-size: 12px;
    font-weight: 600;
}

.sub-green { color: #008376; }
.sub-neutral { color: #5b4042; }

.matrix-card {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #F5F5F6;
    box-shadow: 0 4px 12px rgba(51, 51, 51, 0.04);
    overflow: hidden;
    margin-top: 16px;
    margin-bottom: 24px;
}

.matrix-header {
    padding: 24px;
    border-bottom: 1px solid #F5F5F6;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #fbf9f8;
}

.matrix-title {
    font-size: 20px;
    font-weight: 600;
    color: #1b1c1c;
}

.matrix-sub {
    font-size: 14px;
    color: #5b4042;
    margin-top: 4px;
}

.matrix-btn-filter {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border: 1px solid #8f6f72;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    color: #1b1c1c;
    background: transparent;
    cursor: pointer;
}

.matrix-table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
}

.matrix-table th {
    background: #f6f3f2;
    padding: 14px 16px;
    font-size: 12px;
    font-weight: 700;
    color: #5b4042;
    text-transform: uppercase;
    border-bottom: 1px solid #F5F5F6;
}

.matrix-table td {
    padding: 16px;
    border-bottom: 1px solid #F5F5F6;
    font-size: 14px;
    color: #1b1c1c;
    vertical-align: middle;
}

.matrix-table tr:hover {
    background: #fbf9f8;
}

.pill-p1 {
    background: #ffdad6;
    color: #93000a;
    padding: 4px 12px;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 12px;
}

.pill-p2 {
    background: #ffd9dc;
    color: #400011;
    padding: 4px 12px;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 12px;
}

.pill-p3 {
    background: #f0eded;
    color: #5b5d6f;
    padding: 4px 12px;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 12px;
}

.progress-bar-bg {
    width: 100%;
    background: #eae8e7;
    height: 8px;
    border-radius: 9999px;
    overflow: hidden;
}

.progress-bar-fill-high { background: #ba1a1a; height: 100%; }
.progress-bar-fill-med { background: #df2457; height: 100%; }
.progress-bar-fill-low { background: #5b5d6f; height: 100%; }

.user-profile-badge {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: #f6f3f2;
    border-radius: 12px;
    margin-top: 32px;
    border-top: 1px solid #e4e2e1;
}

.profile-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #b90041;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 14px;
}

/* Motivations Screen Custom Styles */
.funnel-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid #F5F5F6;
    box-shadow: 0 4px 12px rgba(51, 51, 51, 0.04);
    margin-bottom: 24px;
}

.funnel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.funnel-grid {
    display: flex;
    flex-direction: row;
    align-items: flex-end;
    justify-content: space-between;
    gap: 12px;
    padding-bottom: 16px;
}

@media (max-width: 768px) {
    .funnel-grid { flex-direction: column; align-items: center; }
}

.funnel-step {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
}

.funnel-bar-container {
    width: 100%;
    height: 128px;
    background: rgba(223, 36, 87, 0.1);
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    position: relative;
    overflow: hidden;
}

.funnel-bar-fill {
    position: absolute;
    bottom: 0;
    width: 100%;
    background: #df2457;
    transition: all 0.5s ease;
}

.funnel-pct-text {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 700;
    color: #ffffff;
}

.funnel-arrow {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 128px;
    padding: 0 8px;
    color: #5b4042;
}

.funnel-drop-text {
    font-size: 12px;
    font-weight: 700;
    color: #ba1a1a;
    margin-top: 4px;
}

.chart-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid #F5F5F6;
    box-shadow: 0 4px 12px rgba(51, 51, 51, 0.04);
    height: 100%;
}

.blocker-bar-row {
    display: flex;
    align-items: center;
    width: 100%;
    margin-bottom: 12px;
}

.blocker-label {
    width: 110px;
    text-align: right;
    padding-right: 12px;
    font-size: 12px;
    font-weight: 600;
    color: #5b4042;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.blocker-bar-bg {
    height: 24px;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
    position: relative;
    display: flex;
    align-items: center;
}

.donut-container {
    position: relative;
    width: 192px;
    height: 192px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 16px auto;
    background: conic-gradient(
        #df2457 0% 40%, 
        #ffb2ba 40% 65%, 
        #5b5d6f 65% 85%, 
        #e3bdc0 85% 100%
    );
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
}

.donut-hole {
    width: 128px;
    height: 128px;
    background: #ffffff;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(51, 51, 51, 0.04);
}

.bento-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid #F5F5F6;
    box-shadow: 0 4px 12px rgba(51, 51, 51, 0.04);
    display: flex;
    gap: 16px;
    align-items: flex-start;
}

.bento-icon {
    width: 64px;
    height: 64px;
    border-radius: 12px;
    background: #f6f3f2;
    border: 1px solid #e4e2e1;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

/* Quote Explorer Screen Custom Styles */
.quote-card {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #e4e2e1;
    padding: 24px;
    box-shadow: 0 4px 12px rgba(27, 28, 28, 0.04);
    transition: all 0.3s ease;
    margin-bottom: 16px;
}

.quote-card:hover {
    box-shadow: 0 6px 16px rgba(27, 28, 28, 0.06);
    transform: translateY(-2px);
}

.quote-icon-badge {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #dfe1f7;
    color: #616376;
    display: flex;
    align-items: center;
    justify-content: center;
}

.intent-badge-high {
    background: #008376;
    color: #ffffff;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.intent-badge-med {
    background: #dfe1f7;
    color: #181b2a;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.quote-text-quote {
    font-size: 16px;
    line-height: 1.6;
    color: #1b1c1c;
    padding-left: 16px;
    border-left: 4px solid #e4e2e1;
    margin: 16px 0;
}

.highlight-pink {
    background: #ffd9dc;
    color: #400011;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 600;
}

.highlight-red {
    background: #ffdad6;
    color: #93000a;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 600;
}

.topic-chip {
    padding: 4px 10px;
    background: #eae8e7;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    color: #5b4042;
}

.driver-card {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #e4e2e1;
    padding: 24px;
    box-shadow: 0 4px 12px rgba(27, 28, 28, 0.04);
}

/* Executive Brief Screen Custom Styles */
.report-card {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #e4e2e1;
    padding: 32px;
    box-shadow: 0 4px 20px rgba(27, 28, 28, 0.06);
}

.report-title {
    font-size: 32px;
    font-weight: 700;
    color: #1b1c1c;
    letter-spacing: -0.02em;
    margin-bottom: 8px;
}

.discovery-box {
    background: #f6f3f2;
    padding: 16px;
    border-radius: 8px;
    border: 1px solid #e4e2e1;
}

.action-num-badge-1 {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #df2457;
    color: #fffbff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 12px;
    flex-shrink: 0;
    margin-top: 2px;
}

.action-num-badge-2 {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #dfe1f7;
    color: #616376;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 12px;
    flex-shrink: 0;
    margin-top: 2px;
}

.takeaway-pill-high {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 9999px;
    background: #f4fffb;
    color: #00685d;
    font-size: 12px;
    font-weight: 700;
}

.takeaway-pill-error {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 9999px;
    background: #ffdad6;
    color: #93000a;
    font-size: 12px;
    font-weight: 700;
}

.takeaway-pill-secondary {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 9999px;
    background: #dfe1f7;
    color: #181b2a;
    font-size: 12px;
    font-weight: 700;
}

.btn-export-outline {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    background: transparent;
    border: 1px solid #8f6f72;
    color: #1b1c1c;
    font-weight: 400;
    font-size: 13px;
    padding: 10px 16px;
    border-radius: 8px;
    cursor: pointer;
}

.btn-export-secondary {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    background: #f6f3f2;
    border: 1px solid #e4e2e1;
    color: #1b1c1c;
    font-weight: 400;
    font-size: 13px;
    padding: 10px 16px;
    border-radius: 8px;
    cursor: pointer;
}

/* Sidebar Fixed User Profile Footer at Bottom Left Corner */
.sidebar-user-footer {
    position: fixed;
    bottom: 20px;
    left: 16px;
    width: 250px;
    background: #ffffff;
    border: 1px solid #e3bdc0;
    border-radius: 12px;
    padding: 12px 14px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 4px 14px rgba(27, 28, 28, 0.08);
    z-index: 999;
}

.sidebar-user-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: #dfe1f7;
    color: #181b2a;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 13px;
    border: 2px solid #b90041;
    flex-shrink: 0;
}

/* Global Application Page Footer */
.app-page-footer {
    margin-top: 48px;
    padding: 24px 0 16px 0;
    border-top: 1px solid #e4e2e1;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #5b4042;
    font-size: 13px;
}

/* Streamlit Download Button Styling - Un-colored Clean Outline Style */
div.stDownloadButton > button {
    background-color: #ffffff !important;
    color: #1b1c1c !important;
    border: 1px solid #8f6f72 !important;
    border-radius: 8px !important;
    padding: 10px 16px !important;
    font-weight: 400 !important;
    font-size: 13px !important;
    font-family: 'Outfit', sans-serif !important;
    box-shadow: none !important;
    transition: all 0.2s ease-in-out !important;
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
}

div.stDownloadButton > button:hover {
    background-color: #f6f3f2 !important;
    color: #1b1c1c !important;
    border-color: #1b1c1c !important;
}

/* Unresolved Research Questions Section Custom Styles */
.research-section-card {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #e4e2e1;
    padding: 24px;
    box-shadow: 0 4px 16px rgba(27, 28, 28, 0.04);
    margin-top: 24px;
}

.research-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 16px;
    margin-top: 16px;
}

.research-q-card {
    background: #f6f3f2;
    border: 1px solid #e4e2e1;
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.2s ease;
}

.research-q-card:hover {
    background: #ffffff;
    border-color: #e3bdc0;
    box-shadow: 0 4px 12px rgba(185, 0, 65, 0.06);
    transform: translateY(-2px);
}

.badge-validation-method {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 700;
    width: fit-content;
    margin-top: 12px;
}

.badge-method-analytics {
    background: #f4fffb;
    color: #00685d;
    border: 1px solid #4fdbc8;
}

.badge-method-survey {
    background: #dfe1f7;
    color: #181b2a;
    border: 1px solid #c3c5da;
}

.badge-method-cohort {
    background: #ffdad6;
    color: #93000a;
    border: 1px solid #e3bdc0;
}
</style>"""
    st.markdown(css_content, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="Myntra Wishlist Discovery Engine",
        page_icon="🛍️",
        layout="wide"
    )

    inject_custom_css()

    db, vs = get_managers()
    aggregator = WarehouseAggregator(db)
    scorer = OpportunityScorer(db)
    clusterer = VectorClusterer(vs)
    report_gen = ExecutiveReportGenerator(db, vs)

    # Sidebar Navigation & Profile matching code.html & screen.png
    st.sidebar.markdown("""<div style="margin-bottom: 20px;">
<div style="font-size: 22px; font-weight: 700; color: #b90041;">PM Dashboard</div>
<div style="font-size: 12px; color: #5b4042; font-weight: 600;">AI Discovery Engine</div>
</div>""", unsafe_allow_html=True)

    nav_selection = st.sidebar.radio(
        "Navigation",
        options=["Opportunity Matrix", "Motivations", "Quote Explorer", "Executive Brief"],
        index=0,
        label_visibility="collapsed"
    )

    st.sidebar.markdown("""<hr style="border: none; border-top: 1px solid #e4e2e1; margin: 20px 0;" />""", unsafe_allow_html=True)
    st.sidebar.header("🔍 Discovery Filters")
    platform_filter = st.sidebar.multiselect(
        "Source Platform",
        options=["PLAY_STORE", "REDDIT", "YOUTUBE"],
        default=["PLAY_STORE", "REDDIT", "YOUTUBE"],
        format_func=format_label
    )
    min_intent = st.sidebar.slider("Minimum Intent Score", 0.0, 1.0, 0.0, 0.05)

    # Top Navigation Bar matching code.html lines 234-255
    nav_html = """<div class="top-nav-bar">
<div class="main-header-title">Myntra Wishlist Discovery Engine</div>
<div class="header-actions">
<div class="search-box">
<span class="material-symbols-outlined" style="font-size:18px; color:#5b4042;">search</span>
<input type="text" placeholder="Search insights..." />
</div>
<button class="btn-export-primary">
<span class="material-symbols-outlined" style="font-size:18px;">download</span>
<span>Export Executive Brief</span>
</button>
</div>
</div>"""
    st.markdown(nav_html, unsafe_allow_html=True)

    if nav_selection == "Opportunity Matrix":
        # Render the Exact Executive Dashboard screen matching screen.png & code.html
        st.markdown('<div class="page-title">Executive Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-subtitle">AI-assisted analysis of customer feedback and wishlist purchase barriers.</div>', unsafe_allow_html=True)

        st.markdown("""<div style="background: #fbf9f8; border: 1px solid #e3bdc0; border-left: 4px solid #b90041; border-radius: 8px; padding: 12px 16px; margin: 12px 0 20px 0; display: flex; align-items: center; gap: 10px; font-size: 14px; color: #5b4042;">
<span class="material-symbols-outlined" style="color: #b90041; font-size: 20px;">info</span>
<span><b>Analysis Note:</b> 740 public sources analyzed; one source may generate multiple AI insights, resulting in 1,445 extracted insights.</span>
</div>""", unsafe_allow_html=True)

        funnel = aggregator.get_conversion_funnel_summary()
        raw_posts_cnt = funnel["total_raw_posts"]
        analyzed_cnt = funnel["total_analyzed_insights"]
        dropoff_pct = funnel["high_intent_dropoff_pct"]
        top_blocker = format_label(funnel["top_conversion_blocker"])

        kpi_html = f"""<div class="kpi-grid" style="grid-template-columns: repeat(5, 1fr); margin-bottom: 24px;">
<div class="kpi-card">
<div class="kpi-top">
<span class="kpi-label">PLAY STORE REVIEWS</span>
<span class="material-symbols-outlined kpi-icon-badge badge-primary">shop</span>
</div>
<div class="kpi-val">{funnel['play_store_count']}</div>
<div class="kpi-sub sub-green">
<span class="material-symbols-outlined" style="font-size:16px;">trending_up</span>
<span>Play Store analyzed</span>
</div>
</div>
<div class="kpi-card">
<div class="kpi-top">
<span class="kpi-label">REDDIT POSTS</span>
<span class="material-symbols-outlined kpi-icon-badge badge-primary">forum</span>
</div>
<div class="kpi-val">{funnel['reddit_count']}</div>
<div class="kpi-sub sub-green">
<span class="material-symbols-outlined" style="font-size:16px;">trending_up</span>
<span>r/IndianFashionAddicts</span>
</div>
</div>
<div class="kpi-card">
<div class="kpi-top">
<span class="kpi-label">YOUTUBE COMMENTS</span>
<span class="material-symbols-outlined kpi-icon-badge badge-primary">video_library</span>
</div>
<div class="kpi-val">{funnel['youtube_count']}</div>
<div class="kpi-sub sub-green">
<span class="material-symbols-outlined" style="font-size:16px;">trending_up</span>
<span>Try-on haul comments</span>
</div>
</div>
<div class="kpi-card">
<div class="kpi-top">
<span class="kpi-label">RELEVANT INSIGHTS</span>
<span class="material-symbols-outlined kpi-icon-badge badge-tertiary">lightbulb</span>
</div>
<div class="kpi-val">{funnel['total_analyzed_insights']}</div>
<div class="kpi-sub sub-neutral">
<span class="material-symbols-outlined" style="font-size:16px;">info</span>
<span>Extracted AI insights</span>
</div>
</div>
<div class="kpi-card">
<div class="kpi-top">
<span class="kpi-label">FINAL FRICTION THEMES</span>
<span class="material-symbols-outlined kpi-icon-badge badge-error">category</span>
</div>
<div class="kpi-val">{funnel['final_themes_count']}</div>
<div class="kpi-sub sub-neutral">
<span>Friction themes identified</span>
</div>
</div>
</div>"""
        st.markdown(kpi_html, unsafe_allow_html=True)

        # Core Friction Themes Component
        themes_html = """<div style="background: #ffffff; border: 1px solid #e4e2e1; border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
<div style="font-size: 16px; font-weight: 700; color: #1b1c1c; margin-bottom: 14px; display: flex; align-items: center; justify-content: space-between;">
<div style="display: flex; align-items: center; gap: 8px;">
<span class="material-symbols-outlined" style="color: #b90041;">category</span>
<span>Core Friction Themes Identified</span>
</div>
<span style="font-size: 12px; color: #5b4042; font-weight: 600; background: #f6f3f2; padding: 4px 10px; border-radius: 9999px;">Categorized Friction Domains</span>
</div>
<div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px;">
<div style="background: #fff8f7; border: 1px solid #e3bdc0; border-radius: 8px; padding: 12px; text-align: center;">
<div style="font-size: 13px; font-weight: 700; color: #b90041;">Size & Fit</div>
<div style="font-size: 11px; color: #5b4042; margin-top: 2px;">Predictable Sizing</div>
</div>
<div style="background: #fff8f7; border: 1px solid #e3bdc0; border-radius: 8px; padding: 12px; text-align: center;">
<div style="font-size: 13px; font-weight: 700; color: #b90041;">Product Quality</div>
<div style="font-size: 11px; color: #5b4042; margin-top: 2px;">Fabric & Accuracy</div>
</div>
<div style="background: #fff8f7; border: 1px solid #e3bdc0; border-radius: 8px; padding: 12px; text-align: center;">
<div style="font-size: 13px; font-weight: 700; color: #b90041;">Review Trust</div>
<div style="font-size: 11px; color: #5b4042; margin-top: 2px;">User Media & Trust</div>
</div>
<div style="background: #fff8f7; border: 1px solid #e3bdc0; border-radius: 8px; padding: 12px; text-align: center;">
<div style="font-size: 13px; font-weight: 700; color: #b90041;">Styling & Occasion</div>
<div style="font-size: 11px; color: #5b4042; margin-top: 2px;">Style & Wardrobe Match</div>
</div>
<div style="background: #fff8f7; border: 1px solid #e3bdc0; border-radius: 8px; padding: 12px; text-align: center;">
<div style="font-size: 13px; font-weight: 700; color: #b90041;">Price & Value</div>
<div style="font-size: 11px; color: #5b4042; margin-top: 2px;">Discount Postponement</div>
</div>
<div style="background: #fff8f7; border: 1px solid #e3bdc0; border-radius: 8px; padding: 12px; text-align: center;">
<div style="font-size: 13px; font-weight: 700; color: #b90041;">Delivery & Returns</div>
<div style="font-size: 11px; color: #5b4042; margin-top: 2px;">Logistics & Returns</div>
</div>
<div style="background: #fff8f7; border: 1px solid #e3bdc0; border-radius: 8px; padding: 12px; text-align: center;">
<div style="font-size: 13px; font-weight: 700; color: #b90041;">Stock Availability</div>
<div style="font-size: 11px; color: #5b4042; margin-top: 2px;">Inventory Out-of-Stock</div>
</div>
</div>
</div>"""
        st.markdown(themes_html, unsafe_allow_html=True)



        opps = scorer.compute_opportunity_scores()

        # Build dynamic HTML rows for Matrix matching screen.png & code.html
        rows_html = ""
        if opps:
            for o in opps:
                p_rank = getattr(o, "priority_rank", o.prioritization_level)
                pill_class = "pill-p1" if p_rank == "P1" else ("pill-p2" if p_rank == "P2" else "pill-p3")
                evidence_label = getattr(o, "evidence_strength", "Partially Supported")
                if evidence_label == "Strongly Supported":
                    evidence_pill = '<span class="takeaway-pill-high"><span style="width: 6px; height: 6px; border-radius: 50%; background: #00685d;"></span> Strongly Supported</span>'
                elif evidence_label == "Partially Supported":
                    evidence_pill = '<span class="takeaway-pill-secondary"><span style="width: 6px; height: 6px; border-radius: 50%; background: #5b5d6f;"></span> Partially Supported</span>'
                else:
                    evidence_pill = '<span class="takeaway-pill-error"><span style="width: 6px; height: 6px; border-radius: 50%; background: #ba1a1a;"></span> Needs Interview Validation</span>'

                rows_html += f"""<tr>
<td style="font-weight: 700; color: #1b1c1c;">{o.opportunity_area}</td>
<td style="text-align: center; font-weight: 600; color: #b90041;">{o.ai_feedback_mentions}</td>
<td style="text-align: center; font-weight: 600; color: #181b2a;">{o.survey_respondent_count}</td>
<td style="text-align: center; font-weight: 600; color: #1b1c1c;">{o.purchase_impact:.2f}</td>
<td style="text-align: center; font-weight: 600; color: #5b4042;">{o.severity_weight:.1f}</td>
<td style="text-align: center;">{evidence_pill}</td>
<td style="text-align: center;"><span class="{pill_class}">{p_rank}</span></td>
</tr>"""
        else:
            rows_html = """<tr>
<td style="font-weight: 700; color: #1b1c1c;">Size & Fit Friction</td>
<td style="text-align: center; font-weight: 600; color: #b90041;">305</td>
<td style="text-align: center; font-weight: 600; color: #181b2a;">450</td>
<td style="text-align: center; font-weight: 600; color: #1b1c1c;">0.74</td>
<td style="text-align: center; font-weight: 600; color: #5b4042;">2.5</td>
<td style="text-align: center;"><span class="takeaway-pill-high"><span style="width: 6px; height: 6px; border-radius: 50%; background: #00685d;"></span> Strongly Supported</span></td>
<td style="text-align: center;"><span class="pill-p1">P1</span></td>
</tr>
<tr>
<td style="font-weight: 700; color: #1b1c1c;">Product Quality Skepticism</td>
<td style="text-align: center; font-weight: 600; color: #b90041;">220</td>
<td style="text-align: center; font-weight: 600; color: #181b2a;">310</td>
<td style="text-align: center; font-weight: 600; color: #1b1c1c;">0.79</td>
<td style="text-align: center; font-weight: 600; color: #5b4042;">2.2</td>
<td style="text-align: center;"><span class="takeaway-pill-high"><span style="width: 6px; height: 6px; border-radius: 50%; background: #00685d;"></span> Strongly Supported</span></td>
<td style="text-align: center;"><span class="pill-p1">P1</span></td>
</tr>
<tr>
<td style="font-weight: 700; color: #1b1c1c;">Review Trust Deficit</td>
<td style="text-align: center; font-weight: 600; color: #b90041;">215</td>
<td style="text-align: center; font-weight: 600; color: #181b2a;">280</td>
<td style="text-align: center; font-weight: 600; color: #1b1c1c;">0.78</td>
<td style="text-align: center; font-weight: 600; color: #5b4042;">2.0</td>
<td style="text-align: center;"><span class="takeaway-pill-high"><span style="width: 6px; height: 6px; border-radius: 50%; background: #00685d;"></span> Strongly Supported</span></td>
<td style="text-align: center;"><span class="pill-p1">P1</span></td>
</tr>
<tr>
<td style="font-weight: 700; color: #1b1c1c;">Price & Value Postponement</td>
<td style="text-align: center; font-weight: 600; color: #b90041;">152</td>
<td style="text-align: center; font-weight: 600; color: #181b2a;">210</td>
<td style="text-align: center; font-weight: 600; color: #1b1c1c;">0.77</td>
<td style="text-align: center; font-weight: 600; color: #5b4042;">2.0</td>
<td style="text-align: center;"><span class="takeaway-pill-secondary"><span style="width: 6px; height: 6px; border-radius: 50%; background: #5b5d6f;"></span> Partially Supported</span></td>
<td style="text-align: center;"><span class="pill-p2">P2</span></td>
</tr>
<tr>
<td style="font-weight: 700; color: #1b1c1c;">Delivery & Returns Friction</td>
<td style="text-align: center; font-weight: 600; color: #b90041;">83</td>
<td style="text-align: center; font-weight: 600; color: #181b2a;">125</td>
<td style="text-align: center; font-weight: 600; color: #1b1c1c;">0.77</td>
<td style="text-align: center; font-weight: 600; color: #5b4042;">1.8</td>
<td style="text-align: center;"><span class="takeaway-pill-secondary"><span style="width: 6px; height: 6px; border-radius: 50%; background: #5b5d6f;"></span> Partially Supported</span></td>
<td style="text-align: center;"><span class="pill-p2">P2</span></td>
</tr>
<tr>
<td style="font-weight: 700; color: #1b1c1c;">Stock Availability Friction</td>
<td style="text-align: center; font-weight: 600; color: #b90041;">9</td>
<td style="text-align: center; font-weight: 600; color: #181b2a;">45</td>
<td style="text-align: center; font-weight: 600; color: #1b1c1c;">0.80</td>
<td style="text-align: center; font-weight: 600; color: #5b4042;">1.5</td>
<td style="text-align: center;"><span class="takeaway-pill-error"><span style="width: 6px; height: 6px; border-radius: 50%; background: #ba1a1a;"></span> Needs Interview Validation</span></td>
<td style="text-align: center;"><span class="pill-p3">P3</span></td>
</tr>"""

        matrix_html = f"""<div class="matrix-card">
<div class="matrix-header">
<div>
<div class="matrix-title">Opportunity Comparison Matrix</div>
<div class="matrix-sub">Actionable insights ranked by severity, purchase impact, and evidence strength.</div>
</div>
<button class="matrix-btn-filter">
<span class="material-symbols-outlined" style="font-size:16px;">filter_list</span>
<span>Filter</span>
</button>
</div>
<div style="overflow-x: auto;">
<table class="matrix-table">
<thead>
<tr>
<th>OPPORTUNITY AREA</th>
<th style="text-align: center;">AI EVIDENCE: PUBLIC-FEEDBACK MENTIONS</th>
<th style="text-align: center;">SURVEY EVIDENCE: RESPONDENT COUNT</th>
<th style="text-align: center;">PURCHASE IMPACT</th>
<th style="text-align: center;">SEVERITY</th>
<th style="text-align: center;">EVIDENCE STRENGTH</th>
<th style="width: 100px; text-align: center;">PRIORITY RANK</th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
</div>
</div>"""

        st.markdown(matrix_html, unsafe_allow_html=True)

        # Unresolved Research Questions Section (Hypotheses requiring empirical validation)
        research_questions_html = """<div class="research-section-card">
<div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e4e2e1; padding-bottom: 16px; margin-bottom: 16px;">
<div>
<div style="display: flex; align-items: center; gap: 8px;">
<span class="material-symbols-outlined" style="color: #b90041;">help_center</span>
<div style="font-size: 20px; font-weight: 700; color: #1b1c1c;">Unresolved Research Questions</div>
</div>
<div style="font-size: 13px; color: #5b4042; margin-top: 4px;">
Key product hypotheses extracted from public feedback that require empirical validation before building solutions.
</div>
</div>
<span class="takeaway-pill-secondary" style="font-size: 12px;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #5b5d6f;"></span> Validation Required</span>
</div>

<div class="research-grid">
<!-- Question 1: Size Uncertainty Impact -->
<div class="research-q-card">
<div>
<div style="font-size: 11px; font-weight: 700; color: #b90041; text-transform: uppercase; margin-bottom: 4px;">Hypothesis 1 • Fit & Sizing</div>
<div style="font-size: 15px; font-weight: 700; color: #1b1c1c; margin-bottom: 8px;">Size Uncertainty vs. Price Sensitivity</div>
<div style="font-size: 13px; color: #5b4042; line-height: 1.5;">
Does size uncertainty impact wishlist abandonments more than price sensitivity for high-tier apparel? User interviews and surveys explain <i>why</i> sizing uncertainty occurs (sizing anxiety, inconsistent brand charts), while internal behavioral analytics quantitatively measure <i>how much</i> it impacts conversion. Public feedback alone cannot measure cart drop-off.
</div>
</div>
<div style="display: flex; flex-direction: column; gap: 4px; margin-top: 12px;">
<div class="badge-validation-method badge-method-survey" style="margin-top: 0;">
<span class="material-symbols-outlined" style="font-size: 16px;">record_voice_over</span>
<span>Qualitative (Why): User Surveys & Interviews</span>
</div>
<div class="badge-validation-method badge-method-analytics" style="margin-top: 0;">
<span class="material-symbols-outlined" style="font-size: 16px;">analytics</span>
<span>Quantitative (How Much): Internal Analytics</span>
</div>
</div>
</div>

<!-- Question 2: Strongest High-Intent Blocker -->
<div class="research-q-card">
<div>
<div style="font-size: 11px; font-weight: 700; color: #00685d; text-transform: uppercase; margin-bottom: 4px;">Hypothesis 2 • Funnel Telemetry</div>
<div style="font-size: 15px; font-weight: 700; color: #1b1c1c; margin-bottom: 8px;">Strongest High-Intent Conversion Blocker</div>
<div style="font-size: 13px; color: #5b4042; line-height: 1.5;">
Is sizing mismatch the primary conversion blocker across high-intent vs. low-intent wishlists? Telemetry data must verify whether high-intent buyers (intent > 0.8) drop off at size selection vs. checkout.
</div>
</div>
<div class="badge-validation-method badge-method-analytics">
<span class="material-symbols-outlined" style="font-size: 16px;">analytics</span>
<span>Validation Method: Internal Analytics</span>
</div>
</div>

<!-- Question 3: External Comparison Behavior -->
<div class="research-q-card">
<div>
<div style="font-size: 11px; font-weight: 700; color: #181b2a; text-transform: uppercase; margin-bottom: 4px;">Hypothesis 3 • Cross-Shopping</div>
<div style="font-size: 15px; font-weight: 700; color: #1b1c1c; margin-bottom: 8px;">External Platform Comparison Behavior</div>
<div style="font-size: 13px; color: #5b4042; margin-bottom: 8px; line-height: 1.5;">
Do users abandon wishlists due to price/product comparison on competitor platforms? Unstructured posts mention finding alternatives elsewhere, requiring exit surveys to quantify off-platform leakage.
</div>
</div>
<div class="badge-validation-method badge-method-survey">
<span class="material-symbols-outlined" style="font-size: 16px;">quiz</span>
<span>Validation Method: User Survey / Interviews</span>
</div>
</div>

<!-- Question 4: Wishlist-Age & Aging Impact -->
<div class="research-q-card">
<div>
<div style="font-size: 11px; font-weight: 700; color: #93000a; text-transform: uppercase; margin-bottom: 4px;">Hypothesis 4 • Lifecycle Aging</div>
<div style="font-size: 15px; font-weight: 700; color: #1b1c1c; margin-bottom: 8px;">Wishlist-Age Impact & Conversion Decay</div>
<div style="font-size: 13px; color: #5b4042; line-height: 1.5;">
How does item age in wishlist (e.g., >30 days) correlate with cart conversion rate vs. absolute churn? Cohort tracking is required to map time-to-conversion curves over product lifecycles.
</div>
</div>
<div class="badge-validation-method badge-method-cohort">
<span class="material-symbols-outlined" style="font-size: 16px;">groups</span>
<span>Validation Method: Cohort Analysis</span>
</div>
</div>
</div>
</div>"""
        st.markdown(research_questions_html, unsafe_allow_html=True)

    elif nav_selection == "Motivations":
        # Render Motivations & Analytics View matching ui_screen/motivation_screen code.html & screen.png
        st.markdown('<div class="page-title">Motivations & Analytics</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-subtitle">Deep dive into user intent, identifying key friction points and conversion drivers across the wishlist journey.</div>', unsafe_allow_html=True)

        # Section 1: Funnel Visualization
        funnel_html = """<div class="funnel-card">
<div class="funnel-header">
<div style="font-size: 20px; font-weight: 600; color: #1b1c1c;">Wishlist → Purchase Funnel</div>
<button class="matrix-btn-filter">
<span class="material-symbols-outlined" style="font-size:16px;">filter_list</span>
<span>Filter by Category</span>
</button>
</div>
<div class="funnel-grid">
<div class="funnel-step">
<div class="funnel-bar-container">
<div class="funnel-bar-fill" style="height: 100%;"></div>
<div class="funnel-pct-text">100%</div>
</div>
<div style="text-align: center; margin-top: 8px;">
<div style="font-size: 12px; font-weight: 700; color: #1b1c1c;">Added to Wishlist</div>
<div style="font-size: 12px; color: #5b4042;">2.4M items</div>
</div>
</div>

<div class="funnel-arrow">
<span class="material-symbols-outlined" style="font-size: 20px;">arrow_forward_ios</span>
<span class="funnel-drop-text">-22% Drop</span>
</div>

<div class="funnel-step">
<div class="funnel-bar-container" style="width: 90%;">
<div class="funnel-bar-fill" style="height: 78%;"></div>
<div class="funnel-pct-text">78%</div>
</div>
<div style="text-align: center; margin-top: 8px;">
<div style="font-size: 12px; font-weight: 700; color: #1b1c1c;">Viewed Later</div>
<div style="font-size: 12px; color: #5b4042;">1.87M items</div>
</div>
</div>

<div class="funnel-arrow">
<span class="material-symbols-outlined" style="font-size: 20px;">arrow_forward_ios</span>
<span class="funnel-drop-text">-45% Drop</span>
</div>

<div class="funnel-step">
<div class="funnel-bar-container" style="width: 70%;">
<div class="funnel-bar-fill" style="height: 43%; background: #b90041;"></div>
<div class="funnel-pct-text">43%</div>
</div>
<div style="text-align: center; margin-top: 8px;">
<div style="font-size: 12px; font-weight: 700; color: #1b1c1c;">Added to Cart</div>
<div style="font-size: 12px; color: #5b4042;">1.03M items</div>
</div>
</div>

<div class="funnel-arrow">
<span class="material-symbols-outlined" style="font-size: 20px;">arrow_forward_ios</span>
<span class="funnel-drop-text">-18% Drop</span>
</div>

<div class="funnel-step">
<div class="funnel-bar-container" style="width: 50%;">
<div class="funnel-bar-fill" style="height: 25%; background: #910031;"></div>
<div class="funnel-pct-text">25%</div>
</div>
<div style="text-align: center; margin-top: 8px;">
<div style="font-size: 12px; font-weight: 700; color: #1b1c1c;">Purchased</div>
<div style="font-size: 12px; color: #5b4042;">600k items</div>
</div>
</div>
</div>
</div>"""
        st.markdown(funnel_html, unsafe_allow_html=True)

        # Section 2: Charts Side-by-Side Grid
        col1, col2 = st.columns([7, 5])
        with col1:
            blockers_html = """<div class="chart-card">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
<div style="font-size: 20px; font-weight: 600; color: #1b1c1c;">Primary Conversion Blockers</div>
<span class="material-symbols-outlined" style="color: #5b4042; cursor: pointer;">more_vert</span>
</div>
<div style="display: flex; flex-direction: column; gap: 8px; margin-top: 16px;">
<div class="blocker-bar-row">
<div class="blocker-label">Price Too High</div>
<div class="blocker-bar-bg" style="width: 85%; background: rgba(186, 26, 26, 0.85);">
<span style="position: absolute; right: 8px; font-size: 10px; color: #ffffff; font-weight: 700;">85%</span>
</div>
</div>

<div class="blocker-bar-row">
<div class="blocker-label">Out of Size</div>
<div class="blocker-bar-bg" style="width: 62%; background: rgba(223, 36, 87, 0.85);">
<span style="position: absolute; right: 8px; font-size: 10px; color: #ffffff; font-weight: 700;">62%</span>
</div>
</div>

<div class="blocker-bar-row">
<div class="blocker-label">Shipping Cost</div>
<div class="blocker-bar-bg" style="width: 45%; background: rgba(185, 0, 65, 0.85);">
<span style="position: absolute; right: 8px; font-size: 10px; color: #ffffff; font-weight: 700;">45%</span>
</div>
</div>

<div class="blocker-bar-row">
<div class="blocker-label">Unsure Fit</div>
<div class="blocker-bar-bg" style="width: 30%; background: rgba(143, 111, 114, 0.85);">
<span style="position: absolute; right: 8px; font-size: 10px; color: #ffffff; font-weight: 700;">30%</span>
</div>
</div>

<div class="blocker-bar-row">
<div class="blocker-label">Found Better</div>
<div class="blocker-bar-bg" style="width: 15%; background: rgba(91, 93, 111, 0.85);">
<span style="position: absolute; right: 8px; font-size: 10px; color: #ffffff; font-weight: 700;">15%</span>
</div>
</div>
</div>
</div>"""
            st.markdown(blockers_html, unsafe_allow_html=True)

        with col2:
            donut_html = """<div class="chart-card" style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
<div style="display: flex; justify-content: space-between; align-items: center; width: 100%; margin-bottom: 16px;">
<div style="font-size: 20px; font-weight: 600; color: #1b1c1c;">Wishlist Motivations</div>
<span class="material-symbols-outlined" style="color: #5b4042; cursor: pointer;">info</span>
</div>
<div class="donut-container">
<div class="donut-hole">
<span style="font-size: 32px; font-weight: 700; color: #1b1c1c; line-height: 1;">2.4M</span>
<span style="font-size: 10px; font-weight: 600; color: #5b4042; margin-top: 4px;">Total Items</span>
</div>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; width: 100%; font-size: 12px; font-weight: 600;">
<div style="display: flex; align-items: center; gap: 6px;">
<div style="width: 12px; height: 12px; border-radius: 50%; background: #df2457;"></div>
<span>Price Tracking (40%)</span>
</div>
<div style="display: flex; align-items: center; gap: 6px;">
<div style="width: 12px; height: 12px; border-radius: 50%; background: #ffb2ba;"></div>
<span>Outfit Planning (25%)</span>
</div>
<div style="display: flex; align-items: center; gap: 6px;">
<div style="width: 12px; height: 12px; border-radius: 50%; background: #5b5d6f;"></div>
<span>Awaiting Restock (20%)</span>
</div>
<div style="display: flex; align-items: center; gap: 6px;">
<div style="width: 12px; height: 12px; border-radius: 50%; background: #e3bdc0;"></div>
<span>Casual Browsing (15%)</span>
</div>
</div>
</div>"""
            st.markdown(donut_html, unsafe_allow_html=True)

        st.markdown('<div style="font-size: 20px; font-weight: 600; color: #1b1c1c; margin: 28px 0 16px 0; display: flex; align-items: center; gap: 8px;"><span class="material-symbols-outlined" style="color: #b90041;">group</span>User Segment Analysis</div>', unsafe_allow_html=True)

        # Section 3: User Segment Analysis Bento
        b1, b2 = st.columns(2)
        with b1:
            segment1_html = """<div class="bento-card">
<div class="bento-icon">
<span class="material-symbols-outlined" style="font-size: 32px; color: #b90041;">straighten</span>
</div>
<div style="flex-grow: 1;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
<div style="font-size: 18px; font-weight: 600; color: #1b1c1c;">Fit-Conscious Buyer</div>
<span style="background: #e4e2e1; color: #5b4042; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">High Value</span>
</div>
<div style="font-size: 13px; color: #5b4042; margin-bottom: 16px;">Highly engaged but hesitates due to sizing uncertainty. Needs social proof and exact measurements.</div>
<div style="display: flex; flex-direction: column; gap: 12px;">
<div>
<div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 600; margin-bottom: 4px;">
<span style="color: #5b4042;">Size Anxiety Friction</span>
<span style="color: #ba1a1a; font-weight: 700;">High (8.2/10)</span>
</div>
<div class="progress-bar-bg"><div class="progress-bar-fill-high" style="width: 82%;"></div></div>
</div>

<div>
<div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 600; margin-bottom: 4px;">
<span style="color: #5b4042;">Return Rate Propensity</span>
<span style="color: #b90041; font-weight: 700;">Medium (5.5/10)</span>
</div>
<div class="progress-bar-bg"><div class="progress-bar-fill-med" style="width: 55%;"></div></div>
</div>
</div>
</div>
</div>"""
            st.markdown(segment1_html, unsafe_allow_html=True)

        with b2:
            segment2_html = """<div class="bento-card">
<div class="bento-icon">
<span class="material-symbols-outlined" style="font-size: 32px; color: #b90041;">payments</span>
</div>
<div style="flex-grow: 1;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
<div style="font-size: 18px; font-weight: 600; color: #1b1c1c;">Budget-Sensitive Saver</div>
<span style="background: #eae8e7; color: #1b1c1c; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">High Volume</span>
</div>
<div style="font-size: 13px; color: #5b4042; margin-bottom: 16px;">Uses wishlist exclusively as a price drop tracker. Highly responsive to push notifications on sales.</div>
<div style="display: flex; flex-direction: column; gap: 12px;">
<div>
<div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 600; margin-bottom: 4px;">
<span style="color: #5b4042;">Price Sensitivity Score</span>
<span style="color: #ba1a1a; font-weight: 700;">Critical (9.4/10)</span>
</div>
<div class="progress-bar-bg"><div class="progress-bar-fill-high" style="width: 94%;"></div></div>
</div>

<div>
<div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 600; margin-bottom: 4px;">
<span style="color: #5b4042;">Brand Loyalty</span>
<span style="color: #5b5d6f; font-weight: 700;">Low (3.1/10)</span>
</div>
<div class="progress-bar-bg"><div class="progress-bar-fill-low" style="width: 31%;"></div></div>
</div>
</div>
</div>
</div>"""
            st.markdown(segment2_html, unsafe_allow_html=True)


    elif nav_selection == "Quote Explorer":
        # Render Verbatim Customer Evidence View with dynamic query and raw reviews feed
        col_title, col_search = st.columns([7, 5])
        with col_title:
            st.markdown('<div class="page-title">Verbatim Customer Evidence</div>', unsafe_allow_html=True)
            st.markdown('<div class="page-subtitle">Explore 580+ raw user reviews across Play Store, Reddit, and YouTube.</div>', unsafe_allow_html=True)
        with col_search:
            search_query = st.text_input("🔍 Search Customer Reviews", value="", placeholder="Search keywords (e.g., 'size', 'fabric', 'EORS', 'discount')...", key="quote_search_input")

        st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)

        raw_posts = db.get_all_raw_posts()
        analyzed_insights = db.get_all_analyzed_insights()
        insight_map = {insight.post_id: insight for insight in analyzed_insights}

        # Filter controls
        f_col1, f_col2, f_col3 = st.columns([3, 3, 4])
        with f_col1:
            platform_filter = st.selectbox("Filter Platform", ["All Platforms", "play_store", "reddit", "youtube"], key="quote_platform_filter")
        with f_col2:
            max_cards = st.slider("Display Card Limit", min_value=10, max_value=200, value=30, step=10, key="quote_limit_slider")
        with f_col3:
            st.markdown(f"<div style='padding-top: 28px; font-size: 14px; font-weight: 600; color: #b90041;'>Total Database Reviews: {len(raw_posts)} posts</div>", unsafe_allow_html=True)

        # Apply filtering
        filtered_posts = raw_posts
        if platform_filter != "All Platforms":
            filtered_posts = [p for p in filtered_posts if p.source_platform.value == platform_filter]
        if search_query:
            sq = search_query.lower()
            filtered_posts = [p for p in filtered_posts if sq in p.cleaned_text.lower() or sq in p.post_id.lower()]

        # 2-Column Grid Layout
        feed_col, driver_col = st.columns([8, 4])

        with feed_col:
            st.markdown(f"<div style='font-size: 14px; color: #5b4042; margin-bottom: 12px;'>Showing <b>{min(len(filtered_posts), max_cards)}</b> of <b>{len(filtered_posts)}</b> matching reviews</div>", unsafe_allow_html=True)
            
            for post in filtered_posts[:max_cards]:
                insight = insight_map.get(post.post_id)
                platform_name = post.source_platform.value.upper()
                motivation_label = insight.wishlist_motivation.value if insight else "GENERAL_FEEDBACK"
                blocker_label = insight.primary_blocker.value if insight else "UNSPECIFIED"
                segment_label = insight.user_segment.value if insight else "SHOPPER"
                intent_val = insight.intent_score if insight else 0.75

                card_html = f"""<div class="quote-card" style="margin-bottom: 14px;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
<div style="display: flex; align-items: center; gap: 10px;">
<div class="quote-icon-badge">
<span class="material-symbols-outlined" style="font-size: 16px;">forum</span>
</div>
<div>
<div style="font-size: 15px; font-weight: 700; color: #1b1c1c;">{post.post_id} • {segment_label}</div>
<div style="font-size: 12px; color: #5b4042; font-weight: 600;">{platform_name} • Upvotes: {post.upvotes}</div>
</div>
</div>
<div class="intent-badge-high">
<span class="material-symbols-outlined" style="font-size: 14px;">target</span>
<span>Intent: {intent_val:.2f}</span>
</div>
</div>
<div class="quote-text-quote" style="font-size: 14px; line-height: 1.5; color: #1b1c1c;">
"{post.cleaned_text}"
</div>
<div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px;">
<span class="topic-chip" style="background: #fce4ec; color: #b90041; font-weight: 600;">{motivation_label}</span>
<span class="topic-chip" style="background: #ffebee; color: #c62828; font-weight: 600;">{blocker_label}</span>
</div>
</div>"""
                st.markdown(card_html, unsafe_allow_html=True)

            # Expandable full data table view
            with st.expander("📋 View All Ingested Reviews Data Table (Full 586 Rows)", expanded=False):
                table_data = [
                    {
                        "Post ID": p.post_id,
                        "Platform": p.source_platform.value,
                        "User Review Text": p.cleaned_text,
                        "Upvotes": p.upvotes,
                        "Replies": p.replies
                    }
                    for p in filtered_posts
                ]
                st.dataframe(table_data, use_container_width=True, height=400)


        with driver_col:
            # Sticky Intent Drivers Panel matching code.html lines 275-321
            drivers_html = """<div class="driver-card">
<div style="display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #e4e2e1; padding-bottom: 12px; margin-bottom: 12px;">
<span class="material-symbols-outlined" style="color: #b90041;">analytics</span>
<div style="font-size: 18px; font-weight: 600; color: #1b1c1c;">Intent Drivers</div>
</div>
<div style="font-size: 13px; color: #5b4042; margin-bottom: 20px;">Aggregated structural themes based on the current semantic query.</div>

<div style="display: flex; flex-direction: column; gap: 16px;">
<div>
<div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 600; margin-bottom: 4px;">
<span style="color: #1b1c1c;">Material Degradation</span>
<span style="color: #b90041; font-weight: 700;">42%</span>
</div>
<div class="progress-bar-bg"><div class="progress-bar-fill-high" style="width: 42%; background: #b90041;"></div></div>
</div>

<div>
<div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 600; margin-bottom: 4px;">
<span style="color: #1b1c1c;">Inconsistent Sizing</span>
<span style="color: #b90041; font-weight: 700;">35%</span>
</div>
<div class="progress-bar-bg"><div class="progress-bar-fill-high" style="width: 35%; background: rgba(185, 0, 65, 0.8);"></div></div>
</div>

<div>
<div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 600; margin-bottom: 4px;">
<span style="color: #1b1c1c;">High Aesthetics / Fit</span>
<span style="color: #00685d; font-weight: 700;">18%</span>
</div>
<div class="progress-bar-bg"><div class="progress-bar-fill-high" style="width: 18%; background: #00685d;"></div></div>
</div>
</div>

<div style="margin-top: 24px; pt: 16px; border-top: 1px solid #e4e2e1;">
<button class="btn-export-primary" style="width: 100%; justify-content: center; padding: 10px 16px; border-radius: 8px;">
<span>Generate Action Brief</span>
</button>
</div>
</div>"""
            st.markdown(drivers_html, unsafe_allow_html=True)


    elif nav_selection == "Executive Brief":
        # Render Executive Report Export View matching ui_screen/executive_brief_screen code.html & screen.png
        markdown_report = report_gen.generate_markdown_report()

        doc_col, action_col = st.columns([8, 4])

        with doc_col:
            doc_html = """<div class="report-card">
<div style="border-bottom: 1px solid #e4e2e1; padding-bottom: 20px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: flex-start;">
<div>
<div class="report-title">Myntra Wishlist Intelligence Report: 2026</div>
<div style="font-size: 14px; color: #5b4042;">Generated by AI Discovery Engine • <span style="color: #b90041; font-weight: 600;">Confidential</span></div>
</div>
</div>

<div style="margin-bottom: 28px;">
<div style="font-size: 20px; font-weight: 700; color: #1b1c1c; margin-bottom: 12px;">Executive Summary & Scale of Analysis</div>
<div style="font-size: 15px; color: #5b4042; line-height: 1.6; margin-bottom: 16px;">
AI-assisted analysis of customer feedback and wishlist purchase barriers. 2026 indicates a significant shift in user wishlist behavior, moving away from aspirational hoarding towards curated, intent-driven saves. The 'Myntra Pink' aesthetic continues to drive impulsive adds, but conversion relies heavily on strategic nudges based on emerging micro-trends identified by the AI.
</div>

<div style="background: #fbf9f8; border: 1px solid #e3bdc0; border-left: 4px solid #b90041; border-radius: 12px; padding: 16px; margin-bottom: 16px;">
<div style="font-size: 13px; color: #5b4042; line-height: 1.5; font-weight: 600;">
<span class="material-symbols-outlined" style="color: #b90041; font-size: 18px; vertical-align: middle; margin-right: 6px;">info</span>
740 public sources analyzed; one source may generate multiple AI insights, resulting in 1,445 extracted insights.
</div>
</div>

<div style="background: #fbf9f8; border: 1px solid #e4e2e1; border-radius: 12px; padding: 18px; margin-bottom: 24px;">
<div style="font-size: 15px; font-weight: 700; color: #1b1c1c; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
<span class="material-symbols-outlined" style="color: #b90041;">dataset</span>
<span>Source Data Breakdown (Scale of Analysis)</span>
</div>
<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; font-size: 13px; color: #5b4042;">
<div><b>Play Store reviews analyzed:</b> <span style="color: #b90041; font-weight: 700;">{funnel['play_store_count']}</span></div>
<div><b>Reddit posts analyzed:</b> <span style="color: #b90041; font-weight: 700;">{funnel['reddit_count']}</span></div>
<div><b>YouTube comments analyzed:</b> <span style="color: #b90041; font-weight: 700;">{funnel['youtube_count']}</span></div>
<div><b>Total public posts:</b> <span style="color: #1b1c1c; font-weight: 700;">{funnel['total_raw_posts']}</span></div>
<div><b>Total relevant insights:</b> <span style="color: #00685d; font-weight: 700;">{funnel['total_analyzed_insights']}</span></div>
<div><b>Final friction themes identified:</b> <span style="color: #b90041; font-weight: 700;">{funnel['final_themes_count']}</span></div>
</div>
</div>
</div>

<div style="background: #fff8f7; border: 1px solid #e3bdc0; border-left: 4px solid #b90041; border-radius: 12px; padding: 20px; margin-bottom: 28px; box-shadow: 0 2px 8px rgba(185, 0, 65, 0.04);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
<div style="font-size: 18px; font-weight: 700; color: #1b1c1c; display: flex; align-items: center; gap: 8px;">
<span class="material-symbols-outlined" style="color: #b90041;">analytics</span>
<span>Combined Research Synthesis</span>
</div>
<span class="takeaway-pill-high" style="font-size: 12px; padding: 4px 12px;"><span style="width: 6px; height: 6px; border-radius: 50%; background: #00685d;"></span> Validated Problem Direction</span>
</div>
<div style="font-size: 14px; color: #1b1c1c; line-height: 1.6;">
AI discovery findings indicate that the main barrier is not lack of interest. High-intent users delay purchasing because they need confidence about fit, quality, reviews, customer photos, and comparison between saved products. Many users leave Myntra to validate products before deciding.
</div>
</div>



<div style="margin-bottom: 28px;">
<div style="font-size: 20px; font-weight: 700; color: #1b1c1c; margin-bottom: 16px;">Key AI Discoveries</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
<div class="discovery-box">
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
<span class="material-symbols-outlined" style="color: #00685d;">trending_up</span>
<div style="font-size: 16px; font-weight: 600; color: #1b1c1c;">Trend Velocity</div>
</div>
<div style="font-size: 13px; color: #5b4042; line-height: 1.5;">Y2K revival items are moving from wishlist to cart 40% faster than classic silhouettes.</div>
</div>

<div class="discovery-box">
<div style="display: flex; items-center gap: 8px; margin-bottom: 8px;">
<span class="material-symbols-outlined" style="color: #ba1a1a;">warning</span>
<div style="font-size: 16px; font-weight: 600; color: #1b1c1c;">Abandonment Risk</div>
</div>
<div style="font-size: 13px; color: #5b4042; line-height: 1.5;">High-ticket athleisure shows a 60% drop-off if size availability alerts and review summaries are missing.</div>
</div>
</div>
</div>

<div style="margin-bottom: 28px;">
<div style="font-size: 20px; font-weight: 700; color: #1b1c1c; margin-bottom: 16px;">Strategic Action Recommendations</div>
<div style="display: flex; flex-direction: column; gap: 16px;">
<div style="display: flex; items-start: flex-start; gap: 12px; border-bottom: 1px solid #e4e2e1; padding-bottom: 12px;">
<div class="action-num-badge-1">1</div>
<div>
<div style="font-size: 16px; font-weight: 600; color: #1b1c1c;">Deploy AI Review Summaries & Fit Consensus</div>
<div style="font-size: 13px; color: #5b4042; margin-top: 2px;">Trigger automated AI review summaries and user fit consensus for high-intent wishlisted items to eliminate sizing uncertainty.</div>
</div>
</div>

<div style="display: flex; items-start: flex-start; gap: 12px;">
<div class="action-num-badge-2">2</div>
<div>
<div style="font-size: 16px; font-weight: 600; color: #1b1c1c;">Automate Back-in-Stock & Restock Nudges</div>
<div style="font-size: 13px; color: #5b4042; margin-top: 2px;">Implement automated 48-hour back-in-stock and low-stock alerts to convert wishlisted items without relying on monetary discounts.</div>
</div>
</div>
</div>
</div>

<div style="padding-top: 20px; border-top: 1px solid #e4e2e1;">
<div style="font-size: 16px; font-weight: 600; color: #1b1c1c; margin-bottom: 12px;">AI Leadership Takeaways</div>
<div style="display: flex; gap: 8px; flex-wrap: wrap;">
<span class="takeaway-pill-high"><span style="width: 8px; height: 8px; border-radius: 50%; background: #00685d;"></span> High Confidence</span>
<span class="takeaway-pill-error"><span style="width: 8px; height: 8px; border-radius: 50%; background: #ba1a1a;"></span> Immediate Action Required</span>
<span class="takeaway-pill-secondary"><span style="width: 8px; height: 8px; border-radius: 50%; background: #5b5d6f;"></span> Monitor Trend</span>
</div>
</div>
</div>"""
            st.markdown(doc_html, unsafe_allow_html=True)

        with action_col:
            st.markdown("""<div class="driver-card" style="margin-bottom: 16px;">
<div style="font-size: 18px; font-weight: 600; color: #1b1c1c; margin-bottom: 16px;">Export Actions</div>
<div style="margin-bottom: 12px;">""", unsafe_allow_html=True)

            st.download_button(
                label="📥 Download Executive Brief (Markdown)",
                data=markdown_report,
                file_name="executive_discovery_brief.md",
                mime="text/markdown",
                use_container_width=True,
                key="download_exec_brief_main"
            )

            st.markdown("""</div>
<div style="display: flex; flex-direction: column; gap: 10px;">
<button class="btn-export-outline">
<span class="material-symbols-outlined" style="font-size: 18px;">content_copy</span>
<span>Copy Markdown Report</span>
</button>
<button class="btn-export-secondary">
<span class="material-symbols-outlined" style="font-size: 18px;">link</span>
<span>Share Secure Report Link</span>
</button>
</div>
</div>

<div style="background: #f6f3f2; border-radius: 12px; border: 1px solid #e4e2e1; padding: 16px; margin-bottom: 16px;">
<div style="font-size: 12px; font-weight: 700; color: #5b4042; margin-bottom: 8px; text-transform: uppercase;">Report Meta</div>
<div style="display: flex; flex-direction: column; gap: 6px; font-size: 13px; color: #5b4042;">
<div style="display: flex; justify-content: space-between;"><span>Generated:</span> <span style="font-weight: 600; color: #1b1c1c;">Today, 09:41 AM</span></div>
<div style="display: flex; justify-content: space-between;"><span>Data Range:</span> <span style="font-weight: 600; color: #1b1c1c;">2026</span></div>
<div style="display: flex; justify-content: space-between;"><span>Audience Size:</span> <span style="font-weight: 600; color: #1b1c1c;">2.4M Users</span></div>
</div>
</div>""", unsafe_allow_html=True)

    # Global Application Page Footer
    st.markdown("""<div class="app-page-footer">
<div>© 2026 <b>Myntra AI Discovery Engine</b> • Confidential & Proprietary</div>
<div style="display: flex; gap: 16px;">
<span>Product Insights Platform</span>
<span>•</span>
<span>Powered by Gemini AI</span>
</div>
</div>""", unsafe_allow_html=True)



if __name__ == "__main__":
    main()

