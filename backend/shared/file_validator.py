"""
File validation module for upload security.

Implements strict MIME type validation, file size limits, and content validation
to prevent malicious uploads and resource exhaustion attacks.
"""

import logging
import mimetypes
from typing import Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


# Configuration
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Strictly allowed MIME types for document uploads
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/tiff',
    'image/x-tiff',
}

# Strictly allowed file extensions
ALLOWED_EXTENSIONS = {
    '.pdf',
    '.jpg',
    '.jpeg',
    '.png',
    '.tif',
    '.tiff',
}

# Magic numbers (file signatures) for content verification
FILE_SIGNATURES = {
    b'%PDF': '.pdf',
    b'\xFF\xD8\xFF': '.jpg',  # JPEG
    b'\x89PNG': '.png',
    b'II\x2A\x00': '.tif',  # TIFF (little-endian)
    b'MM\x00\x2A': '.tif',  # TIFF (big-endian)
}


class FileValidationError(Exception):
    """Custom exception for file validation failures."""
    pass


class FileValidator:
    """Validates uploaded files for security and compliance."""

    @staticmethod
    def validate_filename(filename: str) -> Tuple[bool, str]:
        """
        Validate filename for security issues.
        
        Args:
            filename: The filename to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename or len(filename.strip()) == 0:
            return False, "Filename cannot be empty"
        
        if len(filename) > 255:
            return False, f"Filename too long ({len(filename)} > 255 characters)"
        
        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            return False, "Filename contains invalid path characters"
        
        # Verify file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            return False, f"Unsupported file extension '{file_ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        
        return True, ""

    @staticmethod
    def validate_file_size(file_size: int) -> Tuple[bool, str]:
        """
        Validate file size to prevent resource exhaustion.
        
        Args:
            file_size: File size in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if file_size <= 0:
            return False, "File size must be greater than 0"
        
        if file_size > MAX_FILE_SIZE_BYTES:
            return False, (
                f"File exceeds maximum size limit ({file_size / 1024 / 1024:.1f}MB "
                f"> {MAX_FILE_SIZE_MB}MB)"
            )
        
        return True, ""

    @staticmethod
    def validate_mime_type(
        filename: str, 
        content_type: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Validate MIME type based on filename and provided content-type header.
        
        Args:
            filename: The filename
            content_type: Optional Content-Type header value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        file_ext = Path(filename).suffix.lower()
        
        # Guess MIME type from filename
        guessed_type, _ = mimetypes.guess_type(filename)
        
        # If content_type is provided, validate it
        if content_type:
            content_type = content_type.lower().strip()
            if content_type not in ALLOWED_MIME_TYPES:
                return False, (
                    f"Content-Type '{content_type}' not allowed. "
                    f"Allowed: {', '.join(sorted(ALLOWED_MIME_TYPES))}"
                )
        
        # Validate guessed type matches allowed list
        if guessed_type and guessed_type.lower() not in ALLOWED_MIME_TYPES:
            return False, (
                f"File type for extension '{file_ext}' not allowed. "
                f"Guessed type: {guessed_type}"
            )
        
        return True, ""

    @staticmethod
    def validate_file_signature(file_content: bytes, filename: str) -> Tuple[bool, str]:
        """
        Validate file content by checking magic numbers (file signatures).
        Helps prevent attacks where malicious files are disguised with allowed extensions.
        
        Args:
            file_content: The actual file content (first 512 bytes minimum)
            filename: The filename
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(file_content) == 0:
            return False, "File content is empty"
        
        file_ext = Path(filename).suffix.lower()
        
        # Special handling for different file types
        if file_ext == '.pdf':
            if not file_content.startswith(b'%PDF'):
                return False, (
                    "File content does not match PDF format. "
                    "File signature validation failed (expected '%PDF')"
                )
        
        elif file_ext in {'.jpg', '.jpeg'}:
            if not file_content.startswith(b'\xFF\xD8\xFF'):
                return False, (
                    "File content does not match JPEG format. "
                    "File signature validation failed (expected JPEG header)"
                )
        
        elif file_ext == '.png':
            if not file_content.startswith(b'\x89PNG'):
                return False, (
                    "File content does not match PNG format. "
                    "File signature validation failed (expected PNG header)"
                )
        
        elif file_ext in {'.tif', '.tiff'}:
            # TIFF can be little-endian (II) or big-endian (MM)
            if not (file_content.startswith(b'II\x2A\x00') or 
                    file_content.startswith(b'MM\x00\x2A')):
                return False, (
                    "File content does not match TIFF format. "
                    "File signature validation failed (expected TIFF header)"
                )
        
        return True, ""

    @staticmethod
    def validate_file(
        filename: str,
        file_content: bytes,
        content_type: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Comprehensive file validation combining all checks.
        
        Args:
            filename: The filename
            file_content: The file content bytes
            content_type: Optional Content-Type header
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # 1. Validate filename
        is_valid, error_msg = FileValidator.validate_filename(filename)
        if not is_valid:
            logger.warning(f"Filename validation failed: {error_msg}")
            return False, error_msg
        
        # 2. Validate file size
        is_valid, error_msg = FileValidator.validate_file_size(len(file_content))
        if not is_valid:
            logger.warning(f"File size validation failed: {error_msg}")
            return False, error_msg
        
        # 3. Validate MIME type
        is_valid, error_msg = FileValidator.validate_mime_type(filename, content_type)
        if not is_valid:
            logger.warning(f"MIME type validation failed: {error_msg}")
            return False, error_msg
        
        # 4. Validate file signature (magic numbers)
        is_valid, error_msg = FileValidator.validate_file_signature(file_content, filename)
        if not is_valid:
            logger.warning(f"File signature validation failed: {error_msg}")
            return False, error_msg
        
        logger.info(f"✅ File '{filename}' passed all validation checks ({len(file_content)} bytes)")
        return True, ""

    @staticmethod
    def get_validation_summary() -> dict:
        """
        Get a summary of validation configuration.
        
        Returns:
            Dictionary with validation settings
        """
        return {
            "max_file_size_mb": MAX_FILE_SIZE_MB,
            "max_file_size_bytes": MAX_FILE_SIZE_BYTES,
            "allowed_mime_types": sorted(ALLOWED_MIME_TYPES),
            "allowed_extensions": sorted(ALLOWED_EXTENSIONS),
            "validation_checks": [
                "filename_validation",
                "size_limit_enforcement",
                "mime_type_validation",
                "file_signature_validation"
            ]
        }
