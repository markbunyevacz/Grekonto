"""
Comprehensive metadata extraction module for documents.

Extracts document properties including author, dates, word count, statistics,
and other document metadata to provide complete document context.

Features:
- Author and creator extraction
- Document date extraction (created, modified, published)
- Word count and character statistics
- Language detection
- Document statistics (pages, sections, tables)
- Custom metadata fields
- Metadata validation and enrichment
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class MetadataType(Enum):
    """Types of metadata that can be extracted."""
    AUTHOR = "AUTHOR"
    CREATED_DATE = "CREATED_DATE"
    MODIFIED_DATE = "MODIFIED_DATE"
    PUBLISHED_DATE = "PUBLISHED_DATE"
    WORD_COUNT = "WORD_COUNT"
    CHARACTER_COUNT = "CHARACTER_COUNT"
    PAGE_COUNT = "PAGE_COUNT"
    LANGUAGE = "LANGUAGE"
    ENCODING = "ENCODING"
    FILE_SIZE = "FILE_SIZE"
    FILE_FORMAT = "FILE_FORMAT"
    TITLE = "TITLE"
    SUBJECT = "SUBJECT"
    KEYWORDS = "KEYWORDS"
    DESCRIPTION = "DESCRIPTION"
    CUSTOM = "CUSTOM"


@dataclass
class DocumentMetadata:
    """Complete document metadata structure."""
    document_id: str
    filename: str
    file_format: str
    file_size: int
    
    # Author information
    author: Optional[str] = None
    creator: Optional[str] = None
    last_modified_by: Optional[str] = None
    
    # Date information
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    published_date: Optional[datetime] = None
    
    # Content statistics
    word_count: int = 0
    character_count: int = 0
    page_count: int = 0
    section_count: int = 0
    table_count: int = 0
    image_count: int = 0
    
    # Language and encoding
    language: str = "hu"  # Default to Hungarian
    encoding: str = "utf-8"
    
    # Document properties
    title: Optional[str] = None
    subject: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    description: Optional[str] = None
    
    # Custom metadata
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    # Extraction metadata
    extraction_timestamp: datetime = field(default_factory=datetime.utcnow)
    extraction_confidence: float = 0.0
    extraction_method: str = "regex"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        for key in ['created_date', 'modified_date', 'published_date', 'extraction_timestamp']:
            if data[key]:
                data[key] = data[key].isoformat()
        return data


@dataclass
class MetadataExtractionResult:
    """Result of metadata extraction operation."""
    success: bool
    metadata: Optional[DocumentMetadata] = None
    extracted_fields: Dict[str, Any] = field(default_factory=dict)
    missing_fields: List[str] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class MetadataExtractor:
    """Extracts comprehensive metadata from documents."""
    
    def __init__(self):
        """Initialize metadata extractor."""
        self.date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{1,2}\.\d{1,2}\.\d{4}',  # DD.MM.YYYY
            r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',
        ]
        
        self.author_patterns = [
            r'(?:Author|By|Written by|Created by):\s*([A-Za-z\s]+)',
            r'(?:Author|By|Written by|Created by)\s+([A-Za-z\s]+)',
        ]
        
        self.title_patterns = [
            r'^#\s+(.+)$',  # Markdown H1
            r'<h1>(.+?)</h1>',  # HTML H1
            r'(?:Title|Subject):\s*(.+)',
        ]
    
    def extract_metadata(self, document_text: str, filename: str, 
                        file_size: int, document_id: str,
                        file_format: str = "text",
                        additional_metadata: Optional[Dict] = None) -> MetadataExtractionResult:
        """
        Extract comprehensive metadata from document.
        
        Args:
            document_text: Full document text
            filename: Original filename
            file_size: File size in bytes
            document_id: Unique document identifier
            file_format: Document format (text, pdf, docx, etc.)
            additional_metadata: Additional metadata to include
            
        Returns:
            MetadataExtractionResult with extracted metadata
        """
        logger.info(f"Extracting metadata from document: {document_id}")
        
        try:
            metadata = DocumentMetadata(
                document_id=document_id,
                filename=filename,
                file_format=file_format,
                file_size=file_size,
            )
            
            extracted_fields = {}
            confidence_scores = {}
            
            # Extract author
            author, author_conf = self._extract_author(document_text)
            if author:
                metadata.author = author
                extracted_fields['author'] = author
                confidence_scores['author'] = author_conf
            
            # Extract dates
            dates = self._extract_dates(document_text)
            if dates.get('created'):
                metadata.created_date = dates['created']
                extracted_fields['created_date'] = dates['created']
                confidence_scores['created_date'] = 0.8
            if dates.get('modified'):
                metadata.modified_date = dates['modified']
                extracted_fields['modified_date'] = dates['modified']
                confidence_scores['modified_date'] = 0.8
            
            # Extract title
            title, title_conf = self._extract_title(document_text)
            if title:
                metadata.title = title
                extracted_fields['title'] = title
                confidence_scores['title'] = title_conf
            
            # Calculate statistics
            stats = self._calculate_statistics(document_text)
            metadata.word_count = stats['word_count']
            metadata.character_count = stats['character_count']
            metadata.page_count = stats['page_count']
            metadata.section_count = stats['section_count']
            metadata.table_count = stats['table_count']
            metadata.image_count = stats['image_count']
            extracted_fields.update(stats)
            
            # Extract keywords
            keywords = self._extract_keywords(document_text)
            metadata.keywords = keywords
            extracted_fields['keywords'] = keywords
            
            # Detect language
            language = self._detect_language(document_text)
            metadata.language = language
            extracted_fields['language'] = language
            
            # Add additional metadata
            if additional_metadata:
                metadata.custom_fields.update(additional_metadata)
                extracted_fields.update(additional_metadata)
            
            # Set extraction metadata
            metadata.extraction_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.0
            
            logger.info(f"Extracted metadata for {document_id}: "
                       f"words={metadata.word_count}, "
                       f"pages={metadata.page_count}, "
                       f"confidence={metadata.extraction_confidence:.2%}")
            
            return MetadataExtractionResult(
                success=True,
                metadata=metadata,
                extracted_fields=extracted_fields,
                confidence_scores=confidence_scores,
            )
        
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return MetadataExtractionResult(
                success=False,
                errors=[str(e)],
            )
    
    def _extract_author(self, text: str) -> Tuple[Optional[str], float]:
        """Extract author information from document."""
        for pattern in self.author_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                author = match.group(1).strip()
                # Clean up author name - remove extra content
                author = author.split('\n')[0].strip()
                if author and len(author) < 100 and len(author.split()) <= 5:
                    return author, 0.85
        return None, 0.0
    
    def _extract_dates(self, text: str) -> Dict[str, Optional[datetime]]:
        """Extract date information from document."""
        dates = {'created': None, 'modified': None}
        
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    # Try to parse the first match as created date
                    if not dates['created']:
                        dates['created'] = datetime.fromisoformat(matches[0])
                    # Use last match as modified date
                    if len(matches) > 1:
                        dates['modified'] = datetime.fromisoformat(matches[-1])
                except (ValueError, AttributeError):
                    continue
        
        return dates
    
    def _extract_title(self, text: str) -> Tuple[Optional[str], float]:
        """Extract document title."""
        for pattern in self.title_patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                title = match.group(1).strip()
                if title and len(title) < 200:
                    return title, 0.9
        return None, 0.0
    
    def _calculate_statistics(self, text: str) -> Dict[str, int]:
        """Calculate document statistics."""
        words = text.split()
        word_count = len(words)
        character_count = len(text)
        page_count = max(1, character_count // 2500)  # Estimate: ~2500 chars per page
        
        # Count sections (headings)
        section_count = len(re.findall(r'^#+\s+', text, re.MULTILINE))
        
        # Count tables
        table_count = len(re.findall(r'\|.*\|', text))
        
        # Count images
        image_count = len(re.findall(r'!\[.*?\]\(.*?\)', text))
        
        return {
            'word_count': word_count,
            'character_count': character_count,
            'page_count': page_count,
            'section_count': section_count,
            'table_count': table_count,
            'image_count': image_count,
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from document."""
        # Simple keyword extraction: common words
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top 10 keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:10]]
    
    def _detect_language(self, text: str) -> str:
        """Detect document language."""
        # Simple language detection based on common words
        hungarian_words = ['a', 'az', 'és', 'hogy', 'van', 'nem', 'de', 'vagy']
        english_words = ['the', 'and', 'is', 'that', 'to', 'of', 'in', 'for']
        
        text_lower = text.lower()
        hungarian_count = sum(1 for word in hungarian_words if word in text_lower)
        english_count = sum(1 for word in english_words if word in text_lower)
        
        return "hu" if hungarian_count > english_count else "en"
    
    def enrich_metadata(self, metadata: DocumentMetadata, 
                       enrichment_data: Dict[str, Any]) -> DocumentMetadata:
        """Enrich existing metadata with additional information."""
        for key, value in enrichment_data.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)
            else:
                metadata.custom_fields[key] = value
        
        return metadata
    
    def validate_metadata(self, metadata: DocumentMetadata) -> Tuple[bool, List[str]]:
        """Validate extracted metadata."""
        errors = []
        
        if not metadata.document_id:
            errors.append("document_id is required")
        if not metadata.filename:
            errors.append("filename is required")
        if metadata.file_size <= 0:
            errors.append("file_size must be positive")
        if metadata.word_count < 0:
            errors.append("word_count cannot be negative")
        
        return len(errors) == 0, errors

