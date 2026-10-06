"""
Standalone CLI script to ingest, validate, chunk, embed, and index synthetic university policies.
Usage:
    python scripts/ingest_knowledge.py [--all]
"""

import sys
import argparse
from pathlib import Path

# Add backend directory to sys.path so app imports work
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.rag.ingestion import KnowledgeIngestionPipeline

def main():
    parser = argparse.ArgumentParser(description="Ingest, chunk, embed, and index synthetic university policies.")
    parser.add_argument("--include-inactive", action="store_true", help="Include inactive/unapproved documents in index")
    args = parser.parse_args()

    print("[*] Starting Smart RMS Policy Knowledge Ingestion Pipeline...")
    pipeline = KnowledgeIngestionPipeline()
    stats = pipeline.run(filter_approved_only=not args.include_inactive)

    print("\n" + "=" * 55)
    print("       SMART RMS KNOWLEDGE INGESTION REPORT")
    print("=" * 55)
    print(f"Total Documents Loaded:        {stats['total_documents_loaded']}")
    print(f"Approved Documents Indexed:    {stats['approved_documents_indexed']}")
    print(f"Total Sections:                {stats['total_sections']}")
    print(f"Chunks Created:                {stats['total_chunks_created']}")
    print(f"Embeddings Generated:          {stats['total_embeddings_generated']}")
    print(f"Chunks Indexed:                {stats['total_indexed']}")
    print(f"Embedding Provider:            {stats['embedding_provider']} ({stats['embedding_dimension']}-d)")
    print(f"Index Saved To:                {stats['index_path']}")
    print("=" * 55)
    print("[+] Ingestion & vector indexing complete.\n")

if __name__ == "__main__":
    main()
