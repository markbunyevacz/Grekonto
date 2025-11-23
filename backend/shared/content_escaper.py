"""
HTML sanitization and content escaping module for XSS prevention.

Provides functions to escape and sanitize HTML content extracted from documents
to prevent Cross-Site Scripting (XSS) attacks when rendering data in web interfaces.
"""

import logging
import html
import re
from typing import Any, Dict, List, Union, Tuple
from html.parser import HTMLParser

logger = logging.getLogger(__name__)


class HTMLSanitizer(HTMLParser):
    """
    Custom HTML parser for sanitizing HTML content.
    Removes potentially dangerous tags and attributes.
    """
    
    # Tags that are safe to keep (if their content is also safe)
    SAFE_TAGS = {
        'p', 'br', 'hr', 'strong', 'b', 'em', 'i', 'u', 'del', 's',
        'blockquote', 'code', 'pre', 'span', 'div', 'h1', 'h2', 'h3',
        'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'dl', 'dt', 'dd', 'table',
        'thead', 'tbody', 'tfoot', 'tr', 'td', 'th', 'caption', 'a'
    }
    
    # Attributes that are safe to keep on safe tags
    SAFE_ATTRIBUTES = {
        'class', 'id', 'style', 'title', 'href', 'alt', 'src'
    }
    
    # Dangerous protocols to block in URLs
    DANGEROUS_PROTOCOLS = {
        'javascript:', 'data:', 'vbscript:', 'file:', 'about:'
    }
    
    def __init__(self):
        super().__init__()
        self.result = []
        self.tag_stack = []
    
    def handle_starttag(self, tag, attrs):
        """Handle opening tags - only keep safe tags with safe attributes."""
        if tag.lower() not in self.SAFE_TAGS:
            return
        
        # Filter attributes to only safe ones
        safe_attrs = []
        for attr, value in attrs:
            if attr.lower() in self.SAFE_ATTRIBUTES:
                # Additional validation for href and src
                if attr.lower() in {'href', 'src'}:
                    if not self._is_safe_url(value):
                        continue
                safe_attrs.append((attr, value))
        
        # Reconstruct tag with safe attributes
        if safe_attrs:
            attr_str = ' '.join(f'{k}="{html.escape(str(v))}"' for k, v in safe_attrs)
            self.result.append(f'<{tag} {attr_str}>')
        else:
            self.result.append(f'<{tag}>')
        
        self.tag_stack.append(tag.lower())
    
    def handle_endtag(self, tag):
        """Handle closing tags."""
        if tag.lower() in self.SAFE_TAGS and self.tag_stack and self.tag_stack[-1] == tag.lower():
            self.result.append(f'</{tag}>')
            self.tag_stack.pop()
    
    def handle_data(self, data):
        """Handle text content."""
        self.result.append(html.escape(data))
    
    def _is_safe_url(self, url: str) -> bool:
        """Check if URL is safe (doesn't contain dangerous protocols)."""
        url_lower = url.lower().strip()
        for dangerous_protocol in self.DANGEROUS_PROTOCOLS:
            if url_lower.startswith(dangerous_protocol):
                return False
        return True
    
    def get_sanitized_html(self) -> str:
        """Get the sanitized HTML result."""
        return ''.join(self.result)


class ContentEscaper:
    """Utilities for escaping and sanitizing content."""
    
    @staticmethod
    def escape_html(content: str) -> str:
        """
        Escape HTML special characters to prevent XSS.
        Converts: < to &lt;, > to &gt;, & to &amp;, " to &quot;, ' to &#x27;
        
        Args:
            content: Raw content to escape
            
        Returns:
            HTML-escaped content
        """
        if not isinstance(content, str):
            return str(content)
        
        return html.escape(content, quote=True)
    
    @staticmethod
    def escape_javascript(content: str) -> str:
        """
        Escape content for safe use in JavaScript strings.
        
        Args:
            content: Raw content to escape
            
        Returns:
            JavaScript-safe escaped content
        """
        if not isinstance(content, str):
            content = str(content)
        
        # Escape backslashes first (must be first)
        content = content.replace('\\', '\\\\')
        # Escape quotes
        content = content.replace('"', '\\"')
        content = content.replace("'", "\\'")
        # Escape newlines
        content = content.replace('\n', '\\n')
        content = content.replace('\r', '\\r')
        # Escape special characters
        content = content.replace('\t', '\\t')
        content = content.replace('\b', '\\b')
        content = content.replace('\f', '\\f')
        
        return content
    
    @staticmethod
    def escape_csv(content: str) -> str:
        """
        Escape content for safe use in CSV format.
        
        Args:
            content: Raw content to escape
            
        Returns:
            CSV-safe escaped content
        """
        if not isinstance(content, str):
            content = str(content)
        
        # If content contains special characters, wrap in quotes and escape quotes
        if any(char in content for char in [',', '"', '\n', '\r']):
            content = content.replace('"', '""')
            return f'"{content}"'
        
        return content
    
    @staticmethod
    def remove_suspicious_patterns(content: str) -> str:
        """
        Remove or neutralize suspicious patterns commonly used in attacks.
        
        Args:
            content: Content to scan
            
        Returns:
            Content with suspicious patterns removed
        """
        if not isinstance(content, str):
            return content
        
        # Remove script tags and content
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove iframe tags
        content = re.sub(r'<iframe[^>]*>.*?</iframe>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove event handlers
        content = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
        
        # Remove javascript: protocol
        content = re.sub(r'javascript\s*:', '', content, flags=re.IGNORECASE)
        
        # Remove data: protocol
        content = re.sub(r'data\s*:', '', content, flags=re.IGNORECASE)
        
        return content
    
    @staticmethod
    def sanitize_html(content: str, strict: bool = True) -> str:
        """
        Comprehensive HTML sanitization.
        
        Args:
            content: HTML content to sanitize
            strict: If True, remove all HTML; if False, keep safe tags
            
        Returns:
            Sanitized content
        """
        if not isinstance(content, str):
            return str(content)
        
        # First pass: remove suspicious patterns
        content = ContentEscaper.remove_suspicious_patterns(content)
        
        if strict:
            # Strict mode: escape all HTML
            return ContentEscaper.escape_html(content)
        else:
            # Lenient mode: keep safe HTML tags
            try:
                sanitizer = HTMLSanitizer()
                sanitizer.feed(content)
                return sanitizer.get_sanitized_html()
            except Exception as e:
                logger.warning(f"HTML sanitization failed, falling back to escape: {str(e)}")
                return ContentEscaper.escape_html(content)
    
    @staticmethod
    def escape_dict_values(data: Dict[str, Any], escape_fn=None) -> Dict[str, Any]:
        """
        Recursively escape all string values in a dictionary.
        
        Args:
            data: Dictionary to process
            escape_fn: Function to use for escaping (defaults to escape_html)
            
        Returns:
            Dictionary with escaped values
        """
        if escape_fn is None:
            escape_fn = ContentEscaper.escape_html
        
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = escape_fn(value)
            elif isinstance(value, dict):
                result[key] = ContentEscaper.escape_dict_values(value, escape_fn)
            elif isinstance(value, list):
                result[key] = [
                    escape_fn(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def escape_list_values(data: List[Any], escape_fn=None) -> List[Any]:
        """
        Recursively escape all string values in a list.
        
        Args:
            data: List to process
            escape_fn: Function to use for escaping (defaults to escape_html)
            
        Returns:
            List with escaped values
        """
        if escape_fn is None:
            escape_fn = ContentEscaper.escape_html
        
        result = []
        for item in data:
            if isinstance(item, str):
                result.append(escape_fn(item))
            elif isinstance(item, dict):
                result.append(ContentEscaper.escape_dict_values(item, escape_fn))
            elif isinstance(item, list):
                result.append(ContentEscaper.escape_list_values(item, escape_fn))
            else:
                result.append(item)
        
        return result


def escape_html_response(data: Union[str, Dict, List]) -> Union[str, Dict, List]:
    """
    Convenience function to escape HTML in API responses.
    
    Args:
        data: Data to escape (string, dict, or list)
        
    Returns:
        Escaped data
    """
    if isinstance(data, str):
        return ContentEscaper.escape_html(data)
    elif isinstance(data, dict):
        return ContentEscaper.escape_dict_values(data)
    elif isinstance(data, list):
        return ContentEscaper.escape_list_values(data)
    else:
        return data
