"""
TDS Core - Hashing Utilities
Content hashing for deduplication and idempotency key generation
"""
import hashlib
import json
from typing import Any, Dict
from datetime import datetime


def generate_content_hash(data: Dict[str, Any], exclude_fields: list = None) -> str:
    """
    Generate SHA256 hash of data for deduplication

    Args:
        data: Dictionary to hash
        exclude_fields: List of field names to exclude from hash (e.g., timestamps)

    Returns:
        SHA256 hash string

    Example:
        >>> data = {"id": "123", "name": "Product", "updated_at": "2025-10-31"}
        >>> hash1 = generate_content_hash(data, exclude_fields=["updated_at"])
        >>> # Same data with different timestamp produces same hash
        >>> data2 = {"id": "123", "name": "Product", "updated_at": "2025-11-01"}
        >>> hash2 = generate_content_hash(data2, exclude_fields=["updated_at"])
        >>> assert hash1 == hash2
    """
    exclude_fields = exclude_fields or ['updated_at', 'modified_at', 'last_modified']

    # Create a copy to avoid modifying original
    data_copy = data.copy()

    # Remove excluded fields
    for field in exclude_fields:
        data_copy.pop(field, None)

    # Sort keys for consistent hashing
    serialized = json.dumps(data_copy, sort_keys=True, default=str)

    # Generate SHA256 hash
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()


def generate_idempotency_key(
    source_type: str,
    entity_type: str,
    entity_id: str,
    operation: str = None
) -> str:
    """
    Generate unique idempotency key for webhook/event

    Args:
        source_type: Source system (e.g., "zoho")
        entity_type: Entity type (e.g., "product")
        entity_id: Source entity ID
        operation: Optional operation type (e.g., "create", "update")

    Returns:
        Idempotency key string

    Example:
        >>> key = generate_idempotency_key("zoho", "product", "123456", "update")
        >>> # Returns: "zoho:product:123456:update"
    """
    parts = [source_type, entity_type, entity_id]
    if operation:
        parts.append(operation)

    return ":".join(parts)


def generate_event_fingerprint(
    source_type: str,
    entity_type: str,
    entity_id: str,
    content_hash: str
) -> str:
    """
    Generate unique fingerprint combining idempotency key + content hash
    Used to detect exact duplicate events

    Args:
        source_type: Source system
        entity_type: Entity type
        entity_id: Source entity ID
        content_hash: Content hash from generate_content_hash()

    Returns:
        Event fingerprint string
    """
    idempotency = generate_idempotency_key(source_type, entity_type, entity_id)
    fingerprint_data = f"{idempotency}:{content_hash}"
    return hashlib.sha256(fingerprint_data.encode('utf-8')).hexdigest()


def verify_webhook_signature(
    payload: str,
    signature: str,
    secret: str,
    algorithm: str = "sha256"
) -> bool:
    """
    Verify webhook signature for authentication

    Args:
        payload: Raw webhook payload string
        signature: Signature from webhook header
        secret: Shared secret key
        algorithm: Hash algorithm (default: sha256)

    Returns:
        True if signature is valid

    Example:
        >>> payload = '{"id": "123", "name": "Product"}'
        >>> secret = "my_webhook_secret"
        >>> # Generate signature
        >>> expected = hashlib.sha256((payload + secret).encode()).hexdigest()
        >>> # Verify
        >>> is_valid = verify_webhook_signature(payload, expected, secret)
        >>> assert is_valid is True
    """
    if algorithm == "sha256":
        expected = hashlib.sha256((payload + secret).encode('utf-8')).hexdigest()
    elif algorithm == "sha1":
        expected = hashlib.sha1((payload + secret).encode('utf-8')).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(signature, expected)


def hash_sensitive_data(data: str) -> str:
    """
    One-way hash for sensitive data (passwords, tokens, etc.)
    Uses SHA256 for irreversible hashing

    Args:
        data: Sensitive string to hash

    Returns:
        SHA256 hash

    Note:
        Do NOT use for passwords - use bcrypt/argon2 instead
        This is for masking sensitive data in logs
    """
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


# Import hmac for signature verification
import hmac
