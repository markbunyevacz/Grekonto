# Authentication Implementation Guide

**Projekt**: Grekonto AI Automatizáció  
**Verzió**: 1.0
**Utolsó frissítés**: 2025-11-23
**Commit**: TBD (frissítés után)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 2. Configure Environment

Create `.env` file in backend directory:

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
JWT_SECRET=your-super-secret-key-change-in-production

# Azure Configuration
KEY_VAULT_NAME=your-keyvault-name
DOCUMENT_INTELLIGENCE_ENDPOINT=https://...
DOCUMENT_INTELLIGENCE_KEY=...
```

### 3. Start Redis (Development)

```bash
# Using Docker
docker run -d -p 6379:6379 redis:latest

# Or install locally
redis-server
```

### 4. Run Tests

```bash
cd backend
python -m unittest tests.test_authentication -v
```

## Integration Examples

### Protecting an Endpoint

```python
import azure.functions as func
from shared.auth_middleware import require_auth

@require_auth(required_scopes=["read"])
def main(req: func.HttpRequest) -> func.HttpResponse:
    user_id = req.user_id
    scopes = req.scopes
    
    # Your endpoint logic here
    return func.HttpResponse(
        json.dumps({"user": user_id}),
        status_code=200,
        mimetype="application/json"
    )
```

### Generating Tokens

```python
from shared.oauth_token_manager import OAuthTokenManager

manager = OAuthTokenManager()
token = manager.create_token(
    user_id="user@example.com",
    scopes=["read", "write"],
    expires_in_seconds=3600
)
```

### Managing Sessions

```python
from shared.redis_session_store import RedisSessionStore

store = RedisSessionStore()
session_id = store.create_session(
    user_id="user@example.com",
    token_data={"access_token": token}
)
```

### Rate Limiting

```python
from shared.security_utils import RateLimiter

limiter = RateLimiter(max_requests=100, window_seconds=60)
is_allowed, rate_info = limiter.is_allowed("user@example.com")

if not is_allowed:
    return func.HttpResponse(
        json.dumps({"error": "Rate limit exceeded"}),
        status_code=429
    )
```

## API Usage

### Generate Token

```bash
curl -X POST http://localhost:7071/api/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "action": "authenticate",
    "user_id": "user@example.com",
    "scopes": ["read", "write"]
  }'
```

### Refresh Token

```bash
curl -X POST http://localhost:7071/api/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "action": "refresh",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

### Validate Token

```bash
curl -X POST http://localhost:7071/api/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "action": "validate",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

### Use Protected Endpoint

```bash
curl -X GET http://localhost:7071/api/tasks \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

## Deployment Checklist

- [ ] Redis configured and running
- [ ] JWT_SECRET set to strong random value
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Audit logging enabled
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Token rotation policy implemented
- [ ] Monitoring and alerting set up
- [ ] Incident response plan documented

## Troubleshooting

### Redis Connection Error

**Problem**: "Error connecting to localhost:6379"

**Solution**: 
1. Ensure Redis is running: `redis-cli ping`
2. Check REDIS_URL environment variable
3. System will fall back to memory storage (dev only)

### Token Validation Failed

**Problem**: "Invalid or expired token"

**Solution**:
1. Check token hasn't expired
2. Verify JWT_SECRET matches
3. Ensure token format is correct

### Rate Limit Exceeded

**Problem**: "429 Too Many Requests"

**Solution**:
1. Wait for rate limit window to reset
2. Increase RATE_LIMIT_REQUESTS if needed
3. Implement exponential backoff in client

---

## DOKUMENTÁCIÓ VERZIÓ ÉS FRISSÍTÉSI TÖRTÉNET

**Verzió:** 1.0  
**Utolsó frissítés:** 2025-11-23  
**Commit:** TBD (frissítés után)

### Frissítési Történet
* **v1.0** (2025-11-23): Eredeti verzió - Implementation guide és quick start

