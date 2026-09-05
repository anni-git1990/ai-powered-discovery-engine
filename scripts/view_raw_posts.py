"""
Script to display Raw User Input posts across platforms with UTF-8 encoding.
"""
import sys

# Ensure UTF-8 output encoding for Windows terminal (handles Rupee symbol ₹)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.ingestion.pipeline import IngestionPipeline
from src.storage.db import DuckDBManager
from src.storage.vector_store import VectorStoreManager


def main():
    print("================================================================================")
    print("                      RAW USER INPUT POSTS & REVIEWS                            ")
    print("================================================================ shower =================\n")

    db_manager = DuckDBManager(db_path=":memory:")
    vector_manager = VectorStoreManager(persist_directory=":memory:", collection_name="raw_posts_view")

    pipeline = IngestionPipeline(db_manager=db_manager, vector_manager=vector_manager)
    processed_count, _ = pipeline.run(limit_per_source=10)

    raw_posts = db_manager.get_all_raw_posts()

    current_platform = None
    for idx, post in enumerate(raw_posts, 1):
        if post.source_platform.value != current_platform:
            current_platform = post.source_platform.value
            print(f"\n==================== [ Platform: {current_platform} ] ====================")

        print(f"\n[{idx}] Post ID: {post.post_id}")
        print(f"    Raw Input Text: \"{post.raw_text}\"")
        if post.url:
            print(f"    URL           : {post.url}")
        print(f"    Engagement    : {post.upvotes} upvotes | {post.replies} replies")

    db_manager.close()
    print("\n================================================================================")
    print(f"Total Raw User Posts Displayed: {len(raw_posts)}")
    print("================================================================================")


if __name__ == "__main__":
    main()
