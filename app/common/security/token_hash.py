import hashlib


def hash_token(token: str) -> str:
    """Genera un SHA-256 del token. Se almacena en BD en lugar del token raw."""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(token: str, token_hash: str) -> bool:
    """Verifica que el token coincide con su hash almacenado."""
    return hashlib.sha256(token.encode()).hexdigest() == token_hash
