"""
Northgate Enterprise Agent - Security & Auth Module
Implements API-based Authentication & Role-Based Authorization with HTTP Headers.
Frontend NEVER speaks directly to LLM providers; all requests go through this gate.
"""
from fastapi import Header, HTTPException, status, Depends
from typing import Optional, List
from pydantic import BaseModel
from .config import config

class AuthUser(BaseModel):
    user_id: str
    username: str
    full_name: str
    role: str
    department: str
    client_name: str
    api_key: str

def get_current_authenticated_user(
    authorization: Optional[str] = Header(None, description="Bearer Token for User Session"),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key", description="API Key for Frontend/Client Application")
) -> AuthUser:
    """
    Validates both:
    1. X-API-Key (Application authorization)
    2. Authorization: Bearer <token> (User session authentication)
    """
    # 1. Check API Key
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Security Violation: Missing required 'X-API-Key' header in request."
        )

    client_info = config.API_KEYS.get(x_api_key)
    if not client_info:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Security Violation: Invalid or revoked 'X-API-Key'."
        )

    # 2. Check Bearer Token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Security Violation: Missing or invalid 'Authorization: Bearer <token>' header."
        )

    token = authorization.split("Bearer ", 1)[1].strip()
    user_info = config.AUTH_TOKENS.get(token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Security Violation: Expired or unrecognized user session token."
        )

    # 3. Check if user's role is permitted by this client API key
    if user_info["role"] not in client_info["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Security Violation: Role '{user_info['role']}' is not authorized for client '{client_info['client_name']}'."
        )

    return AuthUser(
        user_id=user_info["user_id"],
        username=user_info["username"],
        full_name=user_info["full_name"],
        role=user_info["role"],
        department=user_info["department"],
        client_name=client_info["client_name"],
        api_key=x_api_key
    )

class RequireRoles:
    """Dependency for Role-Based Access Control (RBAC)"""
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: AuthUser = Depends(get_current_authenticated_user)) -> AuthUser:
        if current_user.role not in self.allowed_roles and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: Role '{current_user.role}' lacks permission. Required roles: {self.allowed_roles}"
            )
        return current_user
