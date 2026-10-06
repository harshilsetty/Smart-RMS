import pytest
from app.rag.vector_store import LocalVectorStore
from app.rag.retriever import PolicyRetriever
from app.rag.context_builder import RAGContextBuilder
from app.ai.mock_provider import MockAIProvider
from app.privacy.policy_validator import PolicyValidator

def test_exact_policy_query_retrieval():
    """Verify exact policy query returns correct document with high relevance."""
    retriever = PolicyRetriever()
    query = "How do I challenge an error in continuous assessment marks?"
    sources = retriever.retrieve(query, department="Academic Affairs", limit=3)
    assert len(sources) > 0
    assert sources[0].document_id == "DOC-ACAD-001"
    assert "Clause 4.1" in sources[0].clause
    assert sources[0].relevance_score >= 0.70

def test_paraphrased_query_retrieval():
    """Verify paraphrased query without exact wording retrieves appropriate policy."""
    retriever = PolicyRetriever()
    query = "deadline for raising continuous assessment rubric discrepancies"
    sources = retriever.retrieve(query, department="Academic Affairs", limit=3)
    assert len(sources) > 0
    assert sources[0].document_id == "DOC-ACAD-001"
    assert sources[0].relevance_score >= 0.65

def test_department_aware_retrieval_priority():
    """Verify department filter prioritizes matching department without blinding relevance."""
    store = LocalVectorStore()
    query = "maintenance request for water leaking in room"
    
    # Query with Hostel Affairs
    hostel_results = store.search(query, department="Hostel Affairs", limit=3)
    assert len(hostel_results) > 0
    assert hostel_results[0]["department"] == "Hostel Affairs"

def test_version_selection_prefers_latest_approved():
    """Verify superseded version (v1.0) is ignored when active v2.0 exists."""
    store = LocalVectorStore()
    # Search specifically for continuous assessment
    results = store.search("continuous assessment grievance timeline", department="Academic Affairs", limit=5)
    for r in results:
        if r["canonical_document_id"] == "DOC-ACAD-001":
            assert r["document_version"] == "2.0"
            assert "superseded" not in r["excerpt"].lower()

def test_expired_and_draft_documents_excluded_by_default():
    """Verify expired and draft documents are excluded from active retrieval."""
    store = LocalVectorStore()
    results = store.search("test policy document", active_only=True, limit=10)
    retrieved_ids = [r["document_id"] for r in results]
    assert "DOC-TEST-EXP-099" not in retrieved_ids
    assert "DOC-TEST-DFT-098" not in retrieved_ids

def test_top_k_parameter_honored():
    """Verify top_k parameter strictly controls candidate count."""
    store = LocalVectorStore()
    res1 = store.search("hostel rules", limit=1)
    res3 = store.search("hostel rules", limit=3)
    assert len(res1) <= 1
    assert len(res3) <= 3

def test_no_source_no_answer_refusal():
    """Verify completely out-of-domain query refuses to answer and flags INSUFFICIENT_EVIDENCE."""
    builder = RAGContextBuilder(default_threshold=0.65)
    unrelated_query = "Where can I buy second-hand fiction novels on campus?"
    context = builder.build_context(unrelated_query)
    
    assert context.grounding_status == "INSUFFICIENT_EVIDENCE"
    assert context.needs_human_review is True
    assert "No approved policy crossed the confidence threshold" in (context.refusal_reason or "")
    assert context.context_text == ""

@pytest.mark.asyncio
async def test_end_to_end_grounded_rag_pipeline():
    """Full lifecycle: Query -> Retrieval -> ContextBuilder -> AI Draft -> Human Review boundary."""
    retriever = PolicyRetriever()
    builder = RAGContextBuilder(retriever=retriever)
    ai_provider = MockAIProvider()
    validator = PolicyValidator()
    
    subject = "Emergency hall ticket clearance override"
    desc = "My library clearance was delayed and admit card is blocked before tomorrow morning exam."
    dept = "Examination Branch"
    
    # 1. Retrieve & Build Context
    context = builder.build_context(f"{subject} {desc}", department=dept, top_k=3, min_threshold=0.65)
    assert context.grounding_status == "GROUNDED"
    assert len(context.sources) > 0
    assert context.sources[0].document_id == "DOC-EXAM-001"
    
    # 2. Validate source
    is_valid, reasons = validator.validate_source(context.sources[0])
    assert is_valid is True
    assert len(reasons) == 0
    
    # 3. Generate grounded draft
    draft = await ai_provider.generate_draft(subject, desc, context.sources, dept)
    assert draft.confidence >= 0.70
    assert draft.grounding_status == "GROUNDED"
    assert draft.requires_staff_edit is False
    assert "Examination" in draft.draft_response
    assert "DOC-EXAM-001" in draft.sources[0].document_id
    
    # 4. Human-in-the-loop review boundary
    assert draft.disclaimer == "AI assists. Humans decide. Please review and verify before approving."

def test_source_citation_traceability():
    """Verify source citations contain complete provenance metadata."""
    retriever = PolicyRetriever()
    sources = retriever.retrieve("water leak near electrical switchboard", department="Hostel Affairs", limit=1)
    assert len(sources) > 0
    src = sources[0]
    assert src.document_id in {"DOC-HOSTEL-001", "DOC-2024-HOSTEL-01"}
    assert src.document_version is not None
    assert src.clause is not None
    assert src.chunk_id is not None
    assert src.relevance_score > 0.0
