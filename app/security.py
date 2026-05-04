from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

from app.config import AppConfig


def verify_basic_auth(credentials: HTTPBasicCredentials, username: str, password: str) -> bool:
    is_correct_username = secrets.compare_digest(credentials.username, username)
    is_correct_password = secrets.compare_digest(credentials.password, password)
    return is_correct_username and is_correct_password


def create_auth_dependency(config: AppConfig):
    security = HTTPBasic()

    def dependency(credentials: HTTPBasicCredentials = Depends(security)):
        if not verify_basic_auth(credentials, config.basic_auth_user, config.basic_auth_password):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        return credentials

    return dependency
