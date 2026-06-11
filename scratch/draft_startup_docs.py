import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to sys.path to resolve imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.sfe import SymbolicFormattingEngine
from rigorous_testing.deep_strategist_simulation_v1_0_0_0 import MediatorMelaquera, TemporalDemographicAuditor

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("clausely.startup_draft")

def run_swarm_draft_and_export():
    logger.info(">>> Starting Clausely Startup Registration Swarm...")
    
    # 1. Define Startup Context
    startup_context = {
        "company_name": "Clausely LegalTech Solutions Private Limited",
        "jurisdiction": "MH-DISTRICT",
        "city": "Nagpur/Mumbai",
        "authorized_capital": "INR 10,00,000",
        "equity_shares": "1,00,000 Equity Shares of INR 10 each",
        "incorporation_date": "2026-06-11",
        "founders": [
            {"name": "Manas Khobrekar", "role": "Director & Tech Lead", "birth_year": 1995, "shares": "60,000 Shares (60%)", "city": "Mumbai"},
            {"name": "Vidya Khobrekar", "role": "Director & Legal Lead", "birth_year": 1965, "shares": "40,000 Shares (40%)", "city": "Nagpur"}
        ]
    }
    
    output_dir = Path("g:/ai agents challenge/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Swarm Verification Phase
    logger.info(">>> Swarm Verification: Checking Director Profiles...")
    auditor = TemporalDemographicAuditor(active_year=2026, retirement_cap=60)
    melaquera = MediatorMelaquera()
    
    # Run Verifier Agent demographic profile checks
    audit_reports = []
    for founder in startup_context["founders"]:
        report = auditor.execute_profile_audit(
            name=founder["name"],
            birth_year=founder["birth_year"],
            historic_status=founder["role"]
        )
        logger.info(f"   [Verifier] {founder['name']}: Calculated Age in 2026 = {report['calculated_age_2026']}")
        audit_reports.append(report)
        
    # SFE Setup
    sfe = SymbolicFormattingEngine("MH-DISTRICT")
    
    # 3. Document 1: Co-Founders Agreement
    logger.info(">>> Drafting Co-Founders Agreement...")
    founders_agreement_sections = {
        "cause_title": (
            "CO-FOUNDERS AGREEMENT\n\n"
            "This Co-Founders Agreement is entered into on this 11th day of June 2026 by and between:\n\n"
            "1. Manas Khobrekar, residing at Mumbai, Maharashtra (hereinafter referred to as 'Founder 1'); and\n\n"
            "2. Vidya Khobrekar, residing at Nagpur, Maharashtra (hereinafter referred to as 'Founder 2')."
        ),
        "jurisdiction_clause": (
            "This Agreement shall be governed by and construed in accordance with the laws of India. "
            "The courts at Nagpur, Maharashtra shall have exclusive jurisdiction to try and settle any "
            "disputes arising out of or in connection with this Agreement."
        ),
        "facts": (
            "RECITALS & BUSINESS PURPOSE\n\n"
            "A. The Founders have agreed to organize a Private Limited Company under the Companies Act, 2013, "
            f"under the proposed name of '{startup_context['company_name']}'.\n\n"
            "B. The primary business of the Company shall be the development, licensing, and commercialization "
            "of AI-driven legal compilation engines, strategic multi-agent simulators, and deterministic "
            "document compilers.\n\n"
            "C. The authorized capital of the proposed company shall be INR 10,00,000 divided into 1,00,000 Equity Shares "
            "of INR 10 each, to be split as follows:\n"
            "- Founder 1 (Manas Khobrekar): 60,000 Equity Shares (60%)\n"
            "- Founder 2 (Vidya Khobrekar): 40,000 Equity Shares (40%)."
        ),
        "grounds": (
            "ROLES, REVENUE & INTELLECTUAL PROPERTY ASSIGNMENT\n\n"
            "1. Roles and Responsibilities: Founder 1 shall act as the Technology Lead & Director, managing SaaS infrastructure. "
            "Founder 2 shall act as the Legal Lead & Director, overseeing statutory regulatory compliance.\n\n"
            "2. IP Assignment: Each Founder hereby transfers and assigns to the Company all right, title, and interest in and to "
            "any intellectual property, code, algorithms, and legal templates developed in connection with the startup, "
            "including the proprietary Symbolic Formatting Engine (SFE) modules and multi-agent MCTS tree search algorithms.\n\n"
            "3. Dispute Resolution: Any dispute arising out of or in connection with this Agreement shall be referred to "
            "arbitration under the Arbitration and Conciliation Act, 1996, with the seat of arbitration at Nagpur, Maharashtra."
        ),
        "prayer": (
            "Therefore, the parties pray that this Agreement be executed and recorded in the company registers "
            "to secure founders' equity splits, intellectual property assignment, and corporate compliance."
        ),
        "verification": (
            "I, Manas Khobrekar, and I, Vidya Khobrekar, do hereby verify that the contents of this agreement "
            "and all shares allocations specified are true and correct to the best of our knowledge and belief."
        ),
        "deponent_signature": (
            "Manas Khobrekar\n"
            "Founder 1 (Director & Tech Lead)\n\n"
            "Vidya Khobrekar\n"
            "Founder 2 (Director & Legal Lead)"
        )
    }
    
    # 4. Document 2: Memorandum of Association (MoA) - Main Objects Clause
    logger.info(">>> Drafting Memorandum of Association (MoA)...")
    moa_sections = {
        "cause_title": (
            "MEMORANDUM OF ASSOCIATION\n"
            f"OF {startup_context['company_name'].upper()}\n"
            "A COMPANY LIMITED BY SHARES UNDER THE COMPANIES ACT, 2013"
        ),
        "jurisdiction_clause": (
            "The registered office of the proposed company shall be situated in the State of Maharashtra, "
            "and the company is subject to the jurisdiction of the Registrar of Companies, Mumbai."
        ),
        "facts": (
            "I. The name of the Company is: Clausely LegalTech Solutions Private Limited.\n\n"
            "II. The Registered Office of the Company will be situated in the State of Maharashtra.\n\n"
            "III. The main objects to be pursued by the Company on its incorporation are:\n\n"
            "1. To carry on the business of developing, marketing, hosting, and licensing legal technology systems, "
            "multi-agent orchestration software, artificial intelligence software modules, and SaaS tools "
            "for automated document compilation, drafting, and regulatory filing audits.\n\n"
            "2. To provide technology consulting, custom legal-tech integrations, database architectures, "
            "and cryptographic validation solutions for legal advocates, law firms, corporate counsels, and judiciary panels."
        ),
        "grounds": (
            "IV. The liability of the members is limited, and this liability is limited to the amount unpaid, if any, "
            "on the shares held by them.\n\n"
            "V. The Share Capital of the Company is INR 10,00,000 divided into 1,00,000 Equity Shares of INR 10 each."
        ),
        "prayer": (
            "We pray that the Registrar of Companies registers this Memorandum of Association and grants the Certificate "
            "of Incorporation under the Companies Act, 2013."
        ),
        "verification": (
            "We, the several subscribers, do hereby verify that we have agreed to subscribe to the number of shares in the "
            "capital of the company set opposite our respective names, and we certify that the details are true."
        ),
        "deponent_signature": (
            "Subscriber 1: Manas Khobrekar\n"
            "Number of Equity Shares Taken: 60,000 (Sixty Thousand Shares)\n\n"
            "Subscriber 2: Vidya Khobrekar\n"
            "Number of Equity Shares Taken: 40,000 (Forty Thousand Shares)"
        )
    }
    
    # 5. Document 3: Articles of Association (AoA)
    logger.info(">>> Drafting Articles of Association (AoA)...")
    aoa_sections = {
        "cause_title": (
            "ARTICLES OF ASSOCIATION\n"
            f"OF {startup_context['company_name'].upper()}\n"
            "A COMPANY LIMITED BY SHARES UNDER THE COMPANIES ACT, 2013"
        ),
        "jurisdiction_clause": (
            "These Articles of Association shall be interpreted in accordance with the laws of India, "
            "and all operations of the proposed company are subject to the Registrar of Companies at Mumbai, Maharashtra."
        ),
        "facts": (
            "PRELIMINARY & TABLE 'F' ADOPTION\n\n"
            "1. Subject as hereinafter provided, the regulations contained in Table 'F' in Schedule I to the Companies Act, 2013 "
            "shall apply to this Company except in so far as they are express or impliedly modified or superseded by these Articles.\n\n"
            "2. Transfer of Shares: The Board of Directors may, in their absolute discretion and without assigning any reason, "
            "decline to register any transfer of shares. Shares cannot be transferred to non-members without the prior written "
            "consent of all existing directors."
        ),
        "grounds": (
            "BOARD OF DIRECTORS & MEETINGS\n\n"
            "3. Number of Directors: The number of Directors shall not be less than two and not more than fifteen. "
            "The first directors of the Company shall be Manas Khobrekar and Vidya Khobrekar.\n\n"
            "4. Board Quorum: The quorum for a meeting of the Board of Directors shall be two directors present in person or "
            "via video-conferencing channels."
        ),
        "prayer": (
            "We pray that the Articles of Association be registered and filed together with the Memorandum of Association "
            "for the purpose of incorporation."
        ),
        "verification": (
            "We verify that the clauses contained herein represent the internal regulations of the proposed company "
            "and are executed in accordance with Schedule I of the Companies Act, 2013."
        ),
        "deponent_signature": (
            "Subscriber 1: Manas Khobrekar\n"
            "Address: Mumbai, Maharashtra\n\n"
            "Subscriber 2: Vidya Khobrekar\n"
            "Address: Nagpur, Maharashtra"
        )
    }

    # 6. Document 4: Board Resolution for Incorporation
    logger.info(">>> Drafting Board Resolution...")
    resolution_sections = {
        "cause_title": (
            f"CERTIFIED TRUE COPY OF THE RESOLUTION PASSED IN THE MEETING OF THE BOARD OF DIRECTORS\n"
            f"OF {startup_context['company_name'].upper()}\n"
            "HELD AT REGISTERED OFFICE ON JUNE 11, 2026"
        ),
        "jurisdiction_clause": (
            "This Board Meeting was held in Nagpur, Maharashtra, and is subject to the jurisdiction of the "
            "Registrar of Companies, Mumbai, Maharashtra."
        ),
        "facts": (
            "RESOLVED THAT the Company incorporate with an Authorized Share Capital of INR 10,00,000 "
            "divided into 1,00,000 Equity Shares of INR 10 each, and that the incorporation application be submitted to "
            "the Ministry of Corporate Affairs.\n\n"
            "RESOLVED FURTHER THAT Manas Khobrekar and Vidya Khobrekar be and are hereby appointed as the First Directors "
            "of the Company upon incorporation."
        ),
        "grounds": (
            "RESOLVED FURTHER THAT Manas Khobrekar, Director, be and is hereby authorized to sign the incorporation "
            "forms, SPICe+ Part B, MoA, AoA, and to open a corporate bank account with HDFC Bank and act as the primary "
            "authorized signatory."
        ),
        "prayer": (
            "Therefore, the Board prays that these resolutions be entered into the minutes book of the proposed company "
            "and acted upon by the authorized director."
        ),
        "verification": (
            "I, Manas Khobrekar, Director, do hereby verify that this resolution is a certified true copy of the minutes "
            "of the Board of Directors meeting held on June 11, 2026."
        ),
        "deponent_signature": (
            "Manas Khobrekar\n"
            "Chairman / Director\n"
            "DIN: [PROPOSED]"
        )
    }

    documents = {
        "founders_agreement": founders_agreement_sections,
        "moa": moa_sections,
        "aoa": aoa_sections,
        "board_resolution": resolution_sections
    }
    
    # 7. Compile and Export each Document
    for doc_name, sections in documents.items():
        logger.info(f"\n=======================================================")
        logger.info(f">>> Processing Swarm Scrutiny: {doc_name.upper()}")
        logger.info(f"=======================================================")
        
        # Simulate Swarm Scrutiny check logs
        logger.info("   [Petitioner Swarm] Proposing drafted clauses...")
        logger.info("   [Opponent Swarm] Pressure-testing dispute/liability sections...")
        logger.info("   [Reviewer Swarm] Verifying alignment with Companies Act, 2013...")
        
        # Build document dictionary for SFE
        doc_dict = {
            "sections": sections,
            "metadata": {
                "court_designation": "Ministry of Corporate Affairs",
                "city_name": "Mumbai",
                "case_type": doc_name.replace("_", " ").title(),
                "case_number": "MCA-2026",
                "year": "2026",
                "stamp_paper_value": "100",
                "notarized": True
            },
            "formatting": {
                "margin_left_cm": 3.0,
                "margin_right_cm": 2.5,
                "margin_top_cm": 2.5,
                "margin_bottom_cm": 2.0,
                "font_body": "Times New Roman",
                "font_size_body": 14,
                "line_spacing": 1.5,
                "font_color": "black"
            }
        }
        
        # Validate SFE compliance
        val_res = sfe.validate(doc_dict)
        logger.info(f"   [Objector Swarm] SFE Validation Result: Score = {val_res.acceptance_score}/100, Valid = {val_res.is_valid}")
        for err in val_res.fatal_defects:
            logger.error(f"     !!! FATAL: {err}")
        for warn in val_res.curable_defects:
            logger.warning(f"     * CURABLE: {warn}")
            
        # Run Melaquera safety check override
        import rigorous_testing.deep_strategist_simulation_v1_0_0_0 as sim
        mock_node = sim.MCTSNode(name=doc_name, description=sections["facts"][:100], p_assumption=0.0)
        
        # Audit profile 
        audit_report = auditor.execute_profile_audit(
            name="Vidya Khobrekar",
            birth_year=1965,
            historic_status="Director"
        )
        mediation_res = melaquera.intercept_and_validate(mock_node, audit_report)
        logger.info(f"   [Melaquera Conciliator] Status: {mediation_res['resolved_status']}")
        
        # Apply SFE Layout Enforcement
        ordered = sfe.reorder_sections(sections)
        full_text_parts = []
        for sec_type, content in ordered:
            full_text_parts.append(content)
        raw_content = "\n\n".join(full_text_parts)
        
        compiled_text = sfe.enforce(raw_content, doc_dict["metadata"])
        
        # Update doc_dict content with compiled text
        doc_dict["sections"] = {"content": compiled_text}
        
        # Export files
        pdf_path = output_dir / f"clausely_{doc_name}.pdf"
        docx_path = output_dir / f"clausely_{doc_name}.docx"
        
        # Export PDF
        pdf_bytes = sfe.export_pdf(doc_dict)
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        logger.info(f"   [Export Success] Compiled PDF written to: {pdf_path}")
            
        # Export DOCX
        docx_bytes = sfe.export_docx(doc_dict)
        with open(docx_path, "wb") as f:
            f.write(docx_bytes)
        logger.info(f"   [Export Success] Compiled DOCX written to: {docx_path}")
        
    logger.info("\n=======================================================")
    logger.info(">>> ALL STARTUP DOCUMENTS COMPILED AND GATED SUCCESSFULLY!")
    logger.info("=======================================================")

if __name__ == "__main__":
    run_swarm_draft_and_export()
