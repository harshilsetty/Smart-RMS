"""
Semantic document chunker for Smart RMS policy documents.
Chunks by document sections, clauses, and logical paragraphs without splitting sentences.
"""

import re
from typing import List, Dict, Any, Union
from app.schemas.contracts import KnowledgeDocument, KnowledgeChunk, KnowledgeSection

class SemanticDocumentChunker:
    """
    Semantic chunker designed for statutory and university policy documents.
    Preserves clause references, headings, and context boundaries.
    """

    DEFAULT_MAX_CHUNK_WORDS = 85
    DEFAULT_MIN_CHUNK_WORDS = 20

    @classmethod
    def chunk_document(
        cls,
        document: Union[KnowledgeDocument, Dict[str, Any]],
        max_chunk_words: int = DEFAULT_MAX_CHUNK_WORDS
    ) -> List[KnowledgeChunk]:
        """
        Decomposes a KnowledgeDocument into semantic, contextual KnowledgeChunk units.
        """
        if isinstance(document, dict):
            doc = KnowledgeDocument(**document)
        else:
            doc = document

        chunks: List[KnowledgeChunk] = []

        # If document has explicit structured sections, chunk each section
        if doc.sections:
            for s_idx, section in enumerate(doc.sections, start=1):
                section_chunks = cls._chunk_section(doc, section, s_idx, max_chunk_words)
                chunks.extend(section_chunks)
        elif doc.content:
            # Fallback if only unstructured content is provided
            synth_section = KnowledgeSection(
                section_id=f"{doc.document_id}-S1",
                heading=doc.title,
                clause=doc.clause or "General Regulation",
                content=doc.content,
                keywords=doc.keywords
            )
            chunks.extend(cls._chunk_section(doc, synth_section, 1, max_chunk_words))

        return chunks

    @classmethod
    def _chunk_section(
        cls,
        doc: KnowledgeDocument,
        section: KnowledgeSection,
        section_idx: int,
        max_chunk_words: int
    ) -> List[KnowledgeChunk]:
        raw_text = section.content.strip()
        # Split on paragraph boundaries first, then sentence boundary
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", raw_text) if p.strip()]
        if not paragraphs:
            paragraphs = [raw_text]

        section_chunks: List[KnowledgeChunk] = []
        chunk_counter = 1

        for paragraph in paragraphs:
            words = paragraph.split()
            if len(words) <= max_chunk_words:
                # Whole paragraph fits comfortably in one chunk
                chunk = cls._create_chunk(doc, section, paragraph, section_idx, chunk_counter)
                section_chunks.append(chunk)
                chunk_counter += 1
            else:
                # Split paragraph by sentences
                sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", paragraph) if s.strip()]
                curr_sentences: List[str] = []
                curr_len = 0

                for s in sentences:
                    s_len = len(s.split())
                    if curr_len + s_len > max_chunk_words and curr_sentences:
                        combined_text = " ".join(curr_sentences)
                        chunk = cls._create_chunk(doc, section, combined_text, section_idx, chunk_counter)
                        section_chunks.append(chunk)
                        chunk_counter += 1
                        curr_sentences = [s]
                        curr_len = s_len
                    else:
                        curr_sentences.append(s)
                        curr_len += s_len

                if curr_sentences:
                    combined_text = " ".join(curr_sentences)
                    chunk = cls._create_chunk(doc, section, combined_text, section_idx, chunk_counter)
                    section_chunks.append(chunk)
                    chunk_counter += 1

        return section_chunks

    @classmethod
    def _create_chunk(
        cls,
        doc: KnowledgeDocument,
        section: KnowledgeSection,
        content_text: str,
        section_idx: int,
        chunk_idx: int
    ) -> KnowledgeChunk:
        version_clean = doc.version.replace(".", "").upper()
        chunk_id = f"{doc.document_id}-V{version_clean}-S{section_idx}-C{chunk_idx}"
        
        # Merge section and document keywords
        combined_keywords = list(dict.fromkeys(section.keywords + doc.keywords))

        # Build clean excerpt snippet
        words = content_text.split()
        excerpt = " ".join(words[:40]) + ("..." if len(words) > 40 else "")

        return KnowledgeChunk(
            chunk_id=chunk_id,
            document_id=doc.document_id,
            document_title=doc.title,
            document_version=doc.version,
            section_id=section.section_id,
            heading=section.heading,
            clause=section.clause,
            department_id=doc.department_id,
            department=doc.department,
            document_type=doc.document_type,
            approval_status=doc.approval_status,
            effective_date=doc.effective_date,
            expiry_date=doc.expiry_date,
            source=doc.source,
            content=content_text,
            excerpt=excerpt,
            keywords=combined_keywords,
            token_count=len(words)
        )
