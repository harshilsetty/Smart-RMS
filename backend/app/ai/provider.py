from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.schemas.rms import AIAnalysis, DraftResponse, RAGSource

class AIProvider(ABC):
    """Abstract interface for AI/LLM providers in Smart RMS."""

    @abstractmethod
    async def analyze_ticket(self, ticket_subject: str, ticket_description: str) -> AIAnalysis:
        """Analyzes ticket text to detect intent, department, priority, and extracted entities."""
        pass

    @abstractmethod
    async def generate_draft(
        self,
        ticket_subject: str,
        ticket_description: str,
        sources: List[RAGSource],
        department: str
    ) -> DraftResponse:
        """Generates a grounded draft response citing the provided RAG sources."""
        pass
