"""
Clausely Hyper-Verification & Internal Consistency Engine.

Implements Stage 3: Internal Consistency Re-Checks, Entity Cross-Reference Checks,
Quant Engine Penalty Auditing, and Semantic Variance Control.
"""

from __future__ import annotations
import math
import re
from collections import Counter
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from engine.evidence_matrix import EvidenceMatrix, EvidenceAtom

class BayesianConfidenceResult(BaseModel):
    """Result of a Bayesian confidence evaluation on a legal claim."""
    confidence_score: float = Field(..., description="Bayesian confidence score between 0.0 and 1.0")
    prior_probability: float = Field(..., description="Initial probability prior P(H)")
    evidence_likelihood: float = Field(..., description="Evidence likelihood metric P(E|H)")
    marginal_likelihood: float = Field(..., description="Marginal likelihood P(E)")

class EntityCrossCheckResult(BaseModel):
    """Audit report for physical and spatial entity cross-referencing."""
    line_of_sight_valid: bool = Field(..., description="True if line-of-sight is physically possible")
    ambient_noise_valid: bool = Field(..., description="True if hearing is possible under ambient noise level")
    spatial_coords_valid: bool = Field(..., description="True if coordinates are within jurisdiction boundary")
    medical_diagnosis_matches: bool = Field(..., description="True if medical reports match injury claims")
    forensic_date_valid: bool = Field(..., description="True if forensic recovery post-dates incident time")
    cdr_alignment_valid: bool = Field(..., description="True if call data records match statement location/time")
    warnings: List[str] = Field(default_factory=list, description="List of physical impossibility warning messages")

class SemanticVarianceReport(BaseModel):
    """Linguistic and formatting consistency metrics."""
    jargon_density: float = Field(..., description="Calculated density of legal jargon in the text")
    active_voice_ratio: float = Field(..., description="Ratio of active vs passive voice usage")
    format_compliant: bool = Field(..., description="True if adhering strictly to court formatting rules")
    synonyms_matched: Dict[str, str] = Field(default_factory=dict, description="Synonyms mapped to canonical terms")
    warnings: List[str] = Field(default_factory=list, description="Linguistic style or formatting deviations")

class QuantAuditResult(BaseModel):
    """Result of UCT score penalty audit and pruning decision."""
    original_uct: float = Field(..., description="Original UCT score before audit")
    adjusted_uct: float = Field(..., description="Adjusted UCT score after penalty applied")
    penalty_applied: float = Field(..., description="UCT penalty amount applied")
    pruned: bool = Field(..., description="True if branch should be pruned")
    reason: str = Field(..., description="Reason for UCT penalty or pruning")

class ConsistencyEngine:
    """
    Stage 3 Hyper-Verification Engine.
    Executes micro-verification thread loops, spatial checks, and stylistic auditing.
    """

    def __init__(self, f_matrix: EvidenceMatrix) -> None:
        """Initialize consistency engine with factual matrix data."""
        self.f_matrix = f_matrix
        self.keyword_index = {}
        for atom in f_matrix.atoms:
            words = re.findall(r'\b\w{3,}\b', atom.description.lower())
            for word in words:
                if word not in self.keyword_index:
                    self.keyword_index[word] = []
                self.keyword_index[word].append(atom)

    def verify_claim(self, claim: str, temperature: float) -> BayesianConfidenceResult:
        """
        Execute claim verification against F_matrix across varying temperature bounds.
        Computes the resulting Bayesian Confidence Score.
        """
        def _tokenize(text: str) -> set[str]:
            words = re.findall(r'\b\w{3,}\b', text.lower())
            return set(words)

        claim_tokens = _tokenize(claim)
        relevant_atoms = []
        for atom in self.f_matrix.atoms:
            atom_tokens = _tokenize(atom.description)
            intersection = claim_tokens.intersection(atom_tokens)
            if intersection:
                overlap_ratio = len(intersection) / max(1, len(claim_tokens))
                relevant_atoms.append((atom, overlap_ratio))

        if not relevant_atoms:
            prior = 0.5
            likelihood = 0.5
            marginal = 0.5
            score = 0.5
        else:
            total_weight = sum(w for _, w in relevant_atoms)
            if total_weight > 0:
                prior = sum(atom.confidence * w for atom, w in relevant_atoms) / total_weight
            else:
                prior = 0.5
            prior = max(0.01, min(0.99, prior))

            max_overlap = max(w for _, w in relevant_atoms)
            temp_factor = max(0.0, 1.0 - 0.2 * temperature)

            likelihood = 0.5 + 0.49 * max_overlap * temp_factor
            likelihood = max(0.01, min(0.99, likelihood))

            likelihood_not_h = 0.5 - 0.49 * max_overlap * temp_factor
            likelihood_not_h = max(0.01, min(0.99, likelihood_not_h))

            marginal = likelihood * prior + likelihood_not_h * (1.0 - prior)
            marginal = max(0.01, min(0.99, marginal))

            score = (likelihood * prior) / marginal
            score = max(0.0, min(1.0, score))

        return BayesianConfidenceResult(
            confidence_score=score,
            prior_probability=prior,
            evidence_likelihood=likelihood,
            marginal_likelihood=marginal
        )

    def measure_cosine_distance(self, claim: str) -> float:
        """Measure distance of claim to F_matrix root concepts."""
        claim_tokens = re.findall(r'\b\w+\b', claim.lower())
        claim_counter = Counter(claim_tokens)

        matrix_counter = Counter()
        for atom in self.f_matrix.atoms:
            matrix_counter.update(re.findall(r'\b\w+\b', atom.description.lower()))

        if not matrix_counter or not claim_counter:
            return 1.0

        all_words = set(matrix_counter.keys()).union(set(claim_counter.keys()))
        dot_product = 0.0
        matrix_norm_sq = 0.0
        claim_norm_sq = 0.0

        for word in all_words:
            m_val = matrix_counter[word]
            c_val = claim_counter[word]
            dot_product += m_val * c_val
            matrix_norm_sq += m_val * m_val
            claim_norm_sq += c_val * c_val

        if matrix_norm_sq == 0 or claim_norm_sq == 0:
            return 1.0

        similarity = dot_product / (math.sqrt(matrix_norm_sq) * math.sqrt(claim_norm_sq))
        distance = 1.0 - similarity
        return max(0.0, min(1.0, distance))

    def generate_negation_states(self, claim: str) -> List[str]:
        """Generate alternate negation claim states for consistency checking."""
        negations = []
        if not claim:
            return negations

        negations.append(f"It is not the case that {claim[0].lower() + claim[1:] if len(claim) > 1 else claim}")

        words = claim.split()
        substituted = False

        verbs_map = {
            "was": "was not",
            "is": "is not",
            "did": "did not",
            "has": "has not",
            "should": "should not",
            "must": "must not",
            "can": "cannot",
            "will": "will not",
            "valid": "invalid",
            "compliant": "non-compliant",
            "agree": "disagree",
            "agreed": "disagreed",
            "occurred": "did not occur",
            "signed": "did not sign",
            "breached": "did not breach"
        }

        new_words = []
        for word in words:
            clean_word = word.strip(".,;:!?\"'()").lower()
            if clean_word in verbs_map:
                replacement = verbs_map[clean_word]
                if word[0].isupper():
                    replacement = replacement.capitalize()
                idx = word.find(clean_word)
                prefix = word[:idx]
                suffix = word[idx + len(clean_word):]
                new_words.append(prefix + replacement + suffix)
                substituted = True
            else:
                new_words.append(word)

        if substituted:
            negations.append(" ".join(new_words))
        else:
            negations.append(f"No evidence supports that {claim[0].lower() + claim[1:] if len(claim) > 1 else claim}")

        negations.append(f"Contrary to the assertion, {claim[0].lower() + claim[1:] if len(claim) > 1 else claim} is false")

        return list(dict.fromkeys(negations))

    def count_non_factual_entities(self, text: str) -> int:
        """Count frequency of non-factual or ungrounded entities in text."""
        candidates = re.findall(r'\b[A-Z][a-zA-Z0-9_]+\b', text)

        grounded_vocab = set()
        for atom in self.f_matrix.atoms:
            if atom.grounded:
                words = re.findall(r'\b\w+\b', f"{atom.atom_id} {atom.description} {atom.source}".lower())
                grounded_vocab.update(words)

        ungrounded_count = 0
        seen_entities = set()
        for candidate in candidates:
            cand_lower = candidate.lower()
            if cand_lower in seen_entities:
                continue
            seen_entities.add(cand_lower)
            if cand_lower not in grounded_vocab:
                ungrounded_count += 1

        return ungrounded_count

    def check_logical_connectivity(self, premise: str, conclusion: str) -> bool:
        """Evaluate logical connectivity between premise and conclusion."""
        p_words = set(w.lower() for w in re.findall(r'\b\w{3,}\b', premise))
        c_words = set(w.lower() for w in re.findall(r'\b\w{3,}\b', conclusion))

        if not p_words or not c_words:
            return False

        overlap = p_words.intersection(c_words)

        shared_atoms = False
        for atom in self.f_matrix.atoms:
            atom_words = set(w.lower() for w in re.findall(r'\b\w{3,}\b', atom.description))
            if p_words.intersection(atom_words) and c_words.intersection(atom_words):
                shared_atoms = True
                break

        return len(overlap) > 0 or shared_atoms

    def audit_entity_cross_references(
        self,
        claim: str,
        witness_coords: Tuple[float, float],
        event_coords: Tuple[float, float],
        ambient_noise_db: float,
        medical_record: Optional[Dict[str, Any]] = None,
        forensic_record: Optional[Dict[str, Any]] = None,
        cdr_record: Optional[Dict[str, Any]] = None,
    ) -> EntityCrossCheckResult:
        """
        Verify physical entity bounds, ambient noise levels, and temporal forensic alignments.
        """
        warnings = []

        dx = witness_coords[0] - event_coords[0]
        dy = witness_coords[1] - event_coords[1]
        distance = math.sqrt(dx*dx + dy*dy)

        line_of_sight_valid = distance <= 200.0
        if not line_of_sight_valid:
            warnings.append(f"Witness distance ({distance:.2f}m) exceeds clear line-of-sight threshold (200m).")

        source_db = 90.0
        if distance > 1.0:
            received_db = source_db - 20 * math.log10(distance)
        else:
            received_db = source_db

        ambient_noise_valid = received_db > ambient_noise_db and received_db > 30.0
        if not ambient_noise_valid:
            warnings.append(f"Received audio signal ({received_db:.2f} dB) drowned by ambient noise ({ambient_noise_db} dB).")

        spatial_coords_valid = (0.0 <= event_coords[0] <= 500.0) and (0.0 <= event_coords[1] <= 500.0)
        if not spatial_coords_valid:
            warnings.append(f"Event coordinates {event_coords} lie outside the legal jurisdiction boundary.")

        medical_diagnosis_matches = True
        if medical_record:
            diagnosis = medical_record.get("diagnosis", "").lower()
            claim_lower = claim.lower()
            injury_keywords = ["fracture", "broken", "break", "injury", "concussion", "wound", "bruise", "trauma", "pain"]
            has_injury_claim = any(kw in claim_lower for kw in injury_keywords)
            if has_injury_claim:
                matches_diagnosis = any(kw in diagnosis for kw in injury_keywords)
                if not matches_diagnosis:
                    medical_diagnosis_matches = False
                    warnings.append(f"Medical diagnosis '{diagnosis}' does not support injury claims in statement.")

        forensic_date_valid = True
        if forensic_record:
            recovery_time = forensic_record.get("recovery_timestamp_ms", 0)
            incident_time = forensic_record.get("incident_timestamp_ms", 0)
            if recovery_time <= incident_time:
                forensic_date_valid = False
                warnings.append("Forensic evidence recovery timestamp predates or matches the incident timestamp.")

        cdr_alignment_valid = True
        if cdr_record:
            cdr_coords = cdr_record.get("tower_coords", (0.0, 0.0))
            tower_dx = cdr_coords[0] - witness_coords[0]
            tower_dy = cdr_coords[1] - witness_coords[1]
            tower_dist = math.sqrt(tower_dx*tower_dx + tower_dy*tower_dy)

            if tower_dist > 100.0:
                cdr_alignment_valid = False
                warnings.append(f"CDR cell tower distance ({tower_dist:.2f}m) indicates witness was not at the stated coordinates.")

        return EntityCrossCheckResult(
            line_of_sight_valid=line_of_sight_valid,
            ambient_noise_valid=ambient_noise_valid,
            spatial_coords_valid=spatial_coords_valid,
            medical_diagnosis_matches=medical_diagnosis_matches,
            forensic_date_valid=forensic_date_valid,
            cdr_alignment_valid=cdr_alignment_valid,
            warnings=warnings
        )

    def audit_quant_engine_penalties(
        self,
        uct_score: float,
        visits: int,
        parent_visits: int,
        p_assumption: float,
        exploration_weight: float = 1.414,
    ) -> QuantAuditResult:
        """
        Evaluate node parameters and apply UCT penalty adjustments or branch pruning.
        Returns the updated UCT score and whether the branch should be pruned.
        """
        # Validate inputs
        if not (0.0 <= p_assumption <= 1.0):
            raise ValueError("p_assumption must be between 0.0 and 1.0")
        if visits < 0 or parent_visits < 0:
            raise ValueError("visits and parent_visits must be non-negative")

        # Calculate base penalty based on assumption score
        penalty = 1000.0 * p_assumption
        adjusted_uct = uct_score - penalty

        # Apply additional quant penalty if confidence is below 0.99
        confidence = 1.0 - p_assumption
        if confidence < 0.99:
            adjusted_uct -= 50.0
            penalty += 50.0

        # Prune branches where adjusted UCT score < 0.1
        pruned = False
        reason = "Clean execution"
        if adjusted_uct < 0.1:
            pruned = True
            reason = f"UCT score {adjusted_uct:.4f} is below minimum threshold 0.1"

        return QuantAuditResult(
            original_uct=uct_score,
            adjusted_uct=adjusted_uct,
            penalty_applied=penalty,
            pruned=pruned,
            reason=reason,
        )

    def audit_semantic_variance(
        self,
        draft_text: str,
        jurisdiction: str,
    ) -> SemanticVarianceReport:
        """
        Analyze linguistic consistency, jargon density, and court style compliance.
        """
        warnings = []
        words = re.findall(r'\b\w+\b', draft_text.lower())
        if not words:
            return SemanticVarianceReport(
                jargon_density=0.0,
                active_voice_ratio=1.0,
                format_compliant=True,
                synonyms_matched={},
                warnings=["Empty draft text provided."]
            )

        # 1. Jargon density
        legal_jargon = {
            "herein", "therein", "hereinafter", "aforesaid", "statute", "jurisdiction",
            "plaintiff", "defendant", "petitioner", "respondent", "tort", "contract",
            "breach", "liability", "damages", "affidavit", "testimony", "evidence",
            "claim", "suit", "motion", "whereas", "hereby", "pursuant", "section", "article"
        }
        jargon_count = sum(1 for w in words if w in legal_jargon)
        jargon_density = jargon_count / len(words)

        # 2. Active voice ratio
        passive_auxiliaries = {"is", "was", "were", "been", "be", "being", "are", "am"}
        irregular_participles = {"taken", "written", "given", "held", "found", "made", "seen", "heard", "done", "sent", "paid"}

        passive_count = 0
        total_verbs = 0
        words_original = re.findall(r'\b\w+\b', draft_text)

        for i in range(len(words_original) - 1):
            w = words_original[i].lower()
            next_w = words_original[i+1].lower()
            if w in passive_auxiliaries:
                total_verbs += 1
                if next_w.endswith("ed") or next_w.endswith("en") or next_w in irregular_participles:
                    passive_count += 1
            elif w.endswith("ed") or w in {"wrote", "gave", "held", "found", "made", "saw", "heard", "did", "sent", "paid", "agreed", "signed"}:
                total_verbs += 1

        active_voice_ratio = 1.0
        if total_verbs > 0:
            active_voice_ratio = 1.0 - (passive_count / total_verbs)

        # 3. Format compliance
        draft_lower = draft_text.lower()
        has_court = "court" in draft_lower
        has_parties = "vs" in draft_lower or "versus" in draft_lower or " v. " in draft_text

        format_compliant = has_court and has_parties
        if not format_compliant:
            if not has_court:
                warnings.append("Document missing reference to the Court.")
            if not has_parties:
                warnings.append("Document missing party designation (vs/v.).")

        # 4. Synonym mapping
        synonym_map = {
            "sued": "filed suit",
            "broke": "breached",
            "agreement": "contract",
            "pay": "indemnify",
            "robbed": "converted",
            "theft": "conversion",
            "stealing": "conversion",
            "liar": "untruthful witness"
        }
        synonyms_matched = {}
        for word in words:
            if word in synonym_map:
                synonyms_matched[word] = synonym_map[word]

        return SemanticVarianceReport(
            jargon_density=jargon_density,
            active_voice_ratio=active_voice_ratio,
            format_compliant=format_compliant,
            synonyms_matched=synonyms_matched,
            warnings=warnings
        )
