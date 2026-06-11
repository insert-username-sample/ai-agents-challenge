# =====================================================================
# CLAUSELY: EVIDENCE ATOM MATRIX
# =====================================================================
# This file implements the EvidenceAtom and EvidenceMatrix data
# structures to handle PPAP (Pen-Pineapple-Apple-Pen) level granularity.
# =====================================================================

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class EvidenceAtom:
    """
    Smallest indivisible evidence unit.
    Acts as a butterfly effect state shift descriptor.
    """
    atom_id: str
    description: str
    timestamp_ms: int
    confidence: float
    source: str              # witness / document / forensic
    grounded: bool = False
    butterfly_weight: float = 1.0
    linked_atoms: List[str] = field(default_factory=list)

    def shifts_timeline(self, threshold: float = 0.3) -> bool:
        """Evaluate if the weight of this atom is enough to trigger a branch shift."""
        return self.butterfly_weight * self.confidence > threshold


class EvidenceMatrix:
    """
    F_matrix for micro-detail evidence tracking.
    Enforces that PPAP level evidence resides in Python structures.
    """
    def __init__(self, atoms: List[EvidenceAtom]):
        self.atoms = atoms

    def butterfly_score(self, atom: EvidenceAtom) -> float:
        """Calculate weight influence of the evidence atom."""
        return atom.confidence * atom.butterfly_weight * (1.0 + len(atom.linked_atoms) * 0.1)

    def apply_to_branch(self, branch_state: Dict[str, Any]) -> Dict[str, Any]:
        """Apply butterfly effect shifts to a simulation branch state."""
        modified_state = dict(branch_state)
        sorted_atoms = sorted(self.atoms, key=self.butterfly_score, reverse=True)
        
        for atom in sorted_atoms:
            if atom.shifts_timeline():
                # Enforce state adjustments based on physical micro-details
                desc_lower = atom.description.lower()
                if "signature" in desc_lower or "signing" in desc_lower:
                    modified_state["signature_validity"] = "doubtful"
                    modified_state["defect_penalty"] = modified_state.get("defect_penalty", 0.0) + 0.3
                if "delay" in desc_lower or "limitation" in desc_lower:
                    modified_state["limitation_status"] = "delayed"
                    modified_state["defect_penalty"] = modified_state.get("defect_penalty", 0.0) + 0.5
                    
        return modified_state
