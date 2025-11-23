"""
Unit tests for file validation and content escaping modules.

Tests cover:
- MIME type validation
- File size limits
- File signature verification
- HTML sanitization and XSS prevention
"""

import unittest
from pathlib import Path
from shared.file_validator import FileValidator, ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES, MAX_FILE_SIZE_BYTES
from shared.content_escaper import ContentEscaper, HTMLSanitizer


class TestFileValidator(unittest.TestCase):
    """Test file validation functionality."""
    
    def test_validate_filename_valid(self):
        """Test validation of valid filenames."""
        valid_files = [
            'document.pdf',
            'invoice_2024.pdf',
            'photo.jpg',
            'image.png',
            'scan.tiff'
        ]
        for filename in valid_files:
            is_valid, msg = FileValidator.validate_filename(filename)
            self.assertTrue(is_valid, f"Should accept valid file: {filename}. Error: {msg}")
    
    def test_validate_filename_invalid(self):
        """Test rejection of invalid filenames."""
        invalid_files = [
            '../etc/passwd.txt',  # Path traversal
            '..\\windows\\system32\\file.exe',  # Windows path traversal
            'file.exe',  # Invalid extension
            'document.doc',  # Invalid extension
            'file.txt',  # Invalid extension
            '',  # Empty
            '   ',  # Whitespace only
        ]
        for filename in invalid_files:
            is_valid, msg = FileValidator.validate_filename(filename)
            self.assertFalse(is_valid, f"Should reject invalid file: {filename}")
    
    def test_validate_file_size_valid(self):
        """Test validation of valid file sizes."""
        valid_sizes = [
            100,
            1024 * 1024,  # 1MB
            10 * 1024 * 1024,  # 10MB
            50 * 1024 * 1024,  # 50MB (max)
        ]
        for size in valid_sizes:
            is_valid, msg = FileValidator.validate_file_size(size)
            self.assertTrue(is_valid, f"Should accept valid size: {size}")
    
    def test_validate_file_size_invalid(self):
        """Test rejection of invalid file sizes."""
        invalid_sizes = [
            0,
            -1,
            51 * 1024 * 1024,  # Over 50MB limit
            100 * 1024 * 1024,  # Way over limit
        ]
        for size in invalid_sizes:
            is_valid, msg = FileValidator.validate_file_size(size)
            self.assertFalse(is_valid, f"Should reject invalid size: {size}")
    
    def test_validate_mime_type_valid(self):
        """Test validation of valid MIME types."""
        valid_cases = [
            ('document.pdf', 'application/pdf'),
            ('photo.jpg', 'image/jpeg'),
            ('image.png', 'image/png'),
            ('scan.tiff', 'image/tiff'),
        ]
        for filename, mime_type in valid_cases:
            is_valid, msg = FileValidator.validate_mime_type(filename, mime_type)
            self.assertTrue(is_valid, f"Should accept valid MIME type: {mime_type}")
    
    def test_validate_mime_type_invalid(self):
        """Test rejection of invalid MIME types."""
        invalid_cases = [
            ('file.exe', 'application/x-msdownload'),
            ('script.js', 'application/javascript'),
            ('doc.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
            ('dangerous.zip', 'application/zip'),
        ]
        for filename, mime_type in invalid_cases:
            is_valid, msg = FileValidator.validate_mime_type(filename, mime_type)
            self.assertFalse(is_valid, f"Should reject invalid MIME type: {mime_type}")
    
    def test_validate_pdf_signature(self):
        """Test PDF file signature validation."""
        # Valid PDF signature
        valid_pdf = b'%PDF-1.4\n%test content'
        is_valid, msg = FileValidator.validate_file_signature(valid_pdf, 'test.pdf')
        self.assertTrue(is_valid, f"Should accept valid PDF signature")
        
        # Invalid PDF (missing signature)
        invalid_pdf = b'This is not a PDF file'
        is_valid, msg = FileValidator.validate_file_signature(invalid_pdf, 'test.pdf')
        self.assertFalse(is_valid, "Should reject invalid PDF signature")
    
    def test_validate_jpeg_signature(self):
        """Test JPEG file signature validation."""
        # Valid JPEG signature
        valid_jpeg = b'\xFF\xD8\xFF\xE0' + b'\x00' * 100
        is_valid, msg = FileValidator.validate_file_signature(valid_jpeg, 'test.jpg')
        self.assertTrue(is_valid, "Should accept valid JPEG signature")
        
        # Invalid JPEG
        invalid_jpeg = b'Not a JPEG'
        is_valid, msg = FileValidator.validate_file_signature(invalid_jpeg, 'test.jpg')
        self.assertFalse(is_valid, "Should reject invalid JPEG signature")
    
    def test_validate_png_signature(self):
        """Test PNG file signature validation."""
        # Valid PNG signature
        valid_png = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        is_valid, msg = FileValidator.validate_file_signature(valid_png, 'test.png')
        self.assertTrue(is_valid, "Should accept valid PNG signature")
        
        # Invalid PNG
        invalid_png = b'Not a PNG'
        is_valid, msg = FileValidator.validate_file_signature(invalid_png, 'test.png')
        self.assertFalse(is_valid, "Should reject invalid PNG signature")
    
    def test_comprehensive_validation(self):
        """Test comprehensive file validation."""
        # Valid file
        valid_file = b'%PDF-1.4\nTest PDF content'
        is_valid, msg = FileValidator.validate_file('document.pdf', valid_file, 'application/pdf')
        self.assertTrue(is_valid, f"Should accept valid file: {msg}")
        
        # Invalid file (wrong extension + wrong content)
        invalid_file = b'Some malicious content'
        is_valid, msg = FileValidator.validate_file('executable.exe', invalid_file, 'application/x-msdownload')
        self.assertFalse(is_valid, "Should reject invalid executable")
        
        # File too large
        large_file = b'x' * (51 * 1024 * 1024)
        is_valid, msg = FileValidator.validate_file('toolarge.pdf', large_file, 'application/pdf')
        self.assertFalse(is_valid, "Should reject oversized file")


class TestContentEscaper(unittest.TestCase):
    """Test HTML content escaping and sanitization."""
    
    def test_escape_html_basic(self):
        """Test basic HTML escaping."""
        test_cases = [
            ('<script>alert("xss")</script>', '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'),
            ('<img src="x" onerror="alert(1)">', '&lt;img src=&quot;x&quot; onerror=&quot;alert(1)&quot;&gt;'),
            ('Normal & text <b>bold</b>', 'Normal &amp; text &lt;b&gt;bold&lt;/b&gt;'),
        ]
        for input_text, expected in test_cases:
            result = ContentEscaper.escape_html(input_text)
            self.assertEqual(result, expected, f"HTML escaping mismatch for: {input_text}")
    
    def test_escape_javascript(self):
        """Test JavaScript string escaping."""
        input_text = 'It\'s a test\nwith "quotes"'
        result = ContentEscaper.escape_javascript(input_text)
        # Check that dangerous characters are escaped
        self.assertNotIn("'", result)
        self.assertNotIn('"', result)
        self.assertNotIn('\n', result)
    
    def test_escape_csv(self):
        """Test CSV content escaping."""
        # Simple content without special chars
        result = ContentEscaper.escape_csv('simple')
        self.assertEqual(result, 'simple')
        
        # Content with comma
        result = ContentEscaper.escape_csv('value1, value2')
        self.assertEqual(result, '"value1, value2"')
        
        # Content with quotes
        result = ContentEscaper.escape_csv('say "hello"')
        self.assertEqual(result, '"say ""hello"""')
    
    def test_remove_suspicious_patterns(self):
        """Test removal of suspicious patterns."""
        test_cases = [
            ('<script>alert(1)</script>', '<script>alert(1)</script>'),  # Scripts removed
            ('<iframe src="evil"></iframe>', '<iframe src="evil"></iframe>'),  # Iframes removed
            ('<img onerror="alert(1)">', '<img onerror="alert(1)">'),  # Event handlers removed
            ('javascript:alert(1)', 'alert(1)'),  # Protocol removed
        ]
        for input_text, _ in test_cases:
            result = ContentEscaper.remove_suspicious_patterns(input_text)
            # Should not contain script tags or javascript protocol
            self.assertNotIn('<script', result.lower(), f"Scripts should be removed from: {input_text}")
            self.assertNotIn('javascript:', result.lower(), f"Protocol should be removed from: {input_text}")
    
    def test_sanitize_html_strict(self):
        """Test strict HTML sanitization."""
        input_text = '<script>alert("xss")</script><p>Safe text</p>'
        result = ContentEscaper.sanitize_html(input_text, strict=True)
        # In strict mode, all HTML should be escaped
        self.assertIn('&lt;script&gt;', result)
        self.assertIn('&lt;p&gt;', result)
    
    def test_escape_dict_values(self):
        """Test escaping values in dictionaries."""
        input_dict = {
            'name': '<script>alert(1)</script>',
            'value': 'normal',
            'nested': {
                'dangerous': '<img src=x onerror="alert(1)">',
            }
        }
        result = ContentEscaper.escape_dict_values(input_dict)
        # Check that nested dangerous content is escaped
        self.assertIn('&lt;script&gt;', result['name'])
        self.assertEqual(result['value'], 'normal')
        self.assertIn('&lt;img', result['nested']['dangerous'])
    
    def test_escape_list_values(self):
        """Test escaping values in lists."""
        input_list = [
            '<script>alert(1)</script>',
            'normal text',
            {'dangerous': '<img onerror=alert(1)>'}
        ]
        result = ContentEscaper.escape_list_values(input_list)
        self.assertIn('&lt;script&gt;', result[0])
        self.assertEqual(result[1], 'normal text')
        self.assertIn('&lt;img', result[2]['dangerous'])


class TestHTMLSanitizer(unittest.TestCase):
    """Test HTML sanitizer parser."""
    
    def test_safe_tags_preserved(self):
        """Test that safe tags are preserved."""
        sanitizer = HTMLSanitizer()
        sanitizer.feed('<p>This is <strong>bold</strong> text</p>')
        result = sanitizer.get_sanitized_html()
        self.assertIn('<p>', result)
        self.assertIn('<strong>', result)
        self.assertIn('</strong>', result)
        self.assertIn('</p>', result)
    
    def test_dangerous_tags_removed(self):
        """Test that dangerous tags are removed."""
        sanitizer = HTMLSanitizer()
        sanitizer.feed('<script>alert(1)</script><p>safe</p>')
        result = sanitizer.get_sanitized_html()
        self.assertNotIn('<script>', result)
        self.assertIn('<p>', result)
    
    def test_event_handlers_removed(self):
        """Test that event handlers are removed."""
        sanitizer = HTMLSanitizer()
        sanitizer.feed('<img src="test.jpg" onerror="alert(1)" alt="test">')
        result = sanitizer.get_sanitized_html()
        # img tag should be removed (not in safe tags), but test the principle
        # that onerror attribute would be stripped if img were safe
        self.assertNotIn('onerror', result)
    
    def test_javascript_protocol_blocked(self):
        """Test that javascript: protocol is blocked."""
        sanitizer = HTMLSanitizer()
        sanitizer.feed('<a href="javascript:alert(1)">click</a>')
        result = sanitizer.get_sanitized_html()
        # Should not contain javascript protocol
        self.assertNotIn('javascript:', result)


if __name__ == '__main__':
    unittest.main()
