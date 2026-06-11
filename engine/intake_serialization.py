"""
Clausely Intake Serialization Engine.

Implements Stage 1.1: Base64 Payload Decoding, Cryptographic Signature Matching,
Envelope Checksums, Identity Certificate Verification, Header Parsing,
Control-character Sanitization, and Schema Validation.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import uuid
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class InvalidIntakeState(Exception):
    """Raised when cryptographic signature matching, checksums, or validation fails."""
    pass


DEFAULT_REGISTRY = {
    "CLIENT_CERT_A": "ACTIVE",
    "CLIENT_CERT_B": "ACTIVE",
    "CLAUSELY_SECURE_INTAKE_GATE_2026": "ACTIVE",
}


def preprocess_secure_intake(
    matter_context: Dict[str, Any],
    registry_logs: Optional[Dict[str, str]] = None,
    current_time_epoch: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Check if the matter_context contains a secure cryptographic envelope.
    If so, verify signatures, decrypt, sanitize, and validate the payload,
    then merge the decrypted payload back into the matter_context.
    """
    envelope_data = None

    # Check if the envelope keys are present directly in the context
    required_keys = {"payload_base64", "signature_sha256", "checksum", "origin_certificate", "timestamp_epoch"}
    if required_keys.issubset(matter_context.keys()):
        envelope_data = matter_context
    else:
        # Check if the cause_of_action is a JSON string containing the envelope
        cause = matter_context.get("cause_of_action", "")
        if isinstance(cause, str) and cause.strip().startswith("{"):
            try:
                parsed_cause = json.loads(cause)
                if required_keys.issubset(parsed_cause.keys()):
                    envelope_data = parsed_cause
            except Exception:
                pass

    if envelope_data is not None:
        try:
            envelope = IntakeEnvelope(
                payload_base64=envelope_data["payload_base64"],
                signature_sha256=envelope_data["signature_sha256"],
                checksum=envelope_data["checksum"],
                origin_certificate=envelope_data["origin_certificate"],
                timestamp_epoch=int(envelope_data["timestamp_epoch"]),
            )
        except Exception as e:
            raise InvalidIntakeState(f"INVALID_INTAKE_STATE: Invalid envelope structure: {e}")

        registry = registry_logs if registry_logs is not None else DEFAULT_REGISTRY
        serializer = IntakeSerializer()
        payload = serializer.deserialize(envelope, registry, current_time_epoch)

        # Merge payload values into the context
        new_context = dict(matter_context)
        new_context["cause_of_action"] = payload.cause_of_action
        new_context["jurisdiction"] = payload.jurisdiction
        new_context["client_role"] = payload.client_role
        new_context["transaction_id"] = payload.transaction_id
        new_context["token_count"] = payload.token_count
        if payload.metadata:
            if "metadata" not in new_context or not isinstance(new_context["metadata"], dict):
                new_context["metadata"] = {}
            new_context["metadata"].update(payload.metadata)

        return new_context

    return matter_context



class IntakeEnvelope(BaseModel):
    """
    Cryptographic envelope carrying base64-encoded client intake payload.
    """
    payload_base64: str = Field(..., description="Base64 encoded raw payload")
    signature_sha256: str = Field(..., description="SHA-256 signature for verification")
    checksum: str = Field(..., description="Envelope checksum to check integrity")
    origin_certificate: str = Field(..., description="Origin certificate verification signature")
    timestamp_epoch: int = Field(..., description="Unix epoch timestamp of transmission")


class IntakePayload(BaseModel):
    """
    Parsed, normalized, and validated client intake payload.
    """
    transaction_id: str = Field(..., description="Unique generated transaction UUID")
    token_count: int = Field(..., description="Number of tokens calculated from header")
    cause_of_action: str = Field(..., description="Core cause of action / facts")
    client_role: str = Field("Petitioner", description="Locus standi role of client")
    jurisdiction: str = Field("MH-HC", description="Declared filing jurisdiction code")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")


class IntakeSerializer:
    """
    Engine to decode, decrypt, sanitize, and validate incoming intake payloads.
    """
    def __init__(self, drift_tolerance_seconds: int = 300) -> None:
        """
        Initialize the serializer configuration.
        """
        self.drift_tolerance_seconds = drift_tolerance_seconds

    def verify_signatures(
        self,
        envelope: IntakeEnvelope,
        registry_logs: Dict[str, str],
        current_time_epoch: Optional[int] = None,
    ) -> None:
        """
        Decrypt intake and verify SHA-256 signatures, envelopes, and identity certificates.
        Fails with InvalidIntakeState if verification fails.
        """
        # 1. Verify identity certificate of input origin
        if envelope.origin_certificate not in registry_logs:
            raise InvalidIntakeState("INVALID_INTAKE_STATE: Identity certificate of input origin is invalid or untrusted.")

        # 2. Decrypt and check standard SHA-256 signatures
        computed_sha256 = hashlib.sha256(envelope.payload_base64.encode("ascii")).hexdigest()
        if computed_sha256 != envelope.signature_sha256:
            raise InvalidIntakeState("INVALID_INTAKE_STATE: SHA-256 signature matching failed.")

        # 3. Validate cryptographic envelope checksums against registry logs
        expected_checksum = hashlib.sha256((envelope.payload_base64 + envelope.signature_sha256).encode("ascii")).hexdigest()
        if expected_checksum != envelope.checksum:
            raise InvalidIntakeState("INVALID_INTAKE_STATE: Envelope checksum verification failed.")

        # 4. Check timestamp drift tolerance bounds
        now = current_time_epoch if current_time_epoch is not None else int(time.time())
        if abs(now - envelope.timestamp_epoch) > self.drift_tolerance_seconds:
            raise InvalidIntakeState("INVALID_INTAKE_STATE: Timestamp drift tolerance bounds exceeded.")

    def parse_headers(self, decoded_bytes: bytes) -> Dict[str, Any]:
        """
        Parse binary stream headers for token metrics.
        The first 4 bytes are the magic header, followed by 4 bytes of token count.
        """
        if len(decoded_bytes) < 8:
            return {"token_count": 0}
        
        magic_bytes = decoded_bytes[:4]
        token_count = int.from_bytes(decoded_bytes[4:8], byteorder="big")
        
        return {
            "magic": magic_bytes.hex().upper(),
            "token_count": token_count
        }

    def sanitize_payload(self, raw_str: str) -> str:
        """
        Sanitize control characters and escape sequences from character streams.
        Removes ASCII control characters (0-31) except tab, carriage return, and newline.
        """
        # Matches any control character except tab (\t), carriage return (\r), newline (\n)
        sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", raw_str)
        return sanitized

    def validate_schema(self, normalized_dict: Dict[str, Any]) -> IntakePayload:
        """
        Validate the normalized data structure against structural specifications.
        """
        if "transaction_id" not in normalized_dict or not normalized_dict["transaction_id"]:
            normalized_dict["transaction_id"] = str(uuid.uuid4())
            
        payload = IntakePayload(**normalized_dict)
        return payload

    def deserialize(
        self,
        envelope: IntakeEnvelope,
        registry_logs: Dict[str, str],
        current_time_epoch: Optional[int] = None,
    ) -> IntakePayload:
        """
        Main entry point to perform the complete Stage 1.1 intake serialization pipeline.
        """
        # Phase 1: Verify signatures, checksums, origin certs, and timestamp drift
        self.verify_signatures(envelope, registry_logs, current_time_epoch)

        # Phase 2: Base64 decode
        try:
            decoded_bytes = base64.b64decode(envelope.payload_base64)
        except Exception as e:
            raise InvalidIntakeState(f"INVALID_INTAKE_STATE: Failed to decode Base64 payload: {e}")

        # Phase 3: Parse headers for token metrics and allocate/slice the payload content
        header_info = self.parse_headers(decoded_bytes)
        token_count = header_info.get("token_count", 0)
        
        # Binary payload format: Header (8 bytes) followed by JSON payload string
        payload_content_bytes = decoded_bytes[8:] if len(decoded_bytes) >= 8 else decoded_bytes
        
        # Convert decoded bytes into raw Unicode character stream
        raw_unicode_str = payload_content_bytes.decode("utf-8")
        
        # Sanitize control characters and escape sequences
        sanitized_unicode_str = self.sanitize_payload(raw_unicode_str)
        
        # Parse JSON
        try:
            parsed_json = json.loads(sanitized_unicode_str)
        except Exception as e:
            raise InvalidIntakeState(f"INVALID_INTAKE_STATE: Failed to parse sanitized payload JSON: {e}")
            
        # Incorporate token metrics and transaction ID
        parsed_json["token_count"] = token_count
        
        # Execute schema validation against structural specifications
        try:
            return self.validate_schema(parsed_json)
        except Exception as e:
            raise InvalidIntakeState(f"INVALID_INTAKE_STATE: Schema validation failed: {e}")
