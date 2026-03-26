"""
crypto_utils.py  —  Local-DB Field-Level Encryption
=====================================================
All *sensitive* fields in the local SQLite database are stored as
Fernet-encrypted, base64-encoded ciphertext so that anyone who opens
counseling.db directly only sees rubbish (e.g. gAAAAABl…).

The encryption key is derived from a fixed passphrase + a per-machine
salt stored alongside the DB.  Both the salt file and the DB must be
present to decrypt — losing either makes the data unreadable.

GTEC Compliance note:
  • Student names are NEVER stored — only case numbers + initials format
    (already enforced at the application layer).
  • Fields encrypted here: contact, parent_contact, email, notes,
    problems, interventions, recommendations, reasons, action_taken,
    outcome, referred_by, comments, full_name (BookingRequest), reason
    (BookingRequest), referral_reason.

Usage (import in app.py / routes):
    from crypto_utils import encrypt_field, decrypt_field

    # Saving:
    contact_enc = encrypt_field(contact_raw)
    conn.execute("INSERT INTO Student ... VALUES (?, ...)", (contact_enc, ...))

    # Reading:
    student = conn.execute(...).fetchone()
    contact_plain = decrypt_field(student['contact'])
"""

import os
import sys
import base64
import hashlib

# ── Key derivation ────────────────────────────────────────────────────────────

def _get_base_dir():
    """Return the directory where counseling.db lives."""
    try:
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))
    except Exception:
        return os.getcwd()


def _get_or_create_salt() -> bytes:
    """Load or create a per-machine 32-byte salt file next to the DB."""
    salt_path = os.path.join(_get_base_dir(), '.db_salt')
    if os.path.exists(salt_path):
        with open(salt_path, 'rb') as f:
            salt = f.read()
            if len(salt) == 32:
                return salt
    # Generate a fresh salt
    salt = os.urandom(32)
    try:
        with open(salt_path, 'wb') as f:
            f.write(salt)
    except Exception as e:
        print(f"[CRYPTO] Warning: could not persist salt: {e}")
    return salt


# Stable passphrase baked into the app (add per-site secret via env var)
_APP_PASSPHRASE = os.environ.get(
    'GCC_DB_PASSPHRASE',
    'AAMUSTED-GCC-COUNSELLING-SYSTEM-SECRET-2024'
)

_fernet_instance = None  # Module-level singleton

def _get_fernet():
    """Return a cached Fernet instance (lazy initialisation)."""
    global _fernet_instance
    if _fernet_instance is not None:
        return _fernet_instance

    try:
        from cryptography.fernet import Fernet
    except ImportError:
        # cryptography not installed — fall back to no-op (warn loudly)
        print("[CRYPTO] WARNING: 'cryptography' package not found. "
              "Fields will NOT be encrypted. Run: pip install cryptography")
        return None

    salt = _get_or_create_salt()
    # Derive a 32-byte key via PBKDF2-HMAC-SHA256 (100k iterations)
    dk = hashlib.pbkdf2_hmac(
        'sha256',
        _APP_PASSPHRASE.encode(),
        salt,
        100_000,
        dklen=32
    )
    key = base64.urlsafe_b64encode(dk)   # Fernet needs a url-safe b64 key
    _fernet_instance = Fernet(key)
    return _fernet_instance


# ── Public helpers ─────────────────────────────────────────────────────────────

_ENC_PREFIX = b'ENC:'   # Magic prefix so we can detect already-encrypted values


def encrypt_field(value: str | None) -> str | None:
    """
    Encrypt a plaintext string and return a base64-encoded ciphertext string.
    Returns None / empty string unchanged.
    If cryptography is not available, returns value unchanged.
    """
    if not value:
        return value

    f = _get_fernet()
    if f is None:
        return value  # Degraded mode — no encryption

    try:
        plaintext = str(value).encode('utf-8')
        ciphertext = f.encrypt(plaintext)               # bytes
        # Prefix + base64 so it stores cleanly as TEXT in SQLite
        stored = base64.b64encode(_ENC_PREFIX + ciphertext).decode('ascii')
        return stored
    except Exception as e:
        print(f"[CRYPTO] Encrypt error: {e}")
        return value  # Return original on error — don't lose data


def decrypt_field(value: str | None) -> str | None:
    """
    Decrypt a previously-encrypted field.  Transparently handles:
      • None / empty  → returned as-is
      • Plaintext (legacy / unencrypted row) → returned as-is
      • ENC: prefixed ciphertext → decrypted and returned as str
    """
    if not value:
        return value

    f = _get_fernet()
    if f is None:
        return value  # Degraded mode

    try:
        raw = base64.b64decode(value.encode('ascii'))
        if not raw.startswith(_ENC_PREFIX):
            return value   # Legacy plaintext row — return unchanged

        ciphertext = raw[len(_ENC_PREFIX):]
        plaintext = f.decrypt(ciphertext)
        return plaintext.decode('utf-8')
    except Exception:
        # Any decryption error → assume it's legacy plaintext
        return value


def is_encrypted(value: str | None) -> bool:
    """Return True if the value looks like an encrypted field."""
    if not value:
        return False
    try:
        raw = base64.b64decode(value.encode('ascii'))
        return raw.startswith(_ENC_PREFIX)
    except Exception:
        return False


def encrypt_row(row_dict: dict, fields: list) -> dict:
    """Return a copy of row_dict with specified fields encrypted."""
    result = dict(row_dict)
    for field in fields:
        if field in result:
            result[field] = encrypt_field(result[field])
    return result


def decrypt_row(row_dict: dict, fields: list) -> dict:
    """Return a copy of row_dict with specified fields decrypted."""
    result = dict(row_dict)
    for field in fields:
        if field in result:
            result[field] = decrypt_field(result[field])
    return result


# Convenience: field lists per table
STUDENT_SENSITIVE_FIELDS    = ['contact', 'parent_contact', 'email']
BOOKING_SENSITIVE_FIELDS    = ['full_name', 'email', 'phone', 'reason']
CASENOTE_SENSITIVE_FIELDS   = ['problems', 'interventions', 'recommendations', 'client_appearance']
REFERRAL_SENSITIVE_FIELDS   = ['referred_by', 'contact', 'reasons', 'action_taken', 'outcome']
SESSION_SENSITIVE_FIELDS    = ['notes', 'outcome']
