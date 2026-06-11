"""
Clausely Legal AST — Abstract Syntax Tree for Legal Documents.

Represents legal documents as structured, typed trees — making Clausely
a compiler rather than a chatbot. Each document is parsed into nodes
that can be validated, serialized, and transformed deterministically.
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class NodeType(Enum):
    """Types of nodes in a Legal AST."""
    DOCUMENT = "document"
    SECTION = "section"
    CLAUSE = "clause"
    VARIABLE = "variable"
    ANNEXURE = "annexure"


class DocumentType(Enum):
    """Supported legal document types."""
    AFFIDAVIT = "affidavit"
    PETITION = "petition"
    WRIT_PETITION = "writ_petition"
    AGREEMENT = "agreement"
    NDA = "nda"
    LEGAL_NOTICE = "legal_notice"
    RENT_AGREEMENT = "rent_agreement"
    BAIL_APPLICATION = "bail_application"
    COMPLAINT = "complaint"


class VariableType(Enum):
    """Types of variables embedded in legal clauses."""
    PARTY = "party"
    AMOUNT = "amount"
    DATE = "date"
    JURISDICTION = "jurisdiction"
    ADDRESS = "address"
    STATUTE = "statute"
    CUSTOM = "custom"


# ---------------------------------------------------------------------------
# AST Node Definitions
# ---------------------------------------------------------------------------

@dataclass
class VariableNode:
    """A typed variable placeholder within a legal clause."""
    name: str
    value: str
    var_type: str  # VariableType value
    is_anonymized: bool = False
    anonymized_token: str = ""  # e.g., "[PARTY_A]"

    def anonymize(self) -> "VariableNode":
        """Return a copy with value replaced by anonymized token."""
        token = self.anonymized_token or f"[{self.name.upper()}]"
        return VariableNode(
            name=self.name,
            value=token,
            var_type=self.var_type,
            is_anonymized=True,
            anonymized_token=token,
        )


@dataclass
class ClauseNode:
    """A single clause in a legal document."""
    clause_type: str  # e.g., "jurisdiction", "verification", "indemnification"
    content: str
    variables: List[VariableNode] = field(default_factory=list)
    risk_score: float = 0.0
    citations: List[str] = field(default_factory=list)
    is_mandatory: bool = False
    order: int = 0

    def substitute_variables(self) -> str:
        """Replace variable placeholders in content with actual values."""
        text = self.content
        for var in self.variables:
            placeholder = f"{{{var.name}}}"
            replacement = var.anonymized_token if var.is_anonymized else var.value
            text = text.replace(placeholder, replacement)
        return text


@dataclass
class SectionNode:
    """A section grouping multiple clauses (e.g., 'facts', 'grounds')."""
    section_type: str
    title: str
    clauses: List[ClauseNode] = field(default_factory=list)
    order: int = 0
    is_mandatory: bool = False

    def render(self) -> str:
        """Render section as formatted text."""
        lines = [self.title.upper(), ""]
        for clause in sorted(self.clauses, key=lambda c: c.order):
            lines.append(clause.substitute_variables())
            lines.append("")
        return "\n".join(lines)


@dataclass
class DocumentNode:
    """Root node of a Legal AST — represents a complete legal document."""
    document_type: str  # DocumentType value
    jurisdiction: str   # e.g., "MH-DISTRICT", "IN-SC"
    corpus_version: str = "BNS-2024-v1"
    template_id: str = ""
    sections: List[SectionNode] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    acceptance_score: float = 0.0
    created_at: str = ""
    matter_id: str = ""

    def __post_init__(self):
        if not self.matter_id:
            self.matter_id = f"CLY-{uuid.uuid4().hex[:8].upper()}"
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat() + "Z"

    def get_all_clauses(self) -> List[ClauseNode]:
        """Flatten all clauses from all sections."""
        clauses: List[ClauseNode] = []
        for section in self.sections:
            clauses.extend(section.clauses)
        return clauses

    def get_section(self, section_type: str) -> Optional[SectionNode]:
        """Find a section by type."""
        for section in self.sections:
            if section.section_type == section_type:
                return section
        return None

    def render(self) -> str:
        """Render the full document as text."""
        parts: List[str] = []
        for section in sorted(self.sections, key=lambda s: s.order):
            parts.append(section.render())
        return "\n\n".join(parts)

    def get_missing_mandatory_sections(self, required: List[str]) -> List[str]:
        """Check which mandatory sections are missing."""
        present = {s.section_type for s in self.sections}
        return [r for r in required if r not in present]


# ---------------------------------------------------------------------------
# AST Parser — converts LLM output → structured AST
# ---------------------------------------------------------------------------

class LegalASTParser:
    """Converts raw LLM-generated text into a structured Legal AST."""

    # Heuristic section header patterns (Indian legal style)
    SECTION_PATTERNS = {
        "cause_title": r"(?i)^(?:IN THE COURT|CAUSE TITLE)",
        "jurisdiction_clause": r"(?i)^(?:JURISDICTION|This .+ court has jurisdiction)",
        "facts": r"(?i)^(?:FACTS|STATEMENT OF FACTS)",
        "grounds": r"(?i)^(?:GROUNDS|The .+ is filed on the following grounds)",
        "prayer": r"(?i)^(?:PRAYER|RELIEF SOUGHT|WHEREFORE)",
        "verification": r"(?i)^(?:VERIFICATION|I .+ do hereby verify)",
        "deponent_signature": r"(?i)^(?:DEPONENT|SIGNATURE|SIGNED)",
        "synopsis_and_list_of_dates": r"(?i)^(?:SYNOPSIS|LIST OF DATES)",
        "questions_of_law": r"(?i)^(?:QUESTIONS OF LAW)",
        "advocate_signature": r"(?i)^(?:ADVOCATE|THROUGH ADVOCATE|COUNSEL)",
        "advocate_on_record_signature": r"(?i)^(?:ADVOCATE.ON.RECORD)",
    }

    def parse(
        self,
        raw_text: str,
        document_type: str,
        jurisdiction: str,
    ) -> DocumentNode:
        """Parse raw LLM-generated text into a DocumentNode AST."""
        doc = DocumentNode(
            document_type=document_type,
            jurisdiction=jurisdiction,
        )

        # Split text into candidate sections by double-newline blocks
        blocks = re.split(r"\n{2,}", raw_text.strip())

        current_section_type = "preamble"
        current_title = "PREAMBLE"
        current_clauses: List[ClauseNode] = []
        section_order = 0

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            # Check if this block starts a new section
            matched_section = None
            for stype, pattern in self.SECTION_PATTERNS.items():
                if re.search(pattern, block.split("\n")[0]):
                    matched_section = stype
                    break

            if matched_section:
                # Save previous section
                if current_clauses:
                    doc.sections.append(SectionNode(
                        section_type=current_section_type,
                        title=current_title,
                        clauses=current_clauses,
                        order=section_order,
                    ))
                    section_order += 1
                    current_clauses = []

                current_section_type = matched_section
                current_title = block.split("\n")[0].strip()
                # Everything after the header is clause content
                remaining = "\n".join(block.split("\n")[1:]).strip()
                if remaining:
                    current_clauses.append(ClauseNode(
                        clause_type=current_section_type,
                        content=remaining,
                        order=len(current_clauses),
                    ))
            else:
                # Continuation of current section
                current_clauses.append(ClauseNode(
                    clause_type=current_section_type,
                    content=block,
                    order=len(current_clauses),
                ))

        # Final section
        if current_clauses:
            doc.sections.append(SectionNode(
                section_type=current_section_type,
                title=current_title,
                clauses=current_clauses,
                order=section_order,
            ))

        return doc

    def serialize(self, node: DocumentNode) -> dict:
        """Convert a DocumentNode AST to a JSON-serializable dict."""
        return asdict(node)

    def deserialize(self, data: dict) -> DocumentNode:
        """Reconstruct a DocumentNode from a serialized dict."""
        sections = []
        for sec_data in data.get("sections", []):
            clauses = []
            for cl_data in sec_data.get("clauses", []):
                variables = [VariableNode(**v) for v in cl_data.get("variables", [])]
                cl_data_copy = {k: v for k, v in cl_data.items() if k != "variables"}
                clauses.append(ClauseNode(**cl_data_copy, variables=variables))
            sec_data_copy = {k: v for k, v in sec_data.items() if k != "clauses"}
            sections.append(SectionNode(**sec_data_copy, clauses=clauses))

        doc_data = {k: v for k, v in data.items() if k != "sections"}
        return DocumentNode(**doc_data, sections=sections)

    def to_prompt_schema(self, node: DocumentNode) -> str:
        """Convert AST to a compact, token-efficient schema for LLM context injection."""
        lines = [
            f"DOC_TYPE: {node.document_type}",
            f"JURISDICTION: {node.jurisdiction}",
            f"CORPUS: {node.corpus_version}",
            f"MATTER_ID: {node.matter_id}",
            f"SECTIONS ({len(node.sections)}):",
        ]
        for section in sorted(node.sections, key=lambda s: s.order):
            lines.append(f"  [{section.order}] {section.section_type}: {section.title}")
            for clause in section.clauses:
                clause_summary = clause.content[:80].replace("\n", " ")
                citations = ", ".join(clause.citations) if clause.citations else "none"
                lines.append(
                    f"    - {clause.clause_type} "
                    f"(risk={clause.risk_score:.1f}, cites={citations}): "
                    f"{clause_summary}..."
                )
        return "\n".join(lines)
