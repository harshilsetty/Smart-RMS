# Semantic Chunking & Embedding System

## 1. Semantic Chunking Strategy

Traditional RAG systems split text arbitrarily every $N$ characters, fragmenting statutory policy clauses and destroying contextual meaning. Smart RMS implements `SemanticDocumentChunker`:

- **Section-Level Boundaries**: Splits documents strictly along designated sections and statutory clauses.
- **Clause Preservation**: Preserves the full clause identifier (e.g. `Clause 4.1 (Continuous Assessment Discrepancy Redressal)`).
- **Metadata Attachment**: Every chunk embeds statutory metadata:
  - `chunk_id`
  - `document_id`
  - `document_title`
  - `document_version`
  - `clause`
  - `department`
  - `approval_status`
  - `effective_date`
  - `expiry_date`

## 2. Embedding System

Embedding generation implements the abstract `EmbeddingProvider` interface:

```python
class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]: ...
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]: ...
```

### Implementations:
1. **`DeterministicLocalEmbeddingProvider`** (Default):
   - 384-dimensional dense normalized vector.
   - Dual-hash architecture: Word token hashing + sub-word character 3-gram hashing.
   - Domain synonym normalization table mapping university terminology (e.g. `hall ticket` &rarr; `admit card`, `re-evaluation` &rarr; `reevaluation`).
   - 100% deterministic, offline-first, sub-millisecond execution.
2. **`SentenceTransformerEmbeddingProvider`**:
   - Backed by HuggingFace / PyTorch using `sentence-transformers/all-MiniLM-L6-v2`.
