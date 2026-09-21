import pytest
from app.ai.mock_provider import MockAIProvider
from app.rag.retriever import PolicyRetriever

@pytest.mark.asyncio
async def test_mock_ai_analysis():
    provider = MockAIProvider()
    subject = "Air conditioner leaking water in room"
    desc = "My AC unit in BH-4 is leaking continuously. Phone: 9876543210."
    analysis = await provider.analyze_ticket(subject, desc)
    
    assert analysis.intent == "HOSTEL_MAINTENANCE"
    assert analysis.suggested_department == "Hostel Affairs"
    assert analysis.priority_score >= 3
    assert analysis.confidence >= 0.8
    assert "[REDACTED_PHONE]" in analysis.pii_detected

@pytest.mark.asyncio
async def test_grounded_draft_generation():
    provider = MockAIProvider()
    retriever = PolicyRetriever()
    subject = "Admit card blocked due to library clearance"
    desc = "My admit card is blocked before tomorrow's exam."
    
    sources = retriever.retrieve(f"{subject} {desc}", department="Examination Branch")
    assert len(sources) > 0

    draft = await provider.generate_draft(subject, desc, sources, "Examination Branch")
    assert draft.confidence > 0.7
    assert len(draft.sources) > 0
    assert "Examination" in draft.draft_response
