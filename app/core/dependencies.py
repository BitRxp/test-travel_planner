from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import verify_password
from app.database import SessionLocal

http_basic = HTTPBasic()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(credentials: HTTPBasicCredentials = Depends(http_basic)) -> str:
    username_ok = verify_password(credentials.username, settings.AUTH_USERNAME)
    password_ok = verify_password(credentials.password, settings.AUTH_PASSWORD)

    if not username_ok or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
