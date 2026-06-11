"""
Tests for the Legal AST module.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.legal_ast import (
    DocumentNode,
    SectionNode,
    ClauseNode,
    VariableNode,
    LegalASTParser,
    NodeType,
    DocumentType,
)


class TestVariableNode:
    def test_create_variable(self):
        v = VariableNode(name="party_name", value="John Doe", var_type="party")
        assert v.name == "party_name"
        assert v.value == "John Doe"
        assert not v.is_anonymized

    def test_anonymize_variable(self):
        v = VariableNode(name="party_name", value="John Doe", var_type="party")
        anon = v.anonymize()
        assert anon.is_anonymized
        assert anon.value == "[PARTY_NAME]"
        assert anon.anonymized_token == "[PARTY_NAME]"


class TestClauseNode:
    def test_substitute_variables(self):
        clause = ClauseNode(
            clause_type="jurisdiction",
            content="Filed by {party_name} in {court_name}",
            variables=[
                VariableNode(name="party_name", value="John Doe", var_type="party"),
                VariableNode(name="court_name", value="Nagpur District Court", var_type="jurisdiction"),
            ],
        )
        result = clause.substitute_variables()
        assert "John Doe" in result
        assert "Nagpur District Court" in result
        assert "{party_name}" not in result


class TestDocumentNode:
    def test_auto_generates_matter_id(self):
        doc = DocumentNode(document_type="affidavit", jurisdiction="MH-DISTRICT")
        assert doc.matter_id.startswith("CLY-")
        assert len(doc.matter_id) == 12  # CLY- + 8 hex chars

    def test_auto_generates_timestamp(self):
        doc = DocumentNode(document_type="affidavit", jurisdiction="MH-DISTRICT")
        assert doc.created_at.endswith("Z")

    def test_get_missing_mandatory_sections(self):
        doc = DocumentNode(document_type="affidavit", jurisdiction="MH-DISTRICT")
        doc.sections.append(SectionNode(section_type="facts", title="FACTS"))
        missing = doc.get_missing_mandatory_sections(["facts", "prayer", "verification"])
        assert "facts" not in missing
        assert "prayer" in missing
        assert "verification" in missing

    def test_render(self):
        doc = DocumentNode(document_type="affidavit", jurisdiction="MH-DISTRICT")
        doc.sections.append(SectionNode(
            section_type="facts",
            title="FACTS",
            clauses=[ClauseNode(clause_type="facts", content="The respondent did X.", order=0)],
            order=0,
        ))
        text = doc.render()
        assert "FACTS" in text
        assert "The respondent did X." in text


class TestLegalASTParser:
    def test_parse_simple_document(self):
        parser = LegalASTParser()
        raw = """IN THE COURT OF THE CIVIL JUDGE
Nagpur

Some case header info

FACTS

The respondent failed to pay rent for 6 months.

PRAYER

Grant eviction order.

VERIFICATION

I hereby verify that the above is true.
"""
        doc = parser.parse(raw, "affidavit", "MH-DISTRICT")
        assert doc.document_type == "affidavit"
        assert doc.jurisdiction == "MH-DISTRICT"
        assert len(doc.sections) >= 3

        section_types = [s.section_type for s in doc.sections]
        assert "facts" in section_types
        assert "prayer" in section_types
        assert "verification" in section_types

    def test_serialize_deserialize_roundtrip(self):
        parser = LegalASTParser()
        doc = DocumentNode(
            document_type="nda",
            jurisdiction="DL-DISTRICT",
            sections=[
                SectionNode(
                    section_type="facts",
                    title="FACTS",
                    clauses=[
                        ClauseNode(
                            clause_type="facts",
                            content="Test content",
                            citations=["CPC S.9"],
                            risk_score=0.3,
                        )
                    ],
                    order=0,
                )
            ],
        )
        serialized = parser.serialize(doc)
        assert isinstance(serialized, dict)
        assert serialized["document_type"] == "nda"
        assert len(serialized["sections"]) == 1

    def test_to_prompt_schema(self):
        parser = LegalASTParser()
        doc = DocumentNode(
            document_type="affidavit",
            jurisdiction="MH-DISTRICT",
            sections=[
                SectionNode(
                    section_type="facts",
                    title="FACTS",
                    clauses=[ClauseNode(clause_type="facts", content="Content here", order=0)],
                    order=0,
                )
            ],
        )
        schema = parser.to_prompt_schema(doc)
        assert "DOC_TYPE: affidavit" in schema
        assert "JURISDICTION: MH-DISTRICT" in schema
        assert "facts" in schema
