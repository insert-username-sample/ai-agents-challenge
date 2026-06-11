"""
Clausely BNS Citation Checker — RAG & Deterministic Citation Validator.

Provides dynamic, rule-based cross-referencing between older Indian laws
(IPC, CrPC, IEA) and the new criminal laws (BNS, BNSS, BSA) that took effect
in 2024. Ensures all cited sections in court documents are active and accurate.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger("clausely.citation_checker")

# Paths to the downloaded mapping files
_MAP_DIR = Path(__file__).resolve().parent.parent / "downloads" / "IndLegal" / "mapping"
_IPC_MAP_PATH = _MAP_DIR / "ipc.json"
_CRPC_MAP_PATH = _MAP_DIR / "crpc.json"
_IEA_MAP_PATH = _MAP_DIR / "iea.json"

class CitationChecker:
    """
    Validates and auto-translates Indian statutory citations
    from IPC/CrPC/IEA to BNS/BNSS/BSA.
    """

    def __init__(self):
        self.ipc_map = self._load_map(_IPC_MAP_PATH)
        self.crpc_map = self._load_map(_CRPC_MAP_PATH)
        self.iea_map = self._load_map(_IEA_MAP_PATH)

    def _load_map(self, path: Path) -> Dict[str, str]:
        """Load mapping JSON securely."""
        if not path.exists():
            logger.warning(f"Citation mapping file not found: {path}")
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading citation map {path}: {e}")
            return {}

    def extract_and_verify(self, text: str) -> Dict[str, Any]:
        """
        Scan document text for deprecated or current statutory citations,
        validate them, and suggest modern replacements.
        """
        results = {
            "is_compliant": True,
            "citations_found": [],
            "warnings": [],
            "suggestions": []
        }

        # 1. Regex patterns to detect various forms of statutory citations
        ipc_pattern = r"(?i)(?:section|sec\.?)\s*(\d+)\s*(?:of\s*the\s*)?(?:ipc|indian\s*penal\s*code)"
        crpc_pattern = r"(?i)(?:section|sec\.?)\s*(\d+)\s*(?:of\s*the\s*)?(?:crpc|code\s*of\s*criminal\s*procedure)"
        iea_pattern = r"(?i)(?:section|sec\.?)\s*(\d+)\s*(?:of\s*the\s*)?(?:iea|indian\s*evidence\s*act)"

        # Verify IPC citations
        for match in re.finditer(ipc_pattern, text):
            sec_num = match.group(1)
            results["is_compliant"] = False
            bns_mapping = self.ipc_map.get(sec_num, "UNKNOWN")
            
            # Special manual override for highly common cheat/theft consolidations
            if sec_num == "420":
                bns_mapping = "Section 318(4) of the Bharatiya Nyaya Sanhita, 2023 (Cheating and dishonestly inducing delivery of property)"
            elif sec_num == "378" or sec_num == "379":
                bns_mapping = "Section 303 of the Bharatiya Nyaya Sanhita, 2023 (Theft)"

            detail = {
                "matched_text": match.group(0),
                "type": "IPC",
                "old_section": sec_num,
                "status": "DEPRECATED",
                "suggested_replacement": bns_mapping
            }
            results["citations_found"].append(detail)
            results["warnings"].append(
                f"Deprecated citation found: '{match.group(0)}'. "
                f"The Indian Penal Code, 1860 is replaced by the Bharatiya Nyaya Sanhita (BNS), 2023."
            )
            if bns_mapping != "REMOVED" and bns_mapping != "UNKNOWN":
                # Clean up descriptions to keep suggestions concise
                clean_mapping = bns_mapping.split("\n")[0].split(":")[0].strip()
                results["suggestions"].append({
                    "original": match.group(0),
                    "replacement": f"{clean_mapping} of BNS, 2023"
                })

        # Verify CrPC citations
        for match in re.finditer(crpc_pattern, text):
            sec_num = match.group(1)
            results["is_compliant"] = False
            bnss_mapping = self.crpc_map.get(sec_num, "UNKNOWN")
            
            detail = {
                "matched_text": match.group(0),
                "type": "CrPC",
                "old_section": sec_num,
                "status": "DEPRECATED",
                "suggested_replacement": bnss_mapping
            }
            results["citations_found"].append(detail)
            results["warnings"].append(
                f"Deprecated citation found: '{match.group(0)}'. "
                f"The CrPC, 1973 is replaced by the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023."
            )
            if bnss_mapping != "REMOVED" and bnss_mapping != "UNKNOWN":
                clean_mapping = bnss_mapping.split("\n")[0].split(":")[0].strip()
                results["suggestions"].append({
                    "original": match.group(0),
                    "replacement": f"Section {clean_mapping} of BNSS, 2023"
                })

        # Verify IEA (Evidence) citations
        for match in re.finditer(iea_pattern, text):
            sec_num = match.group(1)
            results["is_compliant"] = False
            bsa_mapping = self.iea_map.get(sec_num, "UNKNOWN")
            
            detail = {
                "matched_text": match.group(0),
                "type": "IEA",
                "old_section": sec_num,
                "status": "DEPRECATED",
                "suggested_replacement": bsa_mapping
            }
            results["citations_found"].append(detail)
            results["warnings"].append(
                f"Deprecated citation found: '{match.group(0)}'. "
                f"The Indian Evidence Act, 1872 is replaced by the Bharatiya Sakshya Adhiniyam (BSA), 2023."
            )
            if bsa_mapping != "REMOVED" and bsa_mapping != "UNKNOWN":
                clean_mapping = bsa_mapping.split("\n")[0].split(":")[0].strip()
                results["suggestions"].append({
                    "original": match.group(0),
                    "replacement": f"Section {clean_mapping} of BSA, 2023"
                })

        return results

# Singleton instance
checker = CitationChecker()
