import pytest
import base64
import hashlib
import json
import time
from unittest.mock import MagicMock

from engine.intake_serialization import (
    IntakeEnvelope,
    IntakeSerializer,
    InvalidIntakeState,
    IntakePayload,
)

# Mock credentials registry for verification tests
MOCK_REGISTRY = {
    "CLIENT_CERT_A": "ACTIVE",
    "CLIENT_CERT_B": "ACTIVE",
}


def _build_mock_envelope(
    payload_dict: dict,
    cert: str = "CLIENT_CERT_A",
    timestamp: int = 1717150000,
    tamper_payload: bool = False,
    tamper_sig: bool = False,
    tamper_checksum: bool = False,
    bad_base64: bool = False,
) -> IntakeEnvelope:
    # Payload binary format: magic header (4 bytes) + token count (4 bytes) + json content
    json_bytes = json.dumps(payload_dict).encode("utf-8")
    magic = b"\xCA\xFE\xBA\xBE"
    token_count = len(payload_dict.get("cause_of_action", "").split())
    token_count_bytes = token_count.to_bytes(4, byteorder="big")
    
    raw_payload_bytes = magic + token_count_bytes + json_bytes
    
    if bad_base64:
        payload_base64 = "invalid_base64_string_!!!"
    else:
        payload_base64 = base64.b64encode(raw_payload_bytes).decode("ascii")
        
    if tamper_payload:
        payload_base64 += "TAMPER"

    sig = hashlib.sha256(payload_base64.encode("ascii")).hexdigest()
    if tamper_sig:
        sig = sig[:-4] + "0000"

    checksum = hashlib.sha256((payload_base64 + sig).encode("ascii")).hexdigest()
    if tamper_checksum:
        checksum = checksum[:-4] + "9999"

    return IntakeEnvelope(
        payload_base64=payload_base64,
        signature_sha256=sig,
        checksum=checksum,
        origin_certificate=cert,
        timestamp_epoch=timestamp,
    )


def test_successful_deserialization():
    serializer = IntakeSerializer()
    payload_data = {
        "cause_of_action": "Vidya Khobrekar termination challenge",
        "client_role": "Petitioner-in-Person",
        "jurisdiction": "MH-HC",
    }
    
    envelope = _build_mock_envelope(payload_data, timestamp=1717150000)
    
    # Run deserializer with corresponding current time epoch (no drift)
    parsed = serializer.deserialize(
        envelope,
        registry_logs=MOCK_REGISTRY,
        current_time_epoch=1717150000,
    )
    
    assert parsed.cause_of_action == "Vidya Khobrekar termination challenge"
    assert parsed.client_role == "Petitioner-in-Person"
    assert parsed.jurisdiction == "MH-HC"
    assert parsed.token_count == 4
    assert parsed.transaction_id is not None


def test_invalid_origin_certificate():
    serializer = IntakeSerializer()
    payload_data = {"cause_of_action": "test facts"}
    
    # Use un-registered certificate
    envelope = _build_mock_envelope(payload_data, cert="UNTRUSTED_CERT")
    
    with pytest.raises(InvalidIntakeState) as exc:
        serializer.deserialize(envelope, registry_logs=MOCK_REGISTRY, current_time_epoch=1717150000)
    assert "Identity certificate" in str(exc.value)


def test_signature_mismatch():
    serializer = IntakeSerializer()
    payload_data = {"cause_of_action": "test facts"}
    
    # Tamper with the signature
    envelope = _build_mock_envelope(payload_data, tamper_sig=True)
    
    with pytest.raises(InvalidIntakeState) as exc:
        serializer.deserialize(envelope, registry_logs=MOCK_REGISTRY, current_time_epoch=1717150000)
    assert "SHA-256 signature matching failed" in str(exc.value)


def test_checksum_mismatch():
    serializer = IntakeSerializer()
    payload_data = {"cause_of_action": "test facts"}
    
    # Tamper with the checksum
    envelope = _build_mock_envelope(payload_data, tamper_checksum=True)
    
    with pytest.raises(InvalidIntakeState) as exc:
        serializer.deserialize(envelope, registry_logs=MOCK_REGISTRY, current_time_epoch=1717150000)
    assert "checksum verification failed" in str(exc.value)


def test_timestamp_drift_bounds():
    serializer = IntakeSerializer(drift_tolerance_seconds=120)
    payload_data = {"cause_of_action": "test facts"}
    
    # 200 seconds drift (exceeds tolerance of 120)
    envelope = _build_mock_envelope(payload_data, timestamp=1717150000)
    
    with pytest.raises(InvalidIntakeState) as exc:
        serializer.deserialize(
            envelope,
            registry_logs=MOCK_REGISTRY,
            current_time_epoch=1717150200,
        )
    assert "Timestamp drift" in str(exc.value)


def test_control_character_sanitization():
    serializer = IntakeSerializer()
    raw_str = "Clean\x00Text\x1F\nWith\x08Backspaces"
    sanitized = serializer.sanitize_payload(raw_str)
    
    # Tab, newline and carriage return should remain, others stripped
    assert sanitized == "CleanText\nWithBackspaces"


def test_schema_validation_failure():
    serializer = IntakeSerializer()
    
    # Missing required 'cause_of_action' field in the schema
    payload_data = {
        "client_role": "Petitioner",
    }
    envelope = _build_mock_envelope(payload_data)
    
    with pytest.raises(InvalidIntakeState) as exc:
        serializer.deserialize(
            envelope,
            registry_logs=MOCK_REGISTRY,
            current_time_epoch=1717150000,
        )
    assert "Schema validation failed" in str(exc.value)


def test_preprocess_secure_intake_direct_context():
    from engine.intake_serialization import preprocess_secure_intake
    payload_data = {
        "cause_of_action": "Vidya Khobrekar termination challenge",
        "client_role": "Petitioner-in-Person",
        "jurisdiction": "MH-HC",
    }
    envelope = _build_mock_envelope(payload_data, timestamp=1717150000)
    
    input_context = {
        "payload_base64": envelope.payload_base64,
        "signature_sha256": envelope.signature_sha256,
        "checksum": envelope.checksum,
        "origin_certificate": envelope.origin_certificate,
        "timestamp_epoch": envelope.timestamp_epoch,
        "custom_field": "keep_this",
    }
    
    processed = preprocess_secure_intake(
        input_context,
        registry_logs=MOCK_REGISTRY,
        current_time_epoch=1717150000,
    )
    
    assert processed["cause_of_action"] == "Vidya Khobrekar termination challenge"
    assert processed["jurisdiction"] == "MH-HC"
    assert processed["client_role"] == "Petitioner-in-Person"
    assert processed["custom_field"] == "keep_this"
    assert "transaction_id" in processed
    assert processed["token_count"] == 4


def test_preprocess_secure_intake_nested_in_cause_of_action():
    from engine.intake_serialization import preprocess_secure_intake
    payload_data = {
        "cause_of_action": "Another case",
        "client_role": "Petitioner",
        "jurisdiction": "MH-DISTRICT",
    }
    envelope = _build_mock_envelope(payload_data, timestamp=1717150000)
    
    envelope_json = json.dumps({
        "payload_base64": envelope.payload_base64,
        "signature_sha256": envelope.signature_sha256,
        "checksum": envelope.checksum,
        "origin_certificate": envelope.origin_certificate,
        "timestamp_epoch": envelope.timestamp_epoch,
    })
    
    input_context = {
        "cause_of_action": envelope_json,
        "custom_field": "keep_this",
    }
    
    processed = preprocess_secure_intake(
        input_context,
        registry_logs=MOCK_REGISTRY,
        current_time_epoch=1717150000,
    )
    
    assert processed["cause_of_action"] == "Another case"
    assert processed["jurisdiction"] == "MH-DISTRICT"
    assert processed["client_role"] == "Petitioner"
    assert processed["custom_field"] == "keep_this"


def test_preprocess_secure_intake_invalid_signature_raises():
    from engine.intake_serialization import preprocess_secure_intake
    payload_data = {"cause_of_action": "test facts"}
    envelope = _build_mock_envelope(payload_data, tamper_sig=True, timestamp=1717150000)
    
    input_context = {
        "payload_base64": envelope.payload_base64,
        "signature_sha256": envelope.signature_sha256,
        "checksum": envelope.checksum,
        "origin_certificate": envelope.origin_certificate,
        "timestamp_epoch": envelope.timestamp_epoch,
    }
    
    with pytest.raises(InvalidIntakeState) as exc:
        preprocess_secure_intake(
            input_context,
            registry_logs=MOCK_REGISTRY,
            current_time_epoch=1717150000,
        )
    assert "signature matching failed" in str(exc.value)


def test_run_clausely_with_invalid_secure_envelope():
    import asyncio
    from agents.orchestrator import run_clausely
    
    payload_data = {"cause_of_action": "test facts"}
    envelope = _build_mock_envelope(payload_data, tamper_sig=True, timestamp=1717150000)
    
    input_context = {
        "payload_base64": envelope.payload_base64,
        "signature_sha256": envelope.signature_sha256,
        "checksum": envelope.checksum,
        "origin_certificate": envelope.origin_certificate,
        "timestamp_epoch": envelope.timestamp_epoch,
    }
    
    mock_runner = MagicMock()
    with pytest.raises(InvalidIntakeState) as exc:
        asyncio.run(run_clausely(mock_runner, input_context))
    
    assert "signature matching failed" in str(exc.value)

