# =====================================================================
# CLAUSELY: AGENTIC EXECUTION DEFECT SENTINEL (AEDS)
# =====================================================================
# Detects and intercepts infinite repetition loops and hallucination
# patterns in LLM outputs to prevent compute and token waste.
# =====================================================================

from __future__ import annotations
import zlib
import logging

logger = logging.getLogger("clausely.engine.aeds")


class HallucinationLoopDetected(ValueError):
    """Raised when the AEDS sentinel detects an infinite repetition loop."""
    pass


class AEDSSentinel:
    """
    Agentic Execution Defect Sentinel (AEDS).
    Vets LLM streams and outputs for self-similarity and repetition patterns.
    """

    @staticmethod
    def detect_repetition(text: str, max_repeats: int = 4, min_phrase_len: int = 3) -> bool:
        """
        Detect if a phrase of at least min_phrase_len words is repeated consecutively max_repeats+ times.
        """
        # Strip common punctuation and normalize to lowercase words
        words = [w.strip(".,!?()[]{}*:;- \n\r") for w in text.lower().split() if w.strip()]
        n = len(words)

        if n < min_phrase_len * max_repeats:
            return False

        # Check sliding windows L
        for L in range(min_phrase_len, min(n // max_repeats + 1, 30)):
            for i in range(n - L * max_repeats + 1):
                phrase = words[i:i+L]
                is_loop = True
                for r in range(1, max_repeats):
                    start = i + r * L
                    if words[start:start+L] != phrase:
                        is_loop = False
                        break
                if is_loop:
                    logger.warning(f"[AEDS] Consecutively repeated phrase loop detected: {phrase}")
                    return True
        return False

    @staticmethod
    def detect_compression_anomaly(text: str, threshold_ratio: float = 0.08) -> bool:
        """
        Detects repeating patterns using zlib compression ratio.
        Very low compression ratios indicate high redundancy and looping.
        """
        if len(text) < 100:
            return False

        raw_bytes = text.encode("utf-8")
        compressed_len = len(zlib.compress(raw_bytes))
        ratio = compressed_len / len(raw_bytes)

        if ratio < threshold_ratio:
            logger.warning(f"[AEDS] Compression ratio anomaly: {ratio:.3f} (threshold: {threshold_ratio})")
            return True
        return False

    @staticmethod
    def detect_repeating_lines(text: str, max_line_repeats: int = 5) -> bool:
        """
        Detects if a single line is repeated identically or almost identically
        multiple times, typically a sign of enumeration hallucination.
        """
        import re
        lines = text.strip().split("\n")
        if len(lines) < max_line_repeats:
            return False
            
        # Strip numbering like "1. ", "- ", etc. and normalize
        normalized_lines = []
        for line in lines:
            # remove leading bullets, numbers, punctuation and spaces
            cleaned = re.sub(r"^[\W\d_]+", "", line.strip()).lower()
            if cleaned:
                normalized_lines.append(cleaned)
                
        if not normalized_lines:
            return False

        # Count consecutive identical lines
        consecutive_count = 1
        for i in range(1, len(normalized_lines)):
            if normalized_lines[i] == normalized_lines[i-1]:
                consecutive_count += 1
                if consecutive_count >= max_line_repeats:
                    logger.warning(f"[AEDS] Repeating line loop detected: '{normalized_lines[i]}'")
                    return True
            else:
                consecutive_count = 1
                
        return False

    def validate_content(self, text: str) -> str:
        """
        Validates LLM output text against infinite repetition patterns.
        Raises HallucinationLoopDetected to abort the execution path if a loop is found.
        """
        if (self.detect_repetition(text) or 
            self.detect_compression_anomaly(text) or 
            self.detect_repeating_lines(text)):
            raise HallucinationLoopDetected(
                "AEDS INTERCEPTION: Infinite repetition or hallucination loop detected in model output."
            )
        return text
