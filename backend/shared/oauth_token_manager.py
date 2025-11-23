"""
OAuth 2.0 token management with automatic refresh and validation.

Handles token lifecycle including creation, validation, refresh, and expiration.
"""

import jwt
import logging
import os
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class OAuthTokenManager:
    """
    Manages OAuth 2.0 tokens with validation and automatic refresh.
    
    Features:
    - JWT token creation and validation
    - Automatic token refresh
    - Expiration checking
    - Token revocation support
    """
    
    def __init__(self, secret_key: Optional[str] = None, algorithm: str = "HS256"):
        """
        Initialize OAuth token manager.
        
        Args:
            secret_key: Secret key for token signing (default from JWT_SECRET env var)
            algorithm: JWT algorithm (HS256, RS256, etc.)
        """
        self.secret_key = secret_key or os.environ.get("JWT_SECRET", "dev-secret-key")
        self.algorithm = algorithm
        self.revoked_tokens: set = set()  # In production, use Redis
    
    def create_token(self, user_id: str, scopes: list, 
                    expires_in_seconds: int = 3600,
                    additional_claims: Optional[Dict] = None) -> str:
        """
        Create a new JWT token.
        
        Args:
            user_id: User identifier
            scopes: List of permission scopes
            expires_in_seconds: Token expiration time
            additional_claims: Extra claims to include
            
        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        payload = {
            "user_id": user_id,
            "scopes": scopes,
            "iat": now,
            "exp": now + timedelta(seconds=expires_in_seconds),
            "type": "access"
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        try:
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"✓ Token created for user: {user_id}")
            return token
        except Exception as e:
            logger.error(f"Error creating token: {str(e)}")
            raise
    
    def validate_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate a JWT token.
        
        Args:
            token: JWT token to validate
            
        Returns:
            Tuple of (is_valid, payload)
        """
        try:
            # Check if token is revoked
            if token in self.revoked_tokens:
                logger.warning("Token is revoked")
                return False, None
            
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            logger.debug(f"✓ Token validated for user: {payload.get('user_id')}")
            return True, payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return False, None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return False, None
    
    def refresh_token(self, token: str, new_expires_in: int = 3600) -> Optional[str]:
        """
        Refresh an existing token.
        
        Args:
            token: Current token
            new_expires_in: New expiration time
            
        Returns:
            New token or None if refresh failed
        """
        is_valid, payload = self.validate_token(token)
        
        if not is_valid or not payload:
            logger.warning("Cannot refresh invalid token")
            return None
        
        # Create new token with same claims
        new_token = self.create_token(
            user_id=payload["user_id"],
            scopes=payload.get("scopes", []),
            expires_in_seconds=new_expires_in,
            additional_claims={k: v for k, v in payload.items() 
                             if k not in ["iat", "exp", "type"]}
        )
        
        logger.info(f"✓ Token refreshed for user: {payload['user_id']}")
        return new_token
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a token."""
        try:
            self.revoked_tokens.add(token)
            logger.info("✓ Token revoked")
            return True
        except Exception as e:
            logger.error(f"Error revoking token: {str(e)}")
            return False
    
    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """Get token expiration time."""
        is_valid, payload = self.validate_token(token)
        if is_valid and payload:
            return datetime.fromtimestamp(payload["exp"])
        return None
    
    def is_token_expiring_soon(self, token: str, 
                              threshold_seconds: int = 300) -> bool:
        """Check if token is expiring within threshold."""
        expiry = self.get_token_expiry(token)
        if not expiry:
            return True
        
        time_until_expiry = (expiry - datetime.utcnow()).total_seconds()
        return time_until_expiry < threshold_seconds

