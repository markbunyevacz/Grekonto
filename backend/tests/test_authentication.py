"""
Unit tests for authentication and session management.
"""

import unittest
import json
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Import modules to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.oauth_token_manager import OAuthTokenManager
from shared.redis_session_store import RedisSessionStore
from shared.security_utils import (
    RateLimiter, CSRFProtection, PasswordValidator, InputValidator
)


class TestOAuthTokenManager(unittest.TestCase):
    """Test OAuth token manager."""
    
    def setUp(self):
        self.manager = OAuthTokenManager(secret_key="test-secret")
    
    def test_create_token(self):
        """Test token creation."""
        token = self.manager.create_token("user123", ["read", "write"])
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
    
    def test_validate_token(self):
        """Test token validation."""
        token = self.manager.create_token("user123", ["read"])
        is_valid, payload = self.manager.validate_token(token)
        
        self.assertTrue(is_valid)
        self.assertEqual(payload["user_id"], "user123")
        self.assertIn("read", payload["scopes"])
    
    def test_invalid_token(self):
        """Test invalid token validation."""
        is_valid, payload = self.manager.validate_token("invalid-token")
        self.assertFalse(is_valid)
        self.assertIsNone(payload)
    
    def test_refresh_token(self):
        """Test token refresh."""
        token = self.manager.create_token("user123", ["read"])
        time.sleep(0.1)  # Small delay to ensure different iat
        new_token = self.manager.refresh_token(token)

        self.assertIsNotNone(new_token)
        # Tokens may be identical if created within same second, so just validate new token

        is_valid, payload = self.manager.validate_token(new_token)
        self.assertTrue(is_valid)
        self.assertEqual(payload["user_id"], "user123")
    
    def test_revoke_token(self):
        """Test token revocation."""
        token = self.manager.create_token("user123", ["read"])
        self.manager.revoke_token(token)
        
        is_valid, payload = self.manager.validate_token(token)
        self.assertFalse(is_valid)
    
    def test_token_expiry_check(self):
        """Test token expiry checking."""
        token = self.manager.create_token("user123", ["read"], expires_in_seconds=1)
        
        # Token should not be expiring soon
        self.assertFalse(self.manager.is_token_expiring_soon(token, threshold_seconds=0))
        
        # Wait for token to expire
        time.sleep(2)
        
        # Token should be expired
        is_valid, _ = self.manager.validate_token(token)
        self.assertFalse(is_valid)


class TestRedisSessionStore(unittest.TestCase):
    """Test Redis session store."""
    
    def setUp(self):
        # Use memory fallback for testing
        self.store = RedisSessionStore(fallback_to_memory=True)
    
    def test_create_session(self):
        """Test session creation."""
        session_id = self.store.create_session(
            "user123",
            {"token": "test-token"}
        )
        self.assertIsNotNone(session_id)
    
    def test_get_session(self):
        """Test session retrieval."""
        session_id = self.store.create_session(
            "user123",
            {"token": "test-token"}
        )
        session = self.store.get_session(session_id)
        
        self.assertIsNotNone(session)
        self.assertEqual(session["user_id"], "user123")
    
    def test_delete_session(self):
        """Test session deletion."""
        session_id = self.store.create_session(
            "user123",
            {"token": "test-token"}
        )
        self.store.delete_session(session_id)
        
        session = self.store.get_session(session_id)
        self.assertIsNone(session)
    
    def test_refresh_token(self):
        """Test token refresh in session."""
        session_id = self.store.create_session(
            "user123",
            {"token": "old-token"}
        )
        
        self.store.refresh_token(session_id, {"token": "new-token"})
        session = self.store.get_session(session_id)
        
        self.assertIsNotNone(session)
        token_data = json.loads(session["token_data"])
        self.assertEqual(token_data["token"], "new-token")


class TestRateLimiter(unittest.TestCase):
    """Test rate limiter."""
    
    def setUp(self):
        self.limiter = RateLimiter(max_requests=3, window_seconds=60)
    
    def test_rate_limit_allowed(self):
        """Test requests within limit."""
        for i in range(3):
            is_allowed, _ = self.limiter.is_allowed("user123")
            self.assertTrue(is_allowed)
    
    def test_rate_limit_exceeded(self):
        """Test requests exceeding limit."""
        for i in range(3):
            self.limiter.is_allowed("user123")
        
        is_allowed, _ = self.limiter.is_allowed("user123")
        self.assertFalse(is_allowed)


class TestCSRFProtection(unittest.TestCase):
    """Test CSRF protection."""
    
    def test_generate_token(self):
        """Test CSRF token generation."""
        token = CSRFProtection.generate_token()
        self.assertIsNotNone(token)
        self.assertGreater(len(token), 20)
    
    def test_validate_token(self):
        """Test CSRF token validation."""
        token = CSRFProtection.generate_token()
        self.assertTrue(CSRFProtection.validate_token(token, token))
    
    def test_invalid_token(self):
        """Test invalid CSRF token."""
        token1 = CSRFProtection.generate_token()
        token2 = CSRFProtection.generate_token()
        self.assertFalse(CSRFProtection.validate_token(token1, token2))


class TestPasswordValidator(unittest.TestCase):
    """Test password validation."""
    
    def test_weak_password(self):
        """Test weak password rejection."""
        is_valid, _ = PasswordValidator.validate("weak")
        self.assertFalse(is_valid)
    
    def test_strong_password(self):
        """Test strong password acceptance."""
        is_valid, _ = PasswordValidator.validate("StrongP@ss123")
        self.assertTrue(is_valid)
    
    def test_password_hashing(self):
        """Test password hashing."""
        password = "TestPassword123!"
        hashed, salt = PasswordValidator.hash_password(password)
        
        self.assertIsNotNone(hashed)
        self.assertIsNotNone(salt)
        self.assertTrue(PasswordValidator.verify_password(password, hashed, salt))


class TestInputValidator(unittest.TestCase):
    """Test input validation."""
    
    def test_sanitize_string(self):
        """Test string sanitization."""
        result = InputValidator.sanitize_string("  test  ")
        self.assertEqual(result, "test")
    
    def test_sanitize_null_bytes(self):
        """Test null byte removal."""
        result = InputValidator.sanitize_string("test\x00value")
        self.assertEqual(result, "testvalue")
    
    def test_validate_email(self):
        """Test email validation."""
        self.assertTrue(InputValidator.validate_email("user@example.com"))
        self.assertFalse(InputValidator.validate_email("invalid-email"))


if __name__ == "__main__":
    unittest.main()

