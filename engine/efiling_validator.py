import math
from typing import Dict, Any, List

class RegistryComplianceError(ValueError):
    """Raised when document layout or constraints violate Court e-filing manuals."""
    pass

class EFilingValidator:
    """
    Validates structural, typographical, and size constraints 
    required under e-Filing guidelines (e.g., Delhi High Court Rules 2021/2026).
    """

    def validate_layout(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates page parameters: A4 dimensions, margins, font, and line spacing.
        :param metadata: Dict containing layout metrics of the drafted document.
        """
        # A4 size is strictly 29.7cm x 21.0cm
        paper_size = metadata.get("paper_size", "A4").upper()
        if paper_size != "A4":
            raise RegistryComplianceError(f"Rejected: Paper size must be A4, got {paper_size}")

        # Margin rules: Top/Bottom: 2cm, Left/Right: 4cm
        top_margin = metadata.get("top_margin_cm", 2.0)
        bottom_margin = metadata.get("bottom_margin_cm", 2.0)
        left_margin = metadata.get("left_margin_cm", 4.0)
        right_margin = metadata.get("right_margin_cm", 4.0)

        if top_margin < 2.0 or bottom_margin < 2.0:
            raise RegistryComplianceError(
                f"Objection: Top/Bottom margins must be at least 2.0cm. Got Top: {top_margin}cm, Bottom: {bottom_margin}cm"
            )
        if left_margin < 4.0 or right_margin < 4.0:
            raise RegistryComplianceError(
                f"Objection: Left/Right margins must be at least 4.0cm to allow court stitching. Got Left: {left_margin}cm, Right: {right_margin}cm"
            )

        # Typography rules: Times New Roman, Size 14, Spacing 1.5
        font_family = metadata.get("font_family", "Times New Roman").lower()
        font_size = metadata.get("font_size", 14)
        line_spacing = metadata.get("line_spacing", 1.5)

        if "times new roman" not in font_family:
            raise RegistryComplianceError(f"Objection: Allowed primary font is Times New Roman. Got: {font_family}")
        if font_size != 14:
            raise RegistryComplianceError(f"Objection: Standard font size must be exactly 14. Got: {font_size}")
        if line_spacing != 1.5:
            raise RegistryComplianceError(f"Objection: Line spacing must be exactly 1.5. Got: {line_spacing}")

        return {"status": "COMPLIANT", "details": "All layout metrics conform to e-Filing Rules."}

    def validate_upload_limits(self, file_size_mb: float, court_type: str) -> Dict[str, Any]:
        """
        Enforces strict file-size limits: 300MB for High Courts (updated 2026), 20MB for District Courts.
        """
        court = court_type.lower()
        if "district" in court:
            max_limit = 20.0
            if file_size_mb > max_limit:
                raise RegistryComplianceError(
                    f"Objection: District Court upload size limit exceeded. File is {file_size_mb}MB (Max limit: {max_limit}MB). Split file into sub-parts."
                )
        else: # Default High Court
            max_limit = 300.0
            if file_size_mb > max_limit:
                raise RegistryComplianceError(
                    f"Objection: High Court upload size limit exceeded. File is {file_size_mb}MB (Max limit: {max_limit}MB)."
                )

        return {"status": "COMPLIANT", "max_allowed_mb": max_limit}
