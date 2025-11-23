"""
Authentication API endpoint for token generation and validation.

POST /api/authenticate - Generate token
POST /api/authenticate/refresh - Refresh token
POST /api/authenticate/validate - Validate token
"""

import azure.functions as func
import json
import logging
from ..shared.oauth_token_manager import OAuthTokenManager
from ..shared.redis_session_store import RedisSessionStore
from ..shared.security_utils import RateLimiter, InputValidator

logger = logging.getLogger(__name__)

token_manager = OAuthTokenManager()
session_store = RedisSessionStore()
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Handle authentication requests."""
    
    # Rate limiting
    client_ip = req.headers.get("X-Forwarded-For", "unknown")
    is_allowed, rate_info = rate_limiter.is_allowed(client_ip)
    
    if not is_allowed:
        return func.HttpResponse(
            json.dumps({
                "error": "Rate limit exceeded",
                "rate_limit": rate_info
            }),
            status_code=429,
            mimetype="application/json"
        )
    
    try:
        if req.method == "POST":
            body = req.get_json()
            action = body.get("action", "authenticate")
            
            if action == "authenticate":
                return _handle_authenticate(body)
            elif action == "refresh":
                return _handle_refresh(body)
            elif action == "validate":
                return _handle_validate(body)
            else:
                return func.HttpResponse(
                    json.dumps({"error": "Unknown action"}),
                    status_code=400,
                    mimetype="application/json"
                )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )
    
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )


def _handle_authenticate(body: dict) -> func.HttpResponse:
    """Handle token generation."""
    user_id = body.get("user_id")
    scopes = body.get("scopes", ["read"])
    
    if not user_id:
        return func.HttpResponse(
            json.dumps({"error": "user_id is required"}),
            status_code=400,
            mimetype="application/json"
        )
    
    # Sanitize input
    user_id = InputValidator.sanitize_string(user_id, max_length=100)
    
    # Create token
    token = token_manager.create_token(user_id, scopes)
    
    # Create session
    session_id = session_store.create_session(
        user_id,
        {"access_token": token, "scopes": scopes}
    )
    
    return func.HttpResponse(
        json.dumps({
            "access_token": token,
            "session_id": session_id,
            "token_type": "Bearer",
            "expires_in": 3600
        }),
        status_code=200,
        mimetype="application/json"
    )


def _handle_refresh(body: dict) -> func.HttpResponse:
    """Handle token refresh."""
    token = body.get("token")
    
    if not token:
        return func.HttpResponse(
            json.dumps({"error": "token is required"}),
            status_code=400,
            mimetype="application/json"
        )
    
    new_token = token_manager.refresh_token(token)
    
    if not new_token:
        return func.HttpResponse(
            json.dumps({"error": "Token refresh failed"}),
            status_code=401,
            mimetype="application/json"
        )
    
    return func.HttpResponse(
        json.dumps({
            "access_token": new_token,
            "token_type": "Bearer",
            "expires_in": 3600
        }),
        status_code=200,
        mimetype="application/json"
    )


def _handle_validate(body: dict) -> func.HttpResponse:
    """Handle token validation."""
    token = body.get("token")
    
    if not token:
        return func.HttpResponse(
            json.dumps({"error": "token is required"}),
            status_code=400,
            mimetype="application/json"
        )
    
    is_valid, payload = token_manager.validate_token(token)
    
    return func.HttpResponse(
        json.dumps({
            "valid": is_valid,
            "payload": payload if is_valid else None
        }),
        status_code=200,
        mimetype="application/json"
    )

