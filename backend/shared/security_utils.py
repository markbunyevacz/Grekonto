"""
Security utilities including rate limiting, CSRF protection, and secure headers.
"""

import logging
import hashlib
import secrets
import os
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple rate limiter using in-memory storage.
    For production, use Redis-backed rate limiting.
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> Tuple[bool, Dict[str, int]]:
        """
        Check if request is allowed.
        
        Args:
            identifier: User ID or IP address
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]
        
        # Check limit
        request_count = len(self.requests[identifier])
        is_allowed = request_count < self.max_requests
        
        if is_allowed:
            self.requests[identifier].append(now)
        
        return is_allowed, {
            "limit": self.max_requests,
            "remaining": max(0, self.max_requests - request_count - 1),
            "reset": int((window_start + timedelta(seconds=self.window_seconds)).timestamp())
        }


class CSRFProtection:
    """CSRF token generation and validation."""
    
    @staticmethod
    def generate_token() -> str:
        """Generate a CSRF token."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_token(token: str, stored_token: str) -> bool:
        """Validate CSRF token."""
        if not token or not stored_token:
            return False
        
        # Use constant-time comparison to prevent timing attacks
        return secrets.compare_digest(token, stored_token)


class SecureHeaders:
    """Security headers for HTTP responses."""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get recommended security headers."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }


class PasswordValidator:
    """Password validation utilities."""
    
    @staticmethod
    def validate(password: str, min_length: int = 12) -> Tuple[bool, str]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            min_length: Minimum password length
            
        Returns:
            Tuple of (is_valid, message)
        """
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not (has_upper and has_lower and has_digit and has_special):
            return False, "Password must contain uppercase, lowercase, digit, and special character"
        
        return True, "Password is strong"
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Hash password with salt.
        
        Args:
            password: Password to hash
            salt: Optional salt (generated if not provided)
            
        Returns:
            Tuple of (hashed_password, salt)
        """
        if not salt:
            salt = secrets.token_hex(16)
        
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        )
        
        return hashed.hex(), salt
    
    @staticmethod
    def verify_password(password: str, hashed: str, salt: str) -> bool:
        """Verify password against hash."""
        new_hash, _ = PasswordValidator.hash_password(password, salt)
        return secrets.compare_digest(new_hash, hashed)


class InputValidator:
    """Input validation utilities."""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input."""
        if not isinstance(value, str):
            return ""
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Truncate to max length
        return value[:max_length].strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

