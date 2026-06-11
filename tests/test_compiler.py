"""
Tests for the Clausely Compiler Engine.
"""

import sys
from pathlib import Path
import pytest

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.compiler import (
    CompilerEngine,
    CompilerError,
    TOCCompilationError,
    AnnexureAlignmentError,
    PDFAComplianceError,
    TOCEntry,
    AnnexureItem
)


class TestCompilerInitialization:
    """Test CompilerEngine initialization."""

    def test_init_valid_jurisdiction(self):
        compiler = CompilerEngine("MH-DISTRICT")
        assert compiler.jurisdiction == "MH-DISTRICT"
        assert compiler.sfe is not None


class TestTOCGeneration:
    """Test Table of Contents generation and validation."""

    def test_generate_toc_happy_path(self):
        compiler = CompilerEngine("MH-DISTRICT")
        sections = {
            "cause_title": "IN THE COURT OF...",
            "facts": "These are the facts of the case. Word count should determine page size.",
            "prayer": "Therefore, the petitioner prays..."
        }
        res = compiler.generate_toc(sections)
        assert res["is_aligned"]
        assert len(res["toc_entries"]) == 3
        # Sections should be ordered: cause_title, facts, prayer
        assert res["toc_entries"][0]["section_key"] == "cause_title"
        assert res["toc_entries"][1]["section_key"] == "facts"
        assert res["toc_entries"][2]["section_key"] == "prayer"
        
        # Verify page numbering monotonic increase
        pages = [entry["page_number"] for entry in res["toc_entries"]]
        assert pages == sorted(pages)
        assert len(set(pages)) == len(pages)

    def test_generate_toc_empty_sections(self):
        compiler = CompilerEngine("MH-DISTRICT")
        with pytest.raises(TOCCompilationError, match="sections dictionary is empty"):
            compiler.generate_toc({})

    def test_generate_toc_duplicate_headings(self):
        compiler = CompilerEngine("MH-DISTRICT")
        # Direct TOC compilation test with simulated duplicate entries
        # Since _compile_toc_entries reorders, we mock/force a scenario where duplicates exist.
        # Let's mock _compile_toc_entries to return duplicates.
        original_compile = compiler._compile_toc_entries
        try:
            compiler._compile_toc_entries = lambda secs: [
                TOCEntry("Facts", "facts", 1),
                TOCEntry("Facts", "facts_2", 2)
            ]
            with pytest.raises(TOCCompilationError, match="duplicate section titles detected"):
                compiler.generate_toc({"facts": "content", "facts_2": "content"})
        finally:
            compiler._compile_toc_entries = original_compile

    def test_generate_toc_non_monotonic_pages(self):
        compiler = CompilerEngine("MH-DISTRICT")
        original_compile = compiler._compile_toc_entries
        try:
            compiler._compile_toc_entries = lambda secs: [
                TOCEntry("Cause Title", "cause_title", 2),
                TOCEntry("Facts", "facts", 1)
            ]
            with pytest.raises(TOCCompilationError, match="TOC page number sequence is not monotonic"):
                compiler.generate_toc({"cause_title": "content", "facts": "content"})
        finally:
            compiler._compile_toc_entries = original_compile


class TestAnnexureAlignment:
    """Test annexure mapping, page count verification, and labeling checks."""

    def test_align_annexures_happy_path(self):
        compiler = CompilerEngine("MH-DISTRICT")
        body_text = "See Annexure A-1 for the contract and Exhibit B-2 for the proof."
        attachments = [
            {"label": "A-1", "filename": "contract.pdf", "description": "Contract document", "page_count": 5},
            {"label": "B-2", "filename": "proof.pdf", "description": "Evidence document", "page_count": 2}
        ]
        res = compiler.align_annexures(body_text, attachments)
        assert res["is_compliant"]
        assert len(res["aligned_items"]) == 2
        assert res["aligned_items"][0]["label"] == "A-1"
        assert res["aligned_items"][0]["start_page"] == 11
        assert res["aligned_items"][1]["label"] == "B-2"
        assert res["aligned_items"][1]["start_page"] == 16  # 11 + 5

    def test_align_annexures_empty_body(self):
        compiler = CompilerEngine("MH-DISTRICT")
        with pytest.raises(AnnexureAlignmentError, match="body text is empty"):
            compiler.align_annexures("", [])

    def test_align_annexures_missing_label(self):
        compiler = CompilerEngine("MH-DISTRICT")
        with pytest.raises(AnnexureAlignmentError, match="missing required field: 'label'"):
            compiler.align_annexures("Body Annexure-A", [{"filename": "doc.pdf", "page_count": 2}])

    def test_align_annexures_duplicate_label(self):
        compiler = CompilerEngine("MH-DISTRICT")
        with pytest.raises(AnnexureAlignmentError, match="Duplicate attachment label"):
            compiler.align_annexures(
                "Body Annexure-A",
                [
                    {"label": "A", "filename": "doc1.pdf", "page_count": 1},
                    {"label": "A", "filename": "doc2.pdf", "page_count": 2}
                ]
            )

    def test_align_annexures_missing_filename(self):
        compiler = CompilerEngine("MH-DISTRICT")
        with pytest.raises(AnnexureAlignmentError, match="missing required field: 'filename'"):
            compiler.align_annexures("Body Annexure-A", [{"label": "A", "page_count": 2}])

    def test_align_annexures_invalid_page_count(self):
        compiler = CompilerEngine("MH-DISTRICT")
        with pytest.raises(AnnexureAlignmentError, match="Invalid page_count"):
            compiler.align_annexures("Body Annexure-A", [{"label": "A", "filename": "a.pdf", "page_count": "invalid"}])
        with pytest.raises(AnnexureAlignmentError, match="page count must be greater than zero"):
            compiler.align_annexures("Body Annexure-A", [{"label": "A", "filename": "a.pdf", "page_count": 0}])

    def test_align_annexures_mismatch_referenced_but_missing(self):
        compiler = CompilerEngine("MH-DISTRICT")
        body_text = "See Annexure A-1 for detail."
        attachments = [{"label": "B-2", "filename": "b.pdf", "page_count": 2}]
        with pytest.raises(AnnexureAlignmentError, match="missing from attachments"):
            compiler.align_annexures(body_text, attachments)

    def test_align_annexures_mismatch_attachment_not_referenced(self):
        compiler = CompilerEngine("MH-DISTRICT")
        body_text = "No annexures referenced here."
        attachments = [{"label": "A-1", "filename": "a.pdf", "page_count": 2}]
        with pytest.raises(AnnexureAlignmentError, match="not referenced in document body"):
            compiler.align_annexures(body_text, attachments)


class TestOutputFormatting:
    """Test PDF/A e-filing output compliance checks."""

    def test_format_output_happy_path(self):
        compiler = CompilerEngine("MH-DISTRICT")
        pdf_bytes = b"%PDF-1.4\n%...\n/Type /Page\n/Creator (ReportLab PDF Library)\n/Producer (ReportLab PDF Library)\n/Author ()"
        res = compiler.format_output(pdf_bytes, {})
        assert res.startswith(b"%PDF-")
        assert b"/Creator ()" in res
        assert b"/Producer ()" in res

    def test_format_output_invalid_header(self):
        compiler = CompilerEngine("MH-DISTRICT")
        with pytest.raises(PDFAComplianceError, match="Invalid PDF format"):
            compiler.format_output(b"NOT A PDF", {})

    def test_format_output_zero_pages(self):
        compiler = CompilerEngine("MH-DISTRICT")
        pdf_bytes = b"%PDF-1.4\n%...\n/Type /Font"
        with pytest.raises(PDFAComplianceError, match="Total page count is 0"):
            compiler.format_output(pdf_bytes, {})

    def test_format_output_author_metadata_violation(self):
        compiler = CompilerEngine("MH-DISTRICT")
        pdf_bytes = b"%PDF-1.4\n%...\n/Type /Page\n/Author (John Doe)"
        with pytest.raises(PDFAComplianceError, match="User identifier/Author metadata found"):
            compiler.format_output(pdf_bytes, {})


class TestRenderAssets:
    """Test render_assets complete integration."""

    def test_render_assets_invalid_ast(self):
        compiler = CompilerEngine("MH-DISTRICT")
        with pytest.raises(CompilerError, match="Invalid AST"):
            compiler.render_assets({}, {"court_designation": "Civil Judge"})

    def test_render_assets_invalid_metadata(self):
        compiler = CompilerEngine("MH-DISTRICT")
        with pytest.raises(CompilerError, match="Invalid metadata"):
            compiler.render_assets({"sections": {"cause_title": "Content"}}, {})

    def test_render_assets_formatting_validation_failure(self):
        compiler = CompilerEngine("MH-DISTRICT")
        ast = {
            "sections": {"cause_title": "Content"},
            "formatting": {"margin_left_cm": 0.5}  # Invalid margin left for district court
        }
        metadata = {
            "court_designation": "Civil Judge",
            "city_name": "Nagpur",
            "case_type": "Civil Suit",
            "case_number": "123",
            "year": "2026",
            "stamp_paper_value": "100",
            "notarized": True
        }
        # pre-flight formatting checks should fail on invalid margins
        with pytest.raises(CompilerError, match="Pre-flight formatting validation failed"):
            compiler.render_assets(ast, metadata)

    def test_render_assets_happy_path(self):
        compiler = CompilerEngine("MH-DISTRICT")
        # Ensure all required sections are present for MH-DISTRICT
        ast = {
            "sections": {
                "cause_title": "In the Court of Nagpur",
                "jurisdiction_clause": "This Court has jurisdiction.",
                "facts": "The facts are simple.",
                "grounds": "These are the grounds.",
                "prayer": "Pray for relief.",
                "verification": "Verified at Nagpur.",
                "deponent_signature": "Signed by deponent."
            },
            "formatting": {
                "margin_left_cm": 3.0,
                "margin_right_cm": 2.5,
                "margin_top_cm": 2.5,
                "margin_bottom_cm": 2.0,
                "font_body": "Times New Roman",
                "font_size_body": 14,
                "line_spacing": 1.5
            }
        }
        metadata = {
            "court_designation": "Civil Judge",
            "city_name": "Nagpur",
            "case_type": "Civil Suit",
            "case_number": "123",
            "year": "2026",
            "stamp_paper_value": "100"
        }
        pdf = compiler.render_assets(ast, metadata)
        assert isinstance(pdf, bytes)
        assert pdf.startswith(b"%PDF-")


class TestCompilerStage2:
    """Test Stage 2: 10x Byte-Code Audits."""

    def test_audit_binary_structure_happy(self):
        compiler = CompilerEngine("MH-DISTRICT")
        # Construct a simulated valid PDF binary structure
        pdf_bytes = b"%PDF-1.4\n%...\nxref\n/Size 10\ntrailer\n<< >>\nstartxref\n14\n%%EOF"
        res = compiler.audit_binary_structure(pdf_bytes)
        assert res["status"] == "PASS"
        assert len(res["audits"]) == 10
        assert "md5" in res
        assert "sha256" in res

    def test_audit_binary_structure_corrupt(self):
        compiler = CompilerEngine("MH-DISTRICT")
        # Missing startxref/EOF
        pdf_bytes = b"%PDF-1.4\n%...\n/Size 10\ntrailer\n<< >>"
        with pytest.raises(CompilerError, match="Binary structural audit failed"):
            compiler.audit_binary_structure(pdf_bytes)

    def test_audit_text_extraction(self):
        compiler = CompilerEngine("MH-DISTRICT")
        # Construct a PDF binary block containing a compressed stream with Tj and TJ operations
        import zlib
        content_stream = b"BT\n/F1 12 Tf\n(Happy Case Facts) Tj\n[(Grounds) -10 ( Relief)] TJ\nET"
        compressed = zlib.compress(content_stream)
        pdf_bytes = b"%PDF-1.4\n<< /Filter /FlateDecode /Length " + str(len(compressed)).encode() + b" >>\nstream\n" + compressed + b"\nendstream\n"
        
        res = compiler.audit_text_extraction(pdf_bytes, "Happy Case Facts Grounds Relief")
        assert "extraction_loops" in res
        assert res["word_count"] >= 5
        assert res["spelling_score"] > 0.8

    def test_optimize_image_compression_under_limit(self):
        compiler = CompilerEngine("MH-DISTRICT")
        # 1KB file is well under 20MB
        pdf_bytes = b"%PDF-1.4\n" + b"A" * 1000
        res = compiler.optimize_image_compression(pdf_bytes)
        assert len(res) == len(pdf_bytes)

    def test_optimize_image_compression_over_limit(self):
        compiler = CompilerEngine("MH-DISTRICT")
        # 21MB file exceeds 20MB limit
        pdf_bytes = b"%PDF-1.4\n" + b"A\r\n" * 7000000
        res = compiler.optimize_image_compression(pdf_bytes)
        # Should attempt compression loop and shrink due to \r\n replacement to \n
        assert len(res) < len(pdf_bytes)

    def test_sanitize_metadata(self):
        compiler = CompilerEngine("MH-DISTRICT")
        pdf_bytes = b"%PDF-1.4\n/Creator (ReportLab)\n/Producer (ReportLab)\n/Author (Manas)\n/CreationDate (2026)\n/GPSInfo 123 0 R\ntrailer\n<<"
        res = compiler.sanitize_metadata(pdf_bytes, "sha256hashhere")
        
        # Verify creator, producer, author, and date are stripped
        assert b"/Creator ()" in res
        assert b"/Producer ()" in res
        assert b"/Author ()" in res
        assert b"/CreationDate ()" in res
        assert b"/GPSInfo" not in res
        
        # Verify custom verifier hash metadata is injected
        assert b"/VerifierHash (sha256hashhere)" in res


class TestCompilerStage3:
    """Test Stage 3: Court Formatting Rules & AST Compliance Gates."""

    def test_verify_margin_rules_sc_happy(self):
        compiler = CompilerEngine("IN-SC")
        # Pre-fill with incorrect margin, check that auto-corrections apply
        ast = {
            "sections": {
                "cause_title": "Supreme Court of India Pleading",
                "facts": "This is a line of 10 to 50 words that verifies margin check constraints\nand has zero truncation in the final compiled document which we are testing now."
            },
            "formatting": {
                "margin_left_cm": 2.0,
                "margin_right_cm": 2.0,
                "margin_top_cm": 2.0,
                "margin_bottom_cm": 2.0,
                "line_spacing": 1.5,
                "paper_size": "A4",
                "orientation": "portrait"
            }
        }
        res = compiler.verify_margin_rules(ast, {})
        assert res["is_valid"]
        # Verify that auto-corrections mutated the formatting dictionary to SC standards
        assert ast["formatting"]["margin_left_cm"] == 3.175
        assert ast["formatting"]["margin_right_cm"] == 3.175
        assert ast["formatting"]["margin_top_cm"] == 2.54
        assert ast["formatting"]["margin_bottom_cm"] == 2.54
        assert ast["formatting"]["line_spacing"] == 2.0
        assert res["line_checks_run"] > 0
        assert res["paragraph_checks_run"] > 0
        assert res["clause_reviews_run"] > 0

    def test_verify_margin_rules_sc_invalid_orientation(self):
        compiler = CompilerEngine("IN-SC")
        ast = {
            "sections": {"cause_title": "Supreme Court Pleading"},
            "formatting": {
                "paper_size": "LETTER",  # Invalid paper size
                "orientation": "landscape"  # Landscape is invalid
            }
        }
        with pytest.raises(CompilerError, match="Court margin/formatting rules violation"):
            compiler.verify_margin_rules(ast, {})

    def test_verify_clauses_happy_path(self):
        compiler = CompilerEngine("MH-HC")
        metadata = {"petitioner_name": "Vidya Khobrekar"}
        ast = {
            "sections": {
                "cause_title": "IN THE HIGH COURT OF JUDICATURE AT BOMBAY\nVidya Khobrekar",
                "facts": "First paragraph of the facts.\n\nSecond paragraph of the facts.",
                "prayer": "Therefore, the petitioner prays...",
                "verification": "I, Vidya Khobrekar, solemnly affirm...",
                "deponent_signature": "Signature of Petitioner Vidya Khobrekar"
            },
            "formatting": {
                "margin_left_cm": 4.0,
                "margin_right_cm": 2.5,
                "margin_top_cm": 3.0,
                "margin_bottom_cm": 2.5,
                "line_spacing": 2.0,
                "paragraph_indent_cm": 1.0
            }
        }
        res = compiler.verify_clauses_and_headings(ast, metadata)
        assert res["is_valid"]
        assert ast["formatting"]["headings_locked"]
        assert "clause_structural_hashes" in ast
        assert "heading_verification_log" in ast

    def test_verify_clauses_mismatched_petitioner(self):
        compiler = CompilerEngine("MH-HC")
        metadata = {"petitioner_name": "John Doe"}
        ast = {
            "sections": {
                "cause_title": "IN THE HIGH COURT OF JUDICATURE AT BOMBAY\nVidya Khobrekar",
                "facts": "Facts content.",
                "prayer": "Prayer.",
                "verification": "Solemnly affirm.",
                "deponent_signature": "Vidya Khobrekar"
            },
            "formatting": {}
        }
        with pytest.raises(CompilerError, match="Court heading/clause rules violation"):
            compiler.verify_clauses_and_headings(ast, metadata)

    def test_verify_clauses_realignment_prayer(self):
        compiler = CompilerEngine("MH-HC")
        metadata = {"petitioner_name": "Vidya Khobrekar"}
        ast = {
            "sections": {
                "cause_title": "IN THE HIGH COURT OF JUDICATURE AT BOMBAY\nVidya Khobrekar",
                "prayer": "Therefore, the petitioner prays...",
                "facts": "Facts content.",
                "verification": "Solemnly affirm.",
                "deponent_signature": "Signature of Petitioner Vidya Khobrekar"
            },
            "formatting": {}
        }
        # In this AST, prayer is BEFORE facts. Realignment should move it to end.
        res = compiler.verify_clauses_and_headings(ast, metadata)
        assert res["is_valid"]
        keys = list(ast["sections"].keys())
        # Facts should now be before prayer, and prayer should be before verification
        assert keys.index("facts") < keys.index("prayer")
        assert keys.index("prayer") < keys.index("verification")

    def test_format_output_page_limit_violation(self):
        compiler = CompilerEngine("MH-DISTRICT")
        # 3 pages
        pdf_bytes = b"%PDF-1.4\n%...\n/Type /Page\n/Type /Page\n/Type /Page\n/Author ()"
        metadata = {"page_limit": 2}
        with pytest.raises(PDFAComplianceError, match="exceeds the petition limit"):
            compiler.format_output(pdf_bytes, metadata)

    def test_format_output_resolution_violation(self):
        compiler = CompilerEngine("MH-DISTRICT")
        pdf_bytes = b"%PDF-1.4\n%...\n/Type /Page\n/Author ()"
        metadata = {"resolution_dpi": 150} # below 200 bounds
        with pytest.raises(PDFAComplianceError, match="violates e-filing bounds"):
            compiler.format_output(pdf_bytes, metadata)
        metadata = {"resolution_dpi": 700} # above 600 bounds
        with pytest.raises(PDFAComplianceError, match="violates e-filing bounds"):
            compiler.format_output(pdf_bytes, metadata)

    def test_format_output_happy_path_with_metrics(self):
        compiler = CompilerEngine("MH-DISTRICT")
        pdf_bytes = b"%PDF-1.4\n%...\n/Type /Page\n/Author ()"
        metadata = {"page_limit": 10, "resolution_dpi": 400}
        res = compiler.format_output(pdf_bytes, metadata)
        assert res.startswith(b"%PDF-")
        assert metadata["compliance_locked"]
        assert "compliance_metrics" in metadata
        assert metadata["compliance_metrics"]["page_count"] == 1
        assert metadata["compliance_metrics"]["resolution_dpi"] == 400
        assert metadata["compliance_metrics"]["is_valid"]
        assert b"/ComplianceMetrics" in res

    def test_verify_security_attestation_happy(self):
        compiler = CompilerEngine("MH-DISTRICT")
        pdf_bytes = b"%PDF-1.4\n%...\n/Type /Page\n/Author ()"
        metadata = {}
        res = compiler.verify_security_attestation(pdf_bytes, metadata)
        assert res["is_valid"]
        assert res["threat_level_index"] == 0.05
        assert metadata["compiled_file_permissions"] == "READ-ONLY"
        assert metadata["security_attestation_locked"]
        assert "security_attestation_metrics" in metadata
        assert "COMPILE_READY_" in res["token_tag"]

    def test_verify_security_attestation_code_injection(self):
        compiler = CompilerEngine("MH-DISTRICT")
        # Contains /System command injection exploit pattern
        pdf_bytes = b"%PDF-1.4\n/System (cmd.exe /c calc)\n/Type /Page"
        metadata = {}
        with pytest.raises(CompilerError, match="Security attestation violation"):
            compiler.verify_security_attestation(pdf_bytes, metadata)

    def test_verify_security_attestation_alerts_present(self):
        compiler = CompilerEngine("MH-DISTRICT")
        pdf_bytes = b"%PDF-1.4\n/Type /Page"
        metadata = {"compilation_alerts_count": 3}
        with pytest.raises(CompilerError, match="Security attestation violation"):
            compiler.verify_security_attestation(pdf_bytes, metadata)


class TestCompilerStage4:
    """Test Stage 4: Global Internet Grounding Verification."""

    def test_verify_internet_grounding_happy(self):
        compiler = CompilerEngine("MH-DISTRICT")
        ast = {
            "sections": {
                "cause_title": "IN THE COURT OF SUBORDINATE JUDGE AT NAGPUR",
                "facts": "This is a detailed paragraph about facts. It contains more than ten words to pass the line verification check step properly.",
                "prayer": "Therefore the petitioner prays for relief in this court."
            }
        }
        metadata = {
            "scribd_api_status": "connected",
            "quora_api_status": "connected",
            "reddit_token_status": "valid",
            "blogs_api_status": "indexed"
        }
        res = compiler.verify_internet_grounding(ast, metadata)
        assert res["is_valid"]
        assert ast["grounding_verification_status"] == "PASS"
        assert metadata["scribd_verification_locked"]
        assert metadata["quora_verification_locked"]
        assert metadata["reddit_verification_locked"]
        assert metadata["blogs_verification_locked"]
        assert "scribd_validation_metrics" in metadata
        assert "quora_validation_metrics" in metadata
        assert "reddit_validation_metrics" in metadata
        assert "blogs_validation_metrics" in metadata

    def test_verify_internet_grounding_unverified_tag(self):
        compiler = CompilerEngine("MH-DISTRICT")
        ast = {
            "sections": {
                "cause_title": "IN THE COURT OF SUBORDINATE JUDGE AT NAGPUR",
                "facts": "This is an UNVERIFIED statement or claim.",
                "prayer": "Therefore the petitioner prays."
            }
        }
        metadata = {}
        with pytest.raises(CompilerError, match="Compiler blocked filing: 'UNVERIFIED' citation/fact tag found"):
            compiler.verify_internet_grounding(ast, metadata)

    def test_verify_internet_grounding_simulate_failure(self):
        compiler = CompilerEngine("MH-DISTRICT")
        ast = {
            "sections": {
                "cause_title": "IN THE COURT OF SUBORDINATE JUDGE AT NAGPUR",
                "facts": "Facts content for internet grounding checks test.",
                "prayer": "Pray for relief."
            }
        }
        # Simulate generic grounding failure
        metadata = {"simulate_grounding_failure": True}
        with pytest.raises(CompilerError, match="Internet grounding validation failed"):
            compiler.verify_internet_grounding(ast, metadata)
        assert ast["grounding_uct_penalty"] == -5000.0
        assert metadata["uct_penalty"] == -5000.0

        # Simulate specific Scribd failure
        ast_2 = {"sections": {"facts": "Facts."}}
        metadata_2 = {"simulate_scribd_failure": True}
        with pytest.raises(CompilerError, match="Scribd grounding pattern anomaly"):
            compiler.verify_internet_grounding(ast_2, metadata_2)

    def test_verify_internet_grounding_api_failures(self):
        compiler = CompilerEngine("MH-DISTRICT")
        ast = {"sections": {"facts": "Facts."}}
        
        # Test offline Scribd
        with pytest.raises(CompilerError, match="Scribd API connection failure"):
            compiler.verify_internet_grounding(ast, {"scribd_api_status": "disconnected"})

        # Test offline Quora
        with pytest.raises(CompilerError, match="Quora search API offline"):
            compiler.verify_internet_grounding(ast, {"quora_api_status": "offline"})

        # Test invalid Reddit token
        with pytest.raises(CompilerError, match="Reddit developer token invalid"):
            compiler.verify_internet_grounding(ast, {"reddit_token_status": "expired"})

        # Test offline Blogs
        with pytest.raises(CompilerError, match="Legal blogs API indexing offline"):
            compiler.verify_internet_grounding(ast, {"blogs_api_status": "offline"})


class TestCompilerStage5:
    """Test Stage 5: The Delivery Payload."""

    def test_build_delivery_payload_happy(self):
        compiler = CompilerEngine("MH-DISTRICT")
        pdf_bytes = b"%PDF-1.4\n%...\n/Type /Page\n/Author ()"
        ast = {
            "sections": {
                "cause_title": "IN THE COURT OF SUBORDINATE JUDGE AT NAGPUR",
                "facts": "Facts content.",
                "prayer": "Pray for relief."
            },
            "clause_structural_hashes": {
                "facts": "hash123",
                "prayer": "hash456"
            }
        }
        metadata = {
            "destination_coordinates": "IN-SC-DELHI"
        }
        
        # Happy Path
        zip_data = compiler.build_delivery_payload(pdf_bytes, ast, metadata)
        assert isinstance(zip_data, bytes)
        assert zip_data.startswith(b"PK")  # ZIP signature
        
        # Verify ZIP contains correct files
        import zipfile
        import io
        zip_io = io.BytesIO(zip_data)
        with zipfile.ZipFile(zip_io, "r") as zf:
            files = zf.namelist()
            assert "document.pdf" in files
            assert "evidence_ledger.json" in files
            assert "swarm_summary.md" in files
            
            # Verify file content
            pdf_content = zf.read("document.pdf")
            assert pdf_content == pdf_bytes
            
        # Verify Telemetry metics
        assert "telemetry_metrics" in metadata
        assert metadata["telemetry_metrics"]["compilation_outcome"] == "success"
        assert metadata["telemetry_metrics"]["transmission_status"] == "SIGNAL_SENT"
        assert metadata["telemetry_locked"]
        
        # Verify Shutdown metrics
        assert "shutdown_metrics" in metadata
        assert "SHUTDOWN_READY_" in metadata["shutdown_metrics"]["success_token"]
        assert metadata["shutdown_metrics"]["status"] == "compiled-finished"
        assert metadata["shutdown_locked"]
        
        # Verify Delivery Attestation metrics
        assert "delivery_metrics" in metadata
        assert metadata["delivery_metrics"]["tracking_state"] == "complete"
        assert "DELIVERY_OK_" in metadata["delivery_metrics"]["delivery_token"]
        assert metadata["delivery_attestation_closed"]

    def test_build_delivery_payload_failures(self):
        compiler = CompilerEngine("MH-DISTRICT")
        pdf_bytes = b"%PDF-1.4\n%...\n/Type /Page"
        ast = {"sections": {"facts": "Facts."}}
        
        # 1. Package failure
        with pytest.raises(CompilerError, match="Simulated Zip construction failure"):
            compiler.build_delivery_payload(pdf_bytes, ast, {"simulate_package_failure": True})
            
        # 2. Telemetry failure
        with pytest.raises(CompilerError, match="Simulated telemetry reporting failure"):
            compiler.build_delivery_payload(pdf_bytes, ast, {"simulate_telemetry_failure": True})
            
        # 3. Shutdown failure
        with pytest.raises(CompilerError, match="Simulated system shutdown coordination failure"):
            compiler.build_delivery_payload(pdf_bytes, ast, {"simulate_shutdown_failure": True})
            
        # 4. Delivery failure
        with pytest.raises(CompilerError, match="Simulated package delivery attestation failure"):
            compiler.build_delivery_payload(pdf_bytes, ast, {"simulate_delivery_failure": True})

        # Verify UCT penalty is applied on failure
        metadata = {"simulate_package_failure": True}
        with pytest.raises(CompilerError, match="UCT penalty of -5000.0 applied"):
            compiler.build_delivery_payload(pdf_bytes, ast, metadata)
        assert metadata["uct_penalty"] == -5000.0
        assert ast["delivery_uct_penalty"] == -5000.0


class TestCompilerStage6:
    """Test Stage 6: Compiler State Persistence & Payload Dispatch."""

    def test_dispatch_and_cleanup_happy(self):
        compiler = CompilerEngine("MH-DISTRICT")
        zip_payload = b"PK\x03\x04\n\x00..." # Mock ZIP
        ast = {}
        metadata = {
            "registry_file_path": "artifacts/test_compiler_registry.json",
            "summary_report_file_path": "artifacts/test_compiler_summary.log"
        }

        # Happy Path
        res = compiler.dispatch_and_cleanup(zip_payload, ast, metadata)
        assert res["is_valid"]
        assert ast["persistence_dispatch_status"] == "PASS"

        # Verify Persistence metrics & files
        assert metadata["persistence_locked"]
        assert "persistence_metrics" in metadata
        assert metadata["persistence_metrics"]["write_status_ok"]
        import os
        assert os.path.exists("artifacts/test_compiler_registry.json")

        # Verify Dispatch metrics
        assert metadata["dispatch_locked"]
        assert "dispatch_metrics" in metadata
        assert metadata["dispatch_metrics"]["dispatch_status"] == "DISPATCHED"

        # Verify Swarm State Cleanup metrics
        assert metadata["cleanup_locked"]
        assert "cleanup_metrics" in metadata
        assert metadata["cleanup_metrics"]["gpu_memory_released"]
        assert metadata["cleanup_metrics"]["cpu_load_idle"]

        # Verify Compilation Summary Report metrics & files
        assert metadata["summary_locked"]
        assert "summary_metrics" in metadata
        assert os.path.exists("artifacts/test_compiler_summary.log")

        # Cleanup test files
        if os.path.exists("artifacts/test_compiler_registry.json"):
            os.remove("artifacts/test_compiler_registry.json")
        if os.path.exists("artifacts/test_compiler_summary.log"):
            os.remove("artifacts/test_compiler_summary.log")

    def test_dispatch_and_cleanup_failures(self):
        compiler = CompilerEngine("MH-DISTRICT")
        zip_payload = b"PK\x03\x04\n\x00..."
        ast = {}

        # 1. Persistence failure
        with pytest.raises(CompilerError, match="Simulated registry write failure"):
            compiler.dispatch_and_cleanup(zip_payload, ast, {"simulate_persistence_failure": True})

        # 2. Dispatch failure
        with pytest.raises(CompilerError, match="Simulated network dispatch transmission timeout"):
            compiler.dispatch_and_cleanup(zip_payload, ast, {"simulate_dispatch_failure": True})

        # 3. Cleanup failure
        with pytest.raises(CompilerError, match="Simulated memory cleanup failed"):
            compiler.dispatch_and_cleanup(zip_payload, ast, {"simulate_cleanup_failure": True})

        # 4. Summary failure
        with pytest.raises(CompilerError, match="Simulated summary reporting mismatch"):
            compiler.dispatch_and_cleanup(zip_payload, ast, {"simulate_summary_failure": True})

        # Verify UCT penalty is applied on failure
        metadata = {"simulate_persistence_failure": True}
        with pytest.raises(CompilerError, match="UCT penalty of -5000.0 applied"):
            compiler.dispatch_and_cleanup(zip_payload, ast, metadata)
        assert metadata["uct_penalty"] == -5000.0
        assert ast["persistence_uct_penalty"] == -5000.0





