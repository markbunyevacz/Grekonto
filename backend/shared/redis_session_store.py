"""
Redis-backed session store for OAuth 2.0 token management and user sessions.

This module provides persistent session storage with automatic token refresh,
expiration checking, and fallback to in-memory storage for development.
"""

import redis
import json
import logging
import os
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)


class RedisSessionStore:
    """
    Manages user sessions and OAuth tokens using Redis with in-memory fallback.
    
    Features:
    - Persistent session storage
    - Automatic token expiration handling
    - Token refresh capability
    - Health checks and monitoring
    - Development mode with in-memory fallback
    """
    
    def __init__(self, redis_url: Optional[str] = None, fallback_to_memory: bool = True):
        """
        Initialize Redis session store.
        
        Args:
            redis_url: Redis connection URL (default from REDIS_URL env var)
            fallback_to_memory: Enable in-memory fallback for development
        """
        self.redis_url = redis_url or os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        self.fallback_to_memory = fallback_to_memory
        self.memory_store: Dict[str, Dict[str, Any]] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.use_redis = False
        
        self._initialize_redis()
    
    def _initialize_redis(self) -> None:
        """Initialize Redis connection with error handling."""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_client.ping()
            self.use_redis = True
            logger.info("✓ Redis session store initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {str(e)}")
            if self.fallback_to_memory:
                logger.warning("⚠️ Falling back to in-memory session storage (NOT for production)")
                self.use_redis = False
            else:
                raise
    
    def create_session(self, user_id: str, token_data: Dict[str, Any], 
                      ttl_seconds: int = 3600) -> str:
        """
        Create a new session with OAuth token data.
        
        Args:
            user_id: Unique user identifier
            token_data: OAuth token information
            ttl_seconds: Session time-to-live in seconds
            
        Returns:
            Session ID
        """
        session_id = self._generate_session_id(user_id)
        session_data = {
            "user_id": user_id,
            "token_data": json.dumps(token_data),
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat()
        }
        
        if self.use_redis:
            self.redis_client.setex(
                f"session:{session_id}",
                ttl_seconds,
                json.dumps(session_data)
            )
        else:
            self.memory_store[session_id] = session_data
        
        logger.info(f"✓ Session created for user: {user_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data by ID."""
        try:
            if self.use_redis:
                data = self.redis_client.get(f"session:{session_id}")
            else:
                data = self.memory_store.get(session_id)
            
            if data:
                return json.loads(data) if isinstance(data, str) else data
            return None
        except Exception as e:
            logger.error(f"Error retrieving session: {str(e)}")
            return None
    
    def refresh_token(self, session_id: str, new_token_data: Dict[str, Any]) -> bool:
        """Refresh OAuth token for a session."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session["token_data"] = json.dumps(new_token_data)
        session["last_activity"] = datetime.utcnow().isoformat()
        
        try:
            if self.use_redis:
                ttl = self.redis_client.ttl(f"session:{session_id}")
                self.redis_client.setex(
                    f"session:{session_id}",
                    max(ttl, 3600),
                    json.dumps(session)
                )
            else:
                self.memory_store[session_id] = session
            
            logger.info(f"✓ Token refreshed for session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        try:
            if self.use_redis:
                self.redis_client.delete(f"session:{session_id}")
            else:
                self.memory_store.pop(session_id, None)
            
            logger.info(f"✓ Session deleted: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting session: {str(e)}")
            return False
    
    def _generate_session_id(self, user_id: str) -> str:
        """Generate a unique session ID."""
        data = f"{user_id}:{datetime.utcnow().isoformat()}:{os.urandom(16).hex()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def health_check(self) -> Dict[str, Any]:
        """Check session store health."""
        status = {
            "redis_available": self.use_redis,
            "memory_fallback": not self.use_redis and self.fallback_to_memory,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.use_redis:
            try:
                self.redis_client.ping()
                status["redis_status"] = "healthy"
            except Exception as e:
                status["redis_status"] = f"unhealthy: {str(e)}"
        
        return status

