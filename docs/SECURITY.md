# Security Guidelines

**Projekt**: Grekonto AI Automatizáció  
**Verzió**: 1.0
**Utolsó frissítés**: 2025-11-23
**Commit**: TBD (frissítés után)

## Security Architecture

### Defense in Depth

```
Layer 1: Network Security (HTTPS, TLS)
    ↓
Layer 2: Authentication (OAuth 2.0, JWT)
    ↓
Layer 3: Authorization (Scope-based)
    ↓
Layer 4: Input Validation (Sanitization)
    ↓
Layer 5: Rate Limiting (DDoS Protection)
    ↓
Layer 6: Audit Logging (Compliance)
```

## Authentication Security

### OAuth 2.0 Implementation

- **Token Type**: JWT (JSON Web Tokens)
- **Algorithm**: HS256 (HMAC SHA-256)
- **Expiration**: 1 hour (configurable)
- **Refresh**: Automatic before expiration
- **Revocation**: Supported via token blacklist

### Token Lifecycle

```
1. User authenticates via Azure AD
2. Backend generates JWT token
3. Token stored in Redis session
4. Client includes token in Authorization header
5. Middleware validates token on each request
6. Token automatically refreshed if expiring soon
7. Token revoked on logout
```

## Session Management

### Redis Session Store

**Features:**
- Persistent session storage
- Automatic TTL management
- Token refresh capability
- Health monitoring
- Development fallback to memory

**Security Considerations:**
- Redis should be in private network
- Use Redis AUTH for password protection
- Enable TLS for Redis connections
- Regular backup of session data

## API Security

### Rate Limiting

Protects against:
- Brute force attacks
- DDoS attacks
- Resource exhaustion

**Configuration:**
- 100 requests per 60 seconds per user
- Configurable per endpoint
- Returns 429 Too Many Requests

### CSRF Protection

- CSRF tokens for state-changing operations
- Token validation on POST/PUT/DELETE
- Secure token generation using secrets module

### Input Validation

- String sanitization (max length, null bytes)
- Email validation
- Type checking
- SQL injection prevention (parameterized queries)

## Data Protection

### Encryption

- **In Transit**: TLS 1.2+ (HTTPS)
- **At Rest**: Azure Storage encryption
- **Secrets**: Azure Key Vault

### Data Retention

- Session data: 1 hour TTL
- Audit logs: 90 days retention
- Sensitive data: Encrypted at rest

## Compliance

### GDPR Compliance

- User consent for data processing
- Right to be forgotten (data deletion)
- Data portability support
- Privacy by design

### Audit Logging

All security events logged:
- Authentication attempts
- Authorization failures
- Rate limit violations
- Token refresh events
- Session creation/deletion

## Incident Response

### Security Incident Procedure

1. **Detection**: Monitor logs for anomalies
2. **Containment**: Revoke compromised tokens
3. **Investigation**: Analyze audit logs
4. **Remediation**: Rotate secrets, patch vulnerabilities
5. **Recovery**: Restore from backups if needed
6. **Communication**: Notify affected users

### Common Vulnerabilities

| Vulnerability | Mitigation |
|---|---|
| SQL Injection | Parameterized queries |
| XSS | Input sanitization, CSP headers |
| CSRF | CSRF tokens, SameSite cookies |
| Brute Force | Rate limiting, account lockout |
| Token Theft | HTTPS only, httpOnly cookies |
| Privilege Escalation | Scope validation, RBAC |

## Security Checklist

- [ ] HTTPS enabled in production
- [ ] JWT_SECRET configured securely
- [ ] Redis password protected
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] CSRF tokens implemented
- [ ] Audit logging enabled
- [ ] Security headers configured
- [ ] Regular security audits scheduled
- [ ] Incident response plan documented

## File Validation & Upload Security

### Traditional DMS Weaknesses Addressed

**Issue:** Weak MIME type validation, no file size limits, susceptibility to malicious uploads.

**Our Implementation:** Comprehensive file validation with multiple layers of protection.

### 1. MIME Type Validation

**Location:** `backend/shared/file_validator.py` (lines 158-168)

**Implementation:**
```python
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/tiff',
    'image/x-tiff',
}

ALLOWED_EXTENSIONS = {
    '.pdf', '.jpg', '.jpeg', '.png', '.tif', '.tiff',
}
```

**Validation Process:**
1. Filename extension checked against whitelist
2. Content-Type header validated against allowed MIME types
3. Mimetypes module guess verification
4. Explicit rejection of unsupported formats with detailed error messages

**Examples:**
- ✅ `document.pdf` with `Content-Type: application/pdf` - **ALLOWED**
- ❌ `file.exe` with `Content-Type: application/x-msdownload` - **REJECTED**
- ❌ `script.js` with `Content-Type: application/javascript` - **REJECTED**
- ❌ `archive.zip` with `Content-Type: application/zip` - **REJECTED**

### 2. File Size Limits

**Location:** `backend/shared/file_validator.py` (lines 42-47)

**Configuration:**
```python
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # 52,428,800 bytes
```

**Purpose:** Prevent resource exhaustion attacks

**Validation:**
- Checks actual file size during upload
- Rejects files exceeding 50MB limit
- Returns detailed error message with actual size

**Examples:**
- ✅ 10MB PDF - **ALLOWED**
- ✅ 50MB maximum size document - **ALLOWED**
- ❌ 51MB file - **REJECTED** ("File exceeds maximum size limit")

### 3. File Signature Validation (Magic Numbers)

**Location:** `backend/shared/file_validator.py` (lines 145-175)

**Purpose:** Verify file content matches its extension (prevents spoofed files)

**Supported Signatures:**
```python
FILE_SIGNATURES = {
    b'%PDF': '.pdf',           # PDF files must start with %PDF
    b'\xFF\xD8\xFF': '.jpg',   # JPEG magic number
    b'\x89PNG': '.png',        # PNG magic number
    b'II\x2A\x00': '.tif',    # TIFF little-endian
    b'MM\x00\x2A': '.tif',    # TIFF big-endian
}
```

**Attack Prevention:**
- Prevents uploading malware disguised as PDF/JPG
- Detects tampered file headers
- Example attack blocked: `.exe` file renamed to `.pdf`

### 4. Upload Endpoint Integration

**Location:** `backend/api_upload_document/__init__.py`

**Validation Flow:**
```python
# Extract file from request
filename = f.filename
file_content = f.stream.read()
content_type = f.content_type

# Validate file
is_valid, error_message = FileValidator.validate_file(
    filename, 
    file_content, 
    content_type
)

# Reject if invalid
if not is_valid:
    return func.HttpResponse(
        json.dumps({"error": f"File validation failed: {error_message}"}),
        mimetype="application/json",
        status_code=400
    )

# Proceed to upload if valid
storage_client.upload_to_blob("raw-documents", blob_name, file_content)
```

### 5. Ingestion Timer Protection

**Location:** `backend/ingestion_timer/__init__.py`

**Applied to:** Email, Google Drive, Dropbox file ingestion

**Validation:**
```python
# Validates all files from all sources
is_valid, error_msg = FileValidator.validate_file(filename, content)
if not is_valid:
    logging.warning(f"❌ File validation failed for '{filename}': {error_msg}")
    continue  # Skip invalid file

# Only valid files are uploaded
storage_client.upload_to_blob("raw-documents", blob_name, content)
```

---

## HTML Content Sanitization & XSS Prevention

### Traditional DMS Weaknesses Addressed

**Issue:** Unsafe HTML rendering leading to XSS attacks when displaying extracted content.

**Our Implementation:** Multi-layer HTML sanitization preventing script injection.

### 1. Content Escaper Module

**Location:** `backend/shared/content_escaper.py` (lines 590-599)

**Core Functions:**

#### HTML Escaping
```python
ContentEscaper.escape_html(content)
# Converts: < to &lt;, > to &gt;, & to &amp;, " to &quot;, ' to &#x27;
```

#### HTML Sanitization (Strict Mode)
```python
ContentEscaper.sanitize_html(content, strict=True)
# Removes all HTML tags, escapes all special characters
```

#### Suspicious Pattern Removal
```python
ContentEscaper.remove_suspicious_patterns(content)
# Removes: <script>, <iframe>, event handlers, javascript: protocol
```

### 2. XSS Attack Prevention Examples

**Attack Vector 1: Script Injection**
```html
Input:  <script>alert('XSS')</script>
Output: &lt;script&gt;alert('XSS')&lt;/script&gt;
Result: ✅ BLOCKED - Script tag rendered as text
```

**Attack Vector 2: Event Handler Injection**
```html
Input:  <img src="x" onerror="alert('XSS')">
Output: &lt;img src=&quot;x&quot; onerror=&quot;alert('XSS')&quot;&gt;
Result: ✅ BLOCKED - Event handler rendered as text
```

**Attack Vector 3: JavaScript Protocol**
```html
Input:  <a href="javascript:alert('XSS')">Click</a>
Output: &lt;a href=&quot;javascript:alert('XSS')&quot;&gt;Click&lt;/a&gt;
Result: ✅ BLOCKED - Protocol sanitized
```

### 3. Data Structure Escaping

**Recursive Dictionary Escaping:**
```python
data = {
    'name': '<script>alert(1)</script>',
    'nested': {
        'value': '<img onerror=alert(1)>'
    }
}
escaped = ContentEscaper.escape_dict_values(data)
# Result: All string values HTML-escaped recursively
```

**List Escaping:**
```python
list_data = ['<script>alert(1)</script>', 'normal text']
escaped = ContentEscaper.escape_list_values(list_data)
# Result: All string values in list HTML-escaped
```

### 4. HTML Sanitizer (Safe Tag Preservation)

**Location:** `backend/shared/content_escaper.py` (HTMLSanitizer class)

**Safe Tags Allowed:**
```python
SAFE_TAGS = {
    'p', 'br', 'strong', 'b', 'em', 'i', 'u',
    'blockquote', 'code', 'pre', 'span', 'div',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'table', 'tr', 'td', 'th'
}

SAFE_ATTRIBUTES = {'class', 'id', 'style', 'title', 'href', 'alt'}
```

**Security Features:**
- Removes dangerous tags (script, iframe, object, etc.)
- Strips unsafe attributes (event handlers)
- Validates URL protocols (blocks javascript:, data:)
- HTML-escapes text content

### 5. Integration with API Responses

**Apply HTML Escaping Before Returning Data:**
```python
from shared.content_escaper import escape_html_response

# Before returning API response
response_data = {
    "extracted_text": document_text,
    "fields": extracted_fields
}

# Escape all values
safe_response = escape_html_response(response_data)

# Return to client
return func.HttpResponse(json.dumps(safe_response), mimetype="application/json")
```

---

## Testing & Validation

### Unit Tests

**Location:** `backend/tests/test_file_validation.py`

**Test Coverage:**
- ✅ Filename validation (path traversal prevention)
- ✅ File size validation (limit enforcement)
- ✅ MIME type validation
- ✅ PDF signature verification
- ✅ JPEG signature verification
- ✅ PNG signature verification
- ✅ TIFF signature verification
- ✅ Comprehensive validation workflow
- ✅ HTML escaping
- ✅ JavaScript escaping
- ✅ CSV escaping
- ✅ Suspicious pattern removal
- ✅ Safe tag preservation
- ✅ Event handler stripping

### Running Tests

```bash
# Run all file validation tests
python -m pytest backend/tests/test_file_validation.py -v

# Run specific test
python -m pytest backend/tests/test_file_validation.py::TestFileValidator::test_validate_pdf_signature -v

# Run with coverage
python -m pytest backend/tests/test_file_validation.py --cov=backend/shared/file_validator --cov=backend/shared/content_escaper
```

---

## Security Checklist

- [ ] HTTPS enabled in production
- [ ] JWT_SECRET configured securely
- [ ] Redis password protected
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] CSRF tokens implemented
- [ ] Audit logging enabled
- [ ] Security headers configured
- [ ] Regular security audits scheduled
- [ ] Incident response plan documented
- [x] **File upload validation implemented (MIME + Size + Signature)**
- [x] **HTML content sanitization implemented (XSS prevention)**
- [ ] All file uploads tested with malicious samples
- [ ] Security headers include CSP with strict policy
- [ ] Regular penetration testing scheduled

---

## DOKUMENTÁCIÓ VERZIÓ ÉS FRISSÍTÉSI TÖRTÉNET

**Verzió:** 1.0
**Utolsó frissítés:** 2025-11-23
**Commit:** d11b0776

### Frissítési Történet
* **v1.0** (2025-11-23): Eredeti verzió - Security guidelines és best practices

