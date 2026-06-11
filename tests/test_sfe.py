"""
Tests for the Symbolic Formatting Engine (SFE).
"""

import json
import sys
from pathlib import Path

import pytest

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.sfe import SymbolicFormattingEngine, ValidationResult


class TestSFEInitialization:
    """Test SFE loads court rules correctly."""

    def test_load_mh_district(self):
        sfe = SymbolicFormattingEngine("MH-DISTRICT")
        assert sfe.jurisdiction == "MH-DISTRICT"
        assert sfe.rules["court_name"] == "Maharashtra District Court"
        assert sfe.rules["margin_left_cm"] == 3.0
        assert sfe.rules["font_body"] == "Times New Roman"

    def test_load_mh_hc(self):
        sfe = SymbolicFormattingEngine("MH-HC")
        assert sfe.rules["court_name"] == "Bombay High Court"
        assert sfe.rules["line_spacing"] == 2.0

    def test_load_dl_district(self):
        sfe = SymbolicFormattingEngine("DL-DISTRICT")
        assert sfe.rules["court_name"] == "Delhi District Court"

    def test_load_in_sc(self):
        sfe = SymbolicFormattingEngine("IN-SC")
        assert sfe.rules["court_name"] == "Supreme Court of India"
        assert "questions_of_law" in sfe.rules["required_sections"]

    def test_unsupported_jurisdiction(self):
        with pytest.raises(ValueError, match="Unsupported jurisdiction"):
            SymbolicFormattingEngine("XX-UNKNOWN")

    def test_supported_jurisdictions(self):
        jurisdictions = SymbolicFormattingEngine.supported_jurisdictions()
        assert "MH-DISTRICT" in jurisdictions
        assert "IN-SC" in jurisdictions
        assert len(jurisdictions) == 4


class TestSFEValidation:
    """Test document validation against court rules."""

    def _make_valid_document(self, jurisdiction="MH-DISTRICT"):
        sfe = SymbolicFormattingEngine(jurisdiction)
        sections = {sec: f"Content for {sec}" for sec in sfe.rules["required_sections"]}
        return {
            "sections": sections,
            "metadata": {"stamp_paper_value": sfe.rules.get("stamp_paper_value", "0")},
            "formatting": {
                "margin_left_cm": sfe.rules["margin_left_cm"],
                "margin_right_cm": sfe.rules["margin_right_cm"],
                "margin_top_cm": sfe.rules["margin_top_cm"],
                "margin_bottom_cm": sfe.rules["margin_bottom_cm"],
                "font_body": sfe.rules["font_body"],
                "font_size_body": sfe.rules["font_size_body"],
                "line_spacing": sfe.rules["line_spacing"],
            },
        }

    def test_valid_document_passes(self):
        sfe = SymbolicFormattingEngine("MH-DISTRICT")
        doc = self._make_valid_document("MH-DISTRICT")
        result = sfe.validate(doc)
        assert result.is_valid
        assert result.acceptance_score >= 85

    def test_missing_section_fatal(self):
        sfe = SymbolicFormattingEngine("MH-DISTRICT")
        doc = self._make_valid_document("MH-DISTRICT")
        del doc["sections"]["cause_title"]
        result = sfe.validate(doc)
        assert "Missing required section: cause_title" in result.fatal_defects

    def test_wrong_margins_fatal(self):
        sfe = SymbolicFormattingEngine("MH-DISTRICT")
        doc = self._make_valid_document("MH-DISTRICT")
        doc["formatting"]["margin_left_cm"] = 1.0  # Way off
        result = sfe.validate(doc)
        assert any("margin" in d.lower() for d in result.fatal_defects)

    def test_wrong_font_curable(self):
        sfe = SymbolicFormattingEngine("MH-DISTRICT")
        doc = self._make_valid_document("MH-DISTRICT")
        doc["formatting"]["font_body"] = "Arial"
        result = sfe.validate(doc)
        assert any("font" in d.lower() for d in result.curable_defects)

    def test_wrong_stamp_paper_fatal(self):
        sfe = SymbolicFormattingEngine("MH-DISTRICT")
        doc = self._make_valid_document("MH-DISTRICT")
        doc["metadata"]["stamp_paper_value"] = "50"  # Should be 100
        result = sfe.validate(doc)
        assert any("stamp" in d.lower() for d in result.fatal_defects)


class TestSFEEnforce:
    """Test formatting enforcement."""

    def test_enforce_adds_header(self):
        sfe = SymbolicFormattingEngine("MH-DISTRICT")
        metadata = {
            "court_designation": "Civil Judge Senior Division",
            "city_name": "Nagpur",
            "case_type": "Civil Suit",
            "case_number": "123",
            "year": "2026",
        }
        result = sfe.enforce("Test content here", metadata)
        assert "IN THE COURT OF THE Civil Judge Senior Division" in result
        assert "Test content here" in result

    def test_enforce_adds_footer(self):
        sfe = SymbolicFormattingEngine("MH-DISTRICT")
        result = sfe.enforce("Content", {"advocate_name": "John", "bar_number": "MH/123"})
        assert "Advocate: John" in result


class TestSFEExport:
    """Test PDF and DOCX export."""

    def _make_export_doc(self):
        return {
            "sections": {
                "cause_title": "Test Cause Title",
                "facts": "Test facts of the case.",
                "prayer": "Test prayer for relief.",
            },
            "metadata": {
                "court_designation": "Civil Judge",
                "city_name": "Nagpur",
                "case_type": "CS",
                "case_number": "1",
                "year": "2026",
            },
        }

    def test_export_pdf_returns_bytes(self):
        sfe = SymbolicFormattingEngine("MH-DISTRICT")
        pdf = sfe.export_pdf(self._make_export_doc())
        assert isinstance(pdf, bytes)
        assert len(pdf) > 100
        assert pdf[:5] == b"%PDF-"

    def test_export_docx_returns_bytes(self):
        sfe = SymbolicFormattingEngine("MH-DISTRICT")
        docx = sfe.export_docx(self._make_export_doc())
        assert isinstance(docx, bytes)
        assert len(docx) > 100
        # DOCX files start with PK (zip signature)
        assert docx[:2] == b"PK"


class TestSFESectionOrdering:
    """Test that sections are ordered per court rules."""

    def test_reorder_sections(self):
        sfe = SymbolicFormattingEngine("MH-DISTRICT")
        sections = {
            "prayer": "Prayer content",
            "cause_title": "Title content",
            "facts": "Facts content",
            "verification": "Verification content",
        }
        ordered = sfe.reorder_sections(sections)
        types = [t for t, _ in ordered]
        assert types.index("cause_title") < types.index("facts")
        assert types.index("facts") < types.index("prayer")
        assert types.index("prayer") < types.index("verification")


class TestSFELineFormatting:
    """Test line-level formatting, margins, and indentation validations."""

    def test_line_formatting_violations(self):
        sfe = SymbolicFormattingEngine("MH-HC")
        
        # Valid doc base
        sections = {sec: f"Content for {sec}" for sec in sfe.rules["required_sections"]}
        # Inject standard regular text lines and bulleted items
        sections["facts"] = "This is a regular line.\n  - This is an indented bullet item.\nHEADER LINE\n"
        
        doc = {
            "sections": sections,
            "metadata": {"stamp_paper_value": "0"},
            "formatting": {
                "margin_left_cm": 4.0,
                "margin_right_cm": 2.5,
                "margin_top_cm": 3.0,
                "margin_bottom_cm": 2.5,
                "font_body": "Times New Roman",
                "font_size_body": 14,
                "line_spacing": 2.0, # Double line spacing
            }
        }
        
        # Should pass initially
        res = sfe.validate(doc)
        assert res.is_valid
        
        # Assert line logs are populated in details
        logs = res.details.get("line_coordinates_logs", [])
        assert len(logs) > 0
        bullet_logs = [l for l in logs if l.get("type") == "bullet_item"]
        assert len(bullet_logs) == 1
        assert bullet_logs[0]["indentation_spaces"] == 2
        
        header_logs = [l for l in logs if l.get("type") == "header_line"]
        assert len(header_logs) == 1
        assert header_logs[0]["text"] == "HEADER LINE"

        # 1. Left margin deviation
        doc_bad_left = doc.copy()
        doc_bad_left["formatting"] = doc["formatting"].copy()
        doc_bad_left["formatting"]["margin_left_in"] = 1.0 # Deviation from 1.5 in
        res_bad_left = sfe.validate(doc_bad_left)
        assert not res_bad_left.is_valid
        assert any("MARGIN_VIOLATION" in d for d in res_bad_left.fatal_defects)

        # 2. Line spacing deviation
        doc_bad_spacing = doc.copy()
        doc_bad_spacing["formatting"] = doc["formatting"].copy()
        doc_bad_spacing["formatting"]["line_spacing"] = 1.0 # Deviation from 2.0
        res_bad_spacing = sfe.validate(doc_bad_spacing)
        assert not res_bad_spacing.is_valid
        assert any("MARGIN_VIOLATION" in d for d in res_bad_spacing.fatal_defects)

        # 3. Trailing spaces detection
        doc_trailing = doc.copy()
        doc_trailing["sections"] = doc["sections"].copy()
        doc_trailing["sections"]["facts"] = "Regular line with trailing space \nAnother line"
        res_trailing = sfe.validate(doc_trailing)
        assert any("TRAILING_SPACE" in d for d in res_trailing.curable_defects)

        # 4. Line wrap formatting defect detection (line exceeds 100 characters)
        doc_long = doc.copy()
        doc_long["sections"] = doc["sections"].copy()
        doc_long["sections"]["facts"] = "A" * 105
        res_long = sfe.validate(doc_long)
        assert any("LINE_WRAP" in d for d in res_long.curable_defects)

        # 5. Invalid Unicode character detection
        doc_unicode = doc.copy()
        doc_unicode["sections"] = doc["sections"].copy()
        doc_unicode["sections"]["facts"] = "This is a sentence with non-CP1252 character \u03a9"
        res_unicode = sfe.validate(doc_unicode)
        assert not res_unicode.is_valid
        assert any("FONT_VIOLATION_HALT" in d for d in res_unicode.fatal_defects)

        # 6. Non-black font color
        doc_color = doc.copy()
        doc_color["formatting"] = doc["formatting"].copy()
        doc_color["formatting"]["font_color"] = "red"
        res_color = sfe.validate(doc_color)
        assert not res_color.is_valid
        assert any("FONT_VIOLATION_HALT" in d for d in res_color.fatal_defects)

        # 7. Grammar / syntax score below threshold (SYNTAX_REWRITE)
        doc_syntax = doc.copy()
        doc_syntax["sections"] = doc["sections"].copy()
        # Create a section where most lines are invalid (lowercase first char and double spaces)
        doc_syntax["sections"]["facts"] = "lower first character\n  another  invalid line  here\nvalid line starts capitalized"
        res_syntax = sfe.validate(doc_syntax)
        assert not res_syntax.is_valid
        assert any("SYNTAX_REWRITE" in d for d in res_syntax.fatal_defects)

        # 8. Date standardization warning
        doc_date = doc.copy()
        doc_date["sections"] = doc["sections"].copy()
        doc_date["sections"]["facts"] = "The event happened on 12/05/2026."
        res_date = sfe.validate(doc_date)
        assert any("DATE_STANDARDIZATION" in d for d in res_date.curable_defects)

        # 9. Broken numbering sequence
        doc_num = doc.copy()
        doc_num["sections"] = doc["sections"].copy()
        doc_num["sections"]["facts"] = "1. First fact.\n3. Third fact."
        res_num = sfe.validate(doc_num)
        assert not res_num.is_valid
        assert any("PAGINATION_ANOMALY" in d for d in res_num.fatal_defects)

        # 10. Footnote sequence anomaly
        doc_footnote = doc.copy()
        doc_footnote["sections"] = doc["sections"].copy()
        doc_footnote["sections"]["facts"] = "First point [^1]\nSecond point [^3]"
        res_footnote = sfe.validate(doc_footnote)
        assert not res_footnote.is_valid
        assert any("PAGINATION_ANOMALY" in d for d in res_footnote.fatal_defects)

        # 11. Table column count mismatch
        doc_table = doc.copy()
        doc_table["sections"] = doc["sections"].copy()
        doc_table["sections"]["facts"] = "| Col 1 | Col 2 |\n| Row 1 |\n| Row 2 | Col 2 |"
        res_table = sfe.validate(doc_table)
        assert any("ALIGNMENT_ANOMALY" in d for d in res_table.curable_defects)

        # 12. Tab indentation warning
        doc_tab = doc.copy()
        doc_tab["sections"] = doc["sections"].copy()
        doc_tab["sections"]["facts"] = "\tThis line has tab indentation."
        res_tab = sfe.validate(doc_tab)
        assert any("TAB_INDENTATION" in d for d in res_tab.curable_defects)
