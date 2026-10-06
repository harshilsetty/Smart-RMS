# Knowledge Ingestion Pipeline

## 1. Overview
The knowledge ingestion pipeline processes raw synthetic university policy documents into validated, version-controlled semantic chunks indexed for vector retrieval.

## 2. Ingestion Flow
```
Raw Policy Document (JSON)
          ↓
Schema Validation (Pydantic V2 KnowledgeDocument)
          ↓
Active & Approval Status Filtering
          ↓
Semantic Chunking (by Clause / Section)
          ↓
Dense Embedding Generation (384-d normalized vector)
          ↓
Local Vector Store Indexing
          ↓
Persistence to Disk (knowledge_index.json)
```

## 3. Execution CLI

The ingestion pipeline can be executed independently of the API:

```bash
python scripts/ingest_knowledge.py
```

### Verified Run Measurements:
- **Total Documents Loaded**: 11
- **Approved Documents Indexed**: 8
- **Superseded / Expired / Draft Filtered**: 3 (v1.0 superseded, expired policy, unapproved draft)
- **Sections Processed**: 24
- **Semantic Chunks Created**: 21
- **Embeddings Generated**: 21
- **Index Build Duration**: 0.007s
