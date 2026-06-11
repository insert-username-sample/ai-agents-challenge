import pytest
import hashlib
import json
from engine.drafter_mutator import (
    DrafterTransactionQueue,
    DrafterMutator,
    TransactionPayload,
    TransactionEnvelope,
    AttestationToken,
    UnverifiedTransactionAbortError,
)

def test_queue_push_and_pop_happy_path():
    queue = DrafterTransactionQueue(rate_limit_limit=3)
    
    payload_dict = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"ast_node": "PetitionHeader", "content": "Supreme Court of India"}
    }
    
    envelope = queue.push_transaction(payload_dict, signature="MOCK_SIG", sender_id="petitioner_agent")
    
    assert envelope.signature == "MOCK_SIG"
    assert envelope.reference_index == 0
    assert envelope.payload.sender_id == "petitioner_agent"
    
    popped = queue.pop_transaction()
    assert popped is not None
    assert popped.reference_index == 0
    assert popped.payload.sender_id == "petitioner_agent"
    
    assert queue.pop_transaction() is None

def test_queue_push_structure_mismatch():
    queue = DrafterTransactionQueue()
    
    # Missing required 'role' field
    payload_dict = {
        "sender_id": "petitioner_agent",
        "timestamp": 1717848000.0,
        "payload_data": {}
    }
    
    with pytest.raises(Exception):
        queue.push_transaction(payload_dict, signature="MOCK_SIG", sender_id="petitioner_agent")

def test_queue_rate_limiting():
    queue = DrafterTransactionQueue(rate_limit_limit=2)
    
    payload_dict = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {}
    }
    
    # Push 1
    queue.push_transaction(payload_dict, signature="SIG1", sender_id="petitioner_agent")
    # Push 2
    queue.push_transaction(payload_dict, signature="SIG2", sender_id="petitioner_agent")
    
    # Push 3 should fail
    with pytest.raises(ValueError, match="Rate limit exceeded"):
        queue.push_transaction(payload_dict, signature="SIG3", sender_id="petitioner_agent")

def test_mutator_signature_verification():
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    
    # Setup registry
    mutator.active_registry["petitioner_agent"] = "SECRET123"
    
    payload_dict = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"test_field": "hello"}
    }
    
    # Compute valid signature: SHA-256 of json payload_data + secret
    payload_str = json.dumps(payload_dict["payload_data"], sort_keys=True)
    expected_sig = hashlib.sha256((payload_str + "SECRET123").encode("utf-8")).hexdigest()
    
    # Push to queue with valid signature
    envelope = queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent")
    
    assert mutator.verify_sender_signature(envelope.payload, expected_sig, "petitioner_agent", current_time=1717848000.0) is True
    
    with pytest.raises(UnverifiedTransactionAbortError, match="Signature mismatch occurred"):
        mutator.verify_sender_signature(envelope.payload, "WRONG_SIG", "petitioner_agent", current_time=1717848000.0)
        
    with pytest.raises(UnverifiedTransactionAbortError, match="Sender public key not found"):
        mutator.verify_sender_signature(envelope.payload, expected_sig, "unknown_agent", current_time=1717848000.0)

def test_mutator_attestation_token_verification():
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    
    # Valid token structure
    token_dict = {
        "tx_type": "READY_ATTESTATION",
        "timestamp": "2026-06-08T18:00:00Z",
        "tree_hash": "HASH123",
        "confidence": 0.99
    }
    
    # Compute signature: SHA-256 of tx_type:tree_hash:verifier_public_key
    msg = f"READY_ATTESTATION:HASH123:VERIFIER_KEY"
    expected_sig = hashlib.sha256(msg.encode("utf-8")).hexdigest()
    token_dict["signature"] = expected_sig
    
    token = AttestationToken(**token_dict)
    assert mutator.verify_attestation_token(token) is True
    
    # Bad signature
    token_dict["signature"] = "WRONG_SIG"
    token_bad_sig = AttestationToken(**token_dict)
    assert mutator.verify_attestation_token(token_bad_sig) is False

def test_process_next_transaction_happy_path():
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    mutator.active_registry["petitioner_agent"] = "SECRET123"
    mutator.seed_verifier_ledger("Title", "ACTIVE")
    
    # Make token
    msg = f"READY_ATTESTATION:HASH123:VERIFIER_KEY"
    sig = hashlib.sha256(msg.encode("utf-8")).hexdigest()
    attestation = {
        "tx_type": "READY_ATTESTATION",
        "timestamp": "2026-06-08T18:00:00Z",
        "tree_hash": "HASH123",
        "signature": sig,
        "confidence": 0.995
    }
    
    payload_dict = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"ast_node": "Title", "content": "Simple text"},
        "attestation_token": attestation
    }
    
    payload_str = json.dumps(payload_dict["payload_data"], sort_keys=True)
    expected_sig = hashlib.sha256((payload_str + "SECRET123").encode("utf-8")).hexdigest()
    
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent")
    
    processed = mutator.process_next_transaction(current_time=1717848000.0)
    assert processed is not None
    assert processed.sender_id == "petitioner_agent"
    assert processed.payload_data["content"] == "Simple text"
    assert len(mutator.committed_payloads) == 1

def test_process_next_transaction_signature_mismatch():
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    mutator.active_registry["petitioner_agent"] = "SECRET123"
    
    payload_dict = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"ast_node": "Title", "content": "Simple text"},
    }
    
    # Push with bad signature
    queue.push_transaction(payload_dict, signature="BAD_SIG", sender_id="petitioner_agent")
    
    with pytest.raises(UnverifiedTransactionAbortError, match="Signature mismatch occurred|Sender signature verification failed"):
        mutator.process_next_transaction(current_time=1717848000.0)

def test_process_next_transaction_missing_attestation():
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    mutator.active_registry["petitioner_agent"] = "SECRET123"
    
    payload_dict = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"ast_node": "Title", "content": "Simple text"},
    }
    
    payload_str = json.dumps(payload_dict["payload_data"], sort_keys=True)
    expected_sig = hashlib.sha256((payload_str + "SECRET123").encode("utf-8")).hexdigest()
    
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent")
    
    with pytest.raises(UnverifiedTransactionAbortError, match="Missing attestation token"):
        mutator.process_next_transaction(current_time=1717848000.0)

def test_process_next_transaction_confidence_below_threshold():
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    mutator.active_registry["petitioner_agent"] = "SECRET123"
    mutator.seed_verifier_ledger("Title", "ACTIVE")
    
    # Confidence is 0.98 (below 0.99)
    msg = f"READY_ATTESTATION:HASH123:VERIFIER_KEY"
    sig = hashlib.sha256(msg.encode("utf-8")).hexdigest()
    attestation = {
        "tx_type": "READY_ATTESTATION",
        "timestamp": "2026-06-08T18:00:00Z",
        "tree_hash": "HASH123",
        "signature": sig,
        "confidence": 0.98
    }
    
    payload_dict = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"ast_node": "Title", "content": "Simple text"},
        "attestation_token": attestation
    }
    
    payload_str = json.dumps(payload_dict["payload_data"], sort_keys=True)
    expected_sig = hashlib.sha256((payload_str + "SECRET123").encode("utf-8")).hexdigest()
    
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent")
    
    with pytest.raises(UnverifiedTransactionAbortError, match="Confidence rating value is below 0.99"):
        mutator.process_next_transaction(current_time=1717848000.0)

def test_payload_sanitization_html_tags():
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    mutator.active_registry["petitioner_agent"] = "SECRET123"
    mutator.seed_verifier_ledger("Title", "ACTIVE")
    
    msg = f"READY_ATTESTATION:HASH123:VERIFIER_KEY"
    sig = hashlib.sha256(msg.encode("utf-8")).hexdigest()
    attestation = {
        "tx_type": "READY_ATTESTATION",
        "timestamp": "2026-06-08T18:00:00Z",
        "tree_hash": "HASH123",
        "signature": sig,
        "confidence": 0.995
    }
    
    payload_dict = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"ast_node": "Title", "content": "<b>Bold Text</b>"},
        "attestation_token": attestation
    }
    
    payload_str = json.dumps(payload_dict["payload_data"], sort_keys=True)
    expected_sig = hashlib.sha256((payload_str + "SECRET123").encode("utf-8")).hexdigest()
    
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent")
    
    with pytest.raises(ValueError, match="Embedded HTML or formatting tag characters detected"):
        mutator.process_next_transaction(current_time=1717848000.0)

def test_payload_sanitization_delimiter_mismatch():
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    mutator.active_registry["petitioner_agent"] = "SECRET123"
    mutator.seed_verifier_ledger("Title", "ACTIVE")
    
    msg = f"READY_ATTESTATION:HASH123:VERIFIER_KEY"
    sig = hashlib.sha256(msg.encode("utf-8")).hexdigest()
    attestation = {
        "tx_type": "READY_ATTESTATION",
        "timestamp": "2026-06-08T18:00:00Z",
        "tree_hash": "HASH123",
        "signature": sig,
        "confidence": 0.995
    }
    
    payload_dict = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"ast_node": "Title", "content": "Unbalanced (parenthesis"},
        "attestation_token": attestation
    }
    
    payload_str = json.dumps(payload_dict["payload_data"], sort_keys=True)
    expected_sig = hashlib.sha256((payload_str + "SECRET123").encode("utf-8")).hexdigest()
    
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent")
    
    with pytest.raises(ValueError, match="Unbalanced opening delimiter detected"):
        mutator.process_next_transaction(current_time=1717848000.0)

def test_payload_sanitization_markdown_escaping():
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    mutator.active_registry["petitioner_agent"] = "SECRET123"
    mutator.seed_verifier_ledger("Title", "ACTIVE")
    
    msg = f"READY_ATTESTATION:HASH123:VERIFIER_KEY"
    sig = hashlib.sha256(msg.encode("utf-8")).hexdigest()
    attestation = {
        "tx_type": "READY_ATTESTATION",
        "timestamp": "2026-06-08T18:00:00Z",
        "tree_hash": "HASH123",
        "signature": sig,
        "confidence": 0.995
    }
    
    payload_dict = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"ast_node": "Title", "content": "*Header* #Heading `code`"},
        "attestation_token": attestation
    }
    
    payload_str = json.dumps(payload_dict["payload_data"], sort_keys=True)
    expected_sig = hashlib.sha256((payload_str + "SECRET123").encode("utf-8")).hexdigest()
    
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent")
    
    processed = mutator.process_next_transaction(current_time=1717848000.0)
    assert processed is not None
    # Markdown control chars should be escaped: *, _, #, `, \
    assert processed.payload_data["content"] == "\\*Header\\* \\#Heading \\`code\\`"

def test_payload_sanitization_recursive_loop_detection():
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    mutator.active_registry["petitioner_agent"] = "SECRET123"
    mutator.seed_verifier_ledger("Title", "ACTIVE")
    
    msg = f"READY_ATTESTATION:HASH123:VERIFIER_KEY"
    sig = hashlib.sha256(msg.encode("utf-8")).hexdigest()
    attestation = {
        "tx_type": "READY_ATTESTATION",
        "timestamp": "2026-06-08T18:00:00Z",
        "tree_hash": "HASH123",
        "signature": sig,
        "confidence": 0.995
    }
    
    # Repetitive pattern of length >= 10 repeating 3 times
    repetitive_text = "abcdefghijabcdefghijabcdefghij"
    
    payload_dict = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"ast_node": "Title", "content": repetitive_text},
        "attestation_token": attestation
    }
    
    payload_str = json.dumps(payload_dict["payload_data"], sort_keys=True)
    expected_sig = hashlib.sha256((payload_str + "SECRET123").encode("utf-8")).hexdigest()
    
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent")
    
    with pytest.raises(ValueError, match="Recursive syntax loop declaration detected"):
        mutator.process_next_transaction(current_time=1717848000.0)


def test_cryptographic_authenticity_audit_duplicate_detection():
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    mutator.active_registry["petitioner_agent"] = "SECRET123"
    mutator.seed_verifier_ledger("Title", "ACTIVE")
    
    msg = f"READY_ATTESTATION:HASH123:VERIFIER_KEY"
    sig = hashlib.sha256(msg.encode("utf-8")).hexdigest()
    attestation = {
        "tx_type": "READY_ATTESTATION",
        "timestamp": "2026-06-08T18:00:00Z",
        "tree_hash": "HASH123",
        "signature": sig,
        "confidence": 0.995
    }
    
    payload_dict = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"ast_node": "Title", "content": "Ok text"},
        "attestation_token": attestation
    }
    
    payload_str = json.dumps(payload_dict["payload_data"], sort_keys=True)
    expected_sig = hashlib.sha256((payload_str + "SECRET123").encode("utf-8")).hexdigest()
    
    # Push and process first time (should succeed)
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent")
    res = mutator.process_next_transaction(current_time=1717848000.0)
    assert res is not None
    
    # Push and process second time with exact same signature (should raise duplicate error)
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent")
    with pytest.raises(UnverifiedTransactionAbortError, match="DUPLICATE_TRANSACTION_DETECTED"):
        mutator.process_next_transaction(current_time=1717848000.0)

def test_cryptographic_authenticity_audit_timestamp_drift():
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY", drift_tolerance_seconds=10)
    mutator.active_registry["petitioner_agent"] = "SECRET123"
    
    payload_dict = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"ast_node": "Title", "content": "Ok text"}
    }
    
    payload_str = json.dumps(payload_dict["payload_data"], sort_keys=True)
    expected_sig = hashlib.sha256((payload_str + "SECRET123").encode("utf-8")).hexdigest()
    
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent")
    
    # System time has drifted to 1717848020.0 (drift of 20 seconds, tolerance is 10)
    with pytest.raises(UnverifiedTransactionAbortError, match="TIMESTAMP_DRIFT_EXCEEDED"):
        mutator.process_next_transaction(current_time=1717848020.0)

def test_cryptographic_authenticity_audit_certificate_integrity():
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    mutator.active_registry["petitioner_agent"] = "SECRET123"
    
    payload_dict = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"ast_node": "Title", "content": "Ok text"}
    }
    
    payload_str = json.dumps(payload_dict["payload_data"], sort_keys=True)
    expected_sig = hashlib.sha256((payload_str + "SECRET123").encode("utf-8")).hexdigest()
    
    # 1. Invalid certificate (not in registry)
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent", certificate="BAD_CERT")
    with pytest.raises(UnverifiedTransactionAbortError, match="Invalid signature certificate integrity"):
        mutator.process_next_transaction(current_time=1717848000.0)
        
    # 2. Inactive certificate
    mutator.active_certificates["REVOKED_CERT"] = "revoked"
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent", certificate="REVOKED_CERT")
    with pytest.raises(UnverifiedTransactionAbortError, match="Invalid signature certificate integrity"):
        mutator.process_next_transaction(current_time=1717848000.0)

def test_cryptographic_authenticity_audit_authority_filter():
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    mutator.active_registry["reviewer_agent"] = "SECRET123"
    
    # reviewer_agent has authority level 1, which is below minimum of 2
    payload_dict = {
        "sender_id": "reviewer_agent",
        "role": "reviewer_agent",
        "timestamp": 1717848000.0,
        "payload_data": {"ast_node": "Title", "content": "Ok text"}
    }
    
    payload_str = json.dumps(payload_dict["payload_data"], sort_keys=True)
    expected_sig = hashlib.sha256((payload_str + "SECRET123").encode("utf-8")).hexdigest()
    
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="reviewer_agent")
    
    with pytest.raises(UnverifiedTransactionAbortError, match="Authority level is insufficient"):
        mutator.process_next_transaction(current_time=1717848000.0)

def test_cryptographic_authenticity_audit_reports():
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    mutator.active_registry["petitioner_agent"] = "SECRET123"
    mutator.seed_verifier_ledger("Title", "ACTIVE")
    
    msg = f"READY_ATTESTATION:HASH123:VERIFIER_KEY"
    sig = hashlib.sha256(msg.encode("utf-8")).hexdigest()
    attestation = {
        "tx_type": "READY_ATTESTATION",
        "timestamp": "2026-06-08T18:00:00Z",
        "tree_hash": "HASH123",
        "signature": sig,
        "confidence": 0.995
    }
    
    payload_dict = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"ast_node": "Title", "content": "Ok text"},
        "attestation_token": attestation
    }
    
    payload_str = json.dumps(payload_dict["payload_data"], sort_keys=True)
    expected_sig = hashlib.sha256((payload_str + "SECRET123").encode("utf-8")).hexdigest()
    
    # 1. Successful verification
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent")
    mutator.process_next_transaction(current_time=1717848000.0)
    
    # 2. Failure due to signature mismatch
    queue.push_transaction(payload_dict, signature="BAD_SIG", sender_id="petitioner_agent")
    with pytest.raises(UnverifiedTransactionAbortError):
        mutator.process_next_transaction(current_time=1717848000.0)
        
    report = mutator.generate_crypto_audit_report()
    assert report["report_type"] == "CRYPTOGRAPHIC_AUDIT_REPORT"
    assert report["success_count"] == 1
    assert report["failure_count"] == 1
    assert len(report["logs"]) == 2

def test_verification_token_gating_report():
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    mutator.active_registry["petitioner_agent"] = "SECRET123"
    mutator.seed_verifier_ledger("Title", "ACTIVE")
    
    msg = f"READY_ATTESTATION:HASH123:VERIFIER_KEY"
    sig = hashlib.sha256(msg.encode("utf-8")).hexdigest()
    attestation = {
        "tx_type": "READY_ATTESTATION",
        "timestamp": "2026-06-08T18:00:00Z",
        "tree_hash": "HASH123",
        "signature": sig,
        "confidence": 0.995
    }
    
    payload_dict = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"ast_node": "Title", "content": "Ok text"},
        "attestation_token": attestation
    }
    
    payload_str = json.dumps(payload_dict["payload_data"], sort_keys=True)
    expected_sig = hashlib.sha256((payload_str + "SECRET123").encode("utf-8")).hexdigest()
    
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent")
    mutator.process_next_transaction(current_time=1717848010.0)
    
    report = mutator.generate_gate_status_report()
    assert report["report_type"] == "GATE_STATUS_REPORT"
    assert report["total_processed"] == 1
    assert report["average_passage_duration_seconds"] == 10.0
    assert report["gate_passage_durations"] == [10.0]


def test_verification_token_gating_failures():
    # 1. Missing node ID
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    mutator.active_registry["petitioner_agent"] = "SECRET123"
    
    msg = f"READY_ATTESTATION:HASH123:VERIFIER_KEY"
    sig = hashlib.sha256(msg.encode("utf-8")).hexdigest()
    attestation = {
        "tx_type": "READY_ATTESTATION",
        "timestamp": "2026-06-08T18:00:00Z",
        "tree_hash": "HASH123",
        "signature": sig,
        "confidence": 0.995
    }
    
    payload_dict = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"content": "Ok text"},
        "attestation_token": attestation
    }
    
    payload_str = json.dumps(payload_dict["payload_data"], sort_keys=True)
    expected_sig = hashlib.sha256((payload_str + "SECRET123").encode("utf-8")).hexdigest()
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent")
    with pytest.raises(UnverifiedTransactionAbortError, match="Node ID parameter is missing"):
        mutator.process_next_transaction(current_time=1717848000.0)

    # 2. Missing ledger record
    payload_dict["payload_data"]["node_id"] = "N_1"
    payload_str = json.dumps(payload_dict["payload_data"], sort_keys=True)
    expected_sig = hashlib.sha256((payload_str + "SECRET123").encode("utf-8")).hexdigest()
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    mutator.active_registry["petitioner_agent"] = "SECRET123"
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent")
    with pytest.raises(UnverifiedTransactionAbortError, match="No Verifier Agent ledger records found"):
        mutator.process_next_transaction(current_time=1717848000.0)

    # 3. Token status not ACTIVE
    mutator.seed_verifier_ledger("N_1", "REVOKED")
    queue = DrafterTransactionQueue()
    mutator.queue = queue
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent")
    with pytest.raises(UnverifiedTransactionAbortError, match="Verification token status.*expected ACTIVE"):
        mutator.process_next_transaction(current_time=1717848000.0)

    # 4. Token node ID mismatch
    mutator.seed_verifier_ledger("N_1", "ACTIVE")
    mutator.seed_verifier_ledger("N_2", "ACTIVE")
    msg = f"READY_ATTESTATION:HASH123:VERIFIER_KEY:N_2"
    sig = hashlib.sha256(msg.encode("utf-8")).hexdigest()
    attestation_mismatch = {
        "tx_type": "READY_ATTESTATION",
        "timestamp": "2026-06-08T18:00:00Z",
        "tree_hash": "HASH123",
        "signature": sig,
        "confidence": 0.995,
        "node_id": "N_2"
    }
    payload_dict["attestation_token"] = attestation_mismatch
    payload_str = json.dumps(payload_dict["payload_data"], sort_keys=True)
    expected_sig = hashlib.sha256((payload_str + "SECRET123").encode("utf-8")).hexdigest()
    queue = DrafterTransactionQueue()
    mutator.queue = queue
    queue.push_transaction(payload_dict, signature=expected_sig, sender_id="petitioner_agent")
    with pytest.raises(UnverifiedTransactionAbortError, match="Token node ID.*does not match transaction node ID"):
        mutator.process_next_transaction(current_time=1717848000.0)


def test_filter_unverified_transaction_blocks():
    queue = DrafterTransactionQueue()
    mutator = DrafterMutator(queue, verifier_public_key="VERIFIER_KEY")
    mutator.active_registry["petitioner_agent"] = "SECRET123"
    
    # 1. Valid verified transaction
    msg1 = f"READY_ATTESTATION:HASH123:VERIFIER_KEY"
    sig1 = hashlib.sha256(msg1.encode("utf-8")).hexdigest()
    attestation1 = {
        "tx_type": "READY_ATTESTATION",
        "timestamp": "2026-06-08T18:00:00Z",
        "tree_hash": "HASH123",
        "signature": sig1,
        "confidence": 0.995
    }
    payload_dict1 = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"ast_node": "N_OK", "content": "Ok text"},
        "attestation_token": attestation1
    }
    payload_str1 = json.dumps(payload_dict1["payload_data"], sort_keys=True)
    expected_sig1 = hashlib.sha256((payload_str1 + "SECRET123").encode("utf-8")).hexdigest()
    env1 = queue.push_transaction(payload_dict1, signature=expected_sig1, sender_id="petitioner_agent")
    
    # 2. Unverified (no ledger record) transaction
    payload_dict2 = {
        "sender_id": "petitioner_agent",
        "role": "petitioner",
        "timestamp": 1717848000.0,
        "payload_data": {"ast_node": "N_BAD", "content": "Bad text"},
        "attestation_token": attestation1
    }
    payload_str2 = json.dumps(payload_dict2["payload_data"], sort_keys=True)
    expected_sig2 = hashlib.sha256((payload_str2 + "SECRET123").encode("utf-8")).hexdigest()
    env2 = queue.push_transaction(payload_dict2, signature=expected_sig2, sender_id="petitioner_agent")
    
    # Seed only N_OK
    mutator.seed_verifier_ledger("N_OK", "ACTIVE")
    
    envelopes = [env1, env2]
    filtered = mutator.filter_unverified_transaction_blocks(envelopes)
    assert len(filtered) == 1
    assert filtered[0].payload.payload_data["ast_node"] == "N_OK"
