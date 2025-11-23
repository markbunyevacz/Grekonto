"""
Authentication middleware for Azure Functions.

Provides decorators and utilities for protecting API endpoints with OAuth 2.0.
"""

import logging
import functools
from typing import Callable, Optional, Dict, Any
import azure.functions as func
from .oauth_token_manager import OAuthTokenManager
from .redis_session_store import RedisSessionStore

logger = logging.getLogger(__name__)

# Global instances
token_manager = OAuthTokenManager()
session_store = RedisSessionStore()


def require_auth(required_scopes: Optional[list] = None) -> Callable:
    """
    Decorator to require authentication on Azure Function endpoints.
    
    Args:
        required_scopes: List of required OAuth scopes
        
    Returns:
        Decorated function
    """
    def decorator(func_handler: Callable) -> Callable:
        @functools.wraps(func_handler)
        def wrapper(req: func.HttpRequest) -> func.HttpResponse:
            # Extract token from Authorization header
            auth_header = req.headers.get("Authorization", "")
            
            if not auth_header.startswith("Bearer "):
                logger.warning("Missing or invalid Authorization header")
                return func.HttpResponse(
                    '{"error": "Missing or invalid Authorization header"}',
                    status_code=401,
                    mimetype="application/json"
                )
            
            token = auth_header[7:]  # Remove "Bearer " prefix
            
            # Validate token
            is_valid, payload = token_manager.validate_token(token)
            
            if not is_valid:
                logger.warning("Token validation failed")
                return func.HttpResponse(
                    '{"error": "Invalid or expired token"}',
                    status_code=401,
                    mimetype="application/json"
                )
            
            # Check scopes if required
            if required_scopes:
                user_scopes = payload.get("scopes", [])
                if not any(scope in user_scopes for scope in required_scopes):
                    logger.warning(f"Insufficient scopes: {user_scopes}")
                    return func.HttpResponse(
                        '{"error": "Insufficient permissions"}',
                        status_code=403,
                        mimetype="application/json"
                    )
            
            # Check if token is expiring soon and refresh if needed
            if token_manager.is_token_expiring_soon(token):
                new_token = token_manager.refresh_token(token)
                if new_token:
                    # Store new token in response header
                    req.headers["X-New-Token"] = new_token
            
            # Add user context to request
            req.user_id = payload.get("user_id")
            req.scopes = payload.get("scopes", [])
            req.token_payload = payload
            
            return func_handler(req)
        
        return wrapper
    return decorator


def extract_token(req: func.HttpRequest) -> Optional[str]:
    """Extract JWT token from request."""
    auth_header = req.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


def get_user_context(req: func.HttpRequest) -> Optional[Dict[str, Any]]:
    """Get authenticated user context from request."""
    return {
        "user_id": getattr(req, "user_id", None),
        "scopes": getattr(req, "scopes", []),
        "token_payload": getattr(req, "token_payload", {})
    }

