"""
Security & Authentication Layer
JWT authentication + RBAC
"""

import jwt
from datetime import datetime, timedelta
from typing import Dict, Any

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import get_settings

security = HTTPBearer()


# -------------------- JWT MANAGER --------------------

class JWTManager:
    def __init__(self):
        self.settings = get_settings()

    def create_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            hours=self.settings.jwt_expiration_hours
        )
        to_encode.update({"exp": expire})

        return jwt.encode(
            to_encode,
            self.settings.secret_key,
            algorithm=self.settings.jwt_algorithm
        )

    def verify_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.jwt_algorithm]
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )


# -------------------- RBAC MANAGER --------------------

class RBACManager:
    ROLE_PERMISSIONS = {
        "hr": ["hr", "security"],
        "admin": ["hr", "engineering", "finance", "security"],
    }

    @staticmethod
    def allowed_sources(role: str):
        return RBACManager.ROLE_PERMISSIONS.get(role, [])


# -------------------- INSTANCES --------------------

jwt_manager = JWTManager()
rbac_manager = RBACManager()


# -------------------- FASTAPI DEPENDENCY --------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    return jwt_manager.verify_token(token)
