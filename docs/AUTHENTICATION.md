# Authentication & Session Management

**Projekt**: Grekonto AI Automatizáció  
**Verzió**: 1.0
**Utolsó frissítés**: 2025-11-23
**Commit**: TBD (frissítés után)

## Overview

This document describes the OAuth 2.0 authentication and session management system for Grekonto.

### Architecture

```
Frontend (Azure AD)
    ↓
API Gateway
    ↓
Authentication Middleware
    ↓
OAuth Token Manager
    ↓
Redis Session Store
    ↓
Protected Endpoints
```

## Components

### 1. OAuth Token Manager (`oauth_token_manager.py`)

Manages JWT tokens with automatic refresh and validation.

**Features:**
- JWT token creation with custom claims
- Token validation with expiration checking
- Automatic token refresh
- Token revocation support
- Expiration threshold checking

**Usage:**
```python
from backend.shared.oauth_token_manager import OAuthTokenManager

manager = OAuthTokenManager()
token = manager.create_token("user123", ["read", "write"])
is_valid, payload = manager.validate_token(token)
new_token = manager.refresh_token(token)
```

### 2. Redis Session Store (`redis_session_store.py`)

Persistent session storage with automatic fallback to memory.

**Features:**
- Redis-backed session persistence
- Automatic TTL management
- Token refresh capability
- Health checks
- Development mode with in-memory fallback

**Usage:**
```python
from backend.shared.redis_session_store import RedisSessionStore

store = RedisSessionStore()
session_id = store.create_session("user123", {"token": "..."})
session = store.get_session(session_id)
store.refresh_token(session_id, new_token_data)
```

### 3. Authentication Middleware (`auth_middleware.py`)

Decorator-based authentication for Azure Functions.

**Features:**
- Bearer token extraction
- Scope validation
- Automatic token refresh
- User context injection

**Usage:**
```python
from backend.shared.auth_middleware import require_auth

@require_auth(required_scopes=["read"])
def main(req: func.HttpRequest) -> func.HttpResponse:
    user_id = req.user_id
    scopes = req.scopes
    ...
```

### 4. Security Utilities (`security_utils.py`)

Rate limiting, CSRF protection, and input validation.

**Features:**
- Rate limiting per user/IP
- CSRF token generation
- Security headers
- Password validation
- Input sanitization

## API Endpoints

### POST /api/authenticate

Generate a new authentication token.

**Request:**
```json
{
  "action": "authenticate",
  "user_id": "user@example.com",
  "scopes": ["read", "write"]
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "session_id": "abc123...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### POST /api/authenticate (refresh)

Refresh an existing token.

**Request:**
```json
{
  "action": "refresh",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### POST /api/authenticate (validate)

Validate a token.

**Request:**
```json
{
  "action": "validate",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Configuration

### Environment Variables

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
JWT_SECRET=your-secret-key-here

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

## Security Best Practices

1. **Token Storage**: Store tokens in secure, httpOnly cookies
2. **HTTPS Only**: Always use HTTPS in production
3. **Token Rotation**: Implement automatic token refresh
4. **Scope Validation**: Always validate required scopes
5. **Rate Limiting**: Protect endpoints from brute force
6. **Input Validation**: Sanitize all user inputs
7. **CSRF Protection**: Use CSRF tokens for state-changing operations

## Troubleshooting

### Redis Connection Failed

If Redis is unavailable, the system falls back to in-memory storage. This is suitable for development but NOT for production.

**Solution**: Ensure Redis is running and accessible.

### Token Validation Failed

Check that:
1. Token is not expired
2. Token is not revoked
3. JWT_SECRET matches the one used to create the token

### Rate Limit Exceeded

Wait for the rate limit window to reset or increase the limit in configuration.

---

## DOKUMENTÁCIÓ VERZIÓ ÉS FRISSÍTÉSI TÖRTÉNET

**Verzió:** 1.0
**Utolsó frissítés:** 2025-11-23
**Commit:** d11b0776

### Frissítési Történet
* **v1.0** (2025-11-23): Eredeti verzió - OAuth 2.0 és session management dokumentálva

