import os
from typing import List
from app.ai.provider import AIProvider
from app.ai.mock_provider import MockAIProvider
from app.schemas.rms import AIAnalysis, DraftResponse, RAGSource

class GeminiProvider(AIProvider):
    """Google Gemini AI Provider implementation with fallback to Mock."""

    def __init__(self, api_key: str = "", model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name
        self.fallback = MockAIProvider()

    async def analyze_ticket(self, ticket_subject: str, ticket_description: str) -> AIAnalysis:
        if not self.api_key:
            # Gracefully fallback if key is not yet set in environment
            return await self.fallback.analyze_ticket(ticket_subject, ticket_description)

        # Conceptual implementation for Gemini via HTTP or official SDK
        # When key is configured, prompt Gemini with structured JSON schema
        try:
            # Placeholder for SDK invocation
            return await self.fallback.analyze_ticket(ticket_subject, ticket_description)
        except Exception:
            return await self.fallback.analyze_ticket(ticket_subject, ticket_description)

    async def generate_draft(
        self,
        ticket_subject: str,
        ticket_description: str,
        sources: List[RAGSource],
        department: str
    ) -> DraftResponse:
        if not self.api_key:
            return await self.fallback.generate_draft(ticket_subject, ticket_description, sources, department)

        try:
            return await self.fallback.generate_draft(ticket_subject, ticket_description, sources, department)
        except Exception:
            return await self.fallback.generate_draft(ticket_subject, ticket_description, sources, department)
