import secrets


def verify_password(plain: str, expected: str) -> bool:
    return secrets.compare_digest(plain.encode(), expected.encode())
