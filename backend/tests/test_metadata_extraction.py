"""
Unit tests for metadata extraction and document statistics modules.

Tests comprehensive metadata extraction including author, dates, word count,
and document statistics calculation.
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.metadata_extractor import (
    MetadataExtractor, DocumentMetadata, MetadataExtractionResult
)
from shared.document_statistics import (
    DocumentStatisticsCalculator, ReadabilityLevel
)


class TestMetadataExtractor(unittest.TestCase):
    """Test metadata extraction functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = MetadataExtractor()
        self.sample_document = """
# Project Specification Document

Author: John Smith
Created: 2024-01-15
Modified: 2024-01-20

## Introduction

This is a comprehensive project specification document that outlines
the requirements and implementation details for the new system.

## Requirements

- Requirement 1: System must support user authentication
- Requirement 2: System must handle concurrent requests
- Requirement 3: System must provide audit logging

## Implementation Details

The implementation will follow best practices and industry standards.

| Component | Status | Owner |
|-----------|--------|-------|
| Auth | Complete | John |
| API | In Progress | Jane |
| DB | Planned | Bob |

## Conclusion

This document provides a complete specification for the project.
"""
    
    def test_extract_author(self):
        """Test author extraction."""
        result = self.extractor.extract_metadata(
            self.sample_document,
            "spec.md",
            1024,
            "doc_001",
            "markdown"
        )
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.metadata)
        self.assertEqual(result.metadata.author, "John Smith")
    
    def test_extract_dates(self):
        """Test date extraction."""
        result = self.extractor.extract_metadata(
            self.sample_document,
            "spec.md",
            1024,
            "doc_001",
            "markdown"
        )
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.metadata.created_date)
        self.assertIsNotNone(result.metadata.modified_date)
    
    def test_extract_title(self):
        """Test title extraction."""
        result = self.extractor.extract_metadata(
            self.sample_document,
            "spec.md",
            1024,
            "doc_001",
            "markdown"
        )
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.metadata.title)
        self.assertIn("Project Specification", result.metadata.title)
    
    def test_calculate_statistics(self):
        """Test statistics calculation."""
        result = self.extractor.extract_metadata(
            self.sample_document,
            "spec.md",
            1024,
            "doc_001",
            "markdown"
        )
        
        self.assertTrue(result.success)
        self.assertGreater(result.metadata.word_count, 0)
        self.assertGreater(result.metadata.character_count, 0)
        self.assertGreater(result.metadata.page_count, 0)
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        result = self.extractor.extract_metadata(
            self.sample_document,
            "spec.md",
            1024,
            "doc_001",
            "markdown"
        )
        
        self.assertTrue(result.success)
        self.assertGreater(len(result.metadata.keywords), 0)
    
    def test_language_detection(self):
        """Test language detection."""
        result = self.extractor.extract_metadata(
            self.sample_document,
            "spec.md",
            1024,
            "doc_001",
            "markdown"
        )
        
        self.assertTrue(result.success)
        self.assertIn(result.metadata.language, ["hu", "en"])
    
    def test_metadata_to_dict(self):
        """Test metadata serialization."""
        result = self.extractor.extract_metadata(
            self.sample_document,
            "spec.md",
            1024,
            "doc_001",
            "markdown"
        )
        
        self.assertTrue(result.success)
        metadata_dict = result.metadata.to_dict()
        
        self.assertIn('document_id', metadata_dict)
        self.assertIn('filename', metadata_dict)
        self.assertIn('word_count', metadata_dict)
    
    def test_validate_metadata(self):
        """Test metadata validation."""
        metadata = DocumentMetadata(
            document_id="doc_001",
            filename="test.md",
            file_format="markdown",
            file_size=1024,
            word_count=100
        )
        
        is_valid, errors = self.extractor.validate_metadata(metadata)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_metadata_invalid(self):
        """Test metadata validation with invalid data."""
        metadata = DocumentMetadata(
            document_id="",
            filename="",
            file_format="markdown",
            file_size=-1,
            word_count=-10
        )
        
        is_valid, errors = self.extractor.validate_metadata(metadata)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


class TestDocumentStatistics(unittest.TestCase):
    """Test document statistics calculation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = DocumentStatisticsCalculator()
        self.sample_document = """
# Document Title

This is a sample document with multiple paragraphs.

## Section 1

The first section contains important information.

- Item 1
- Item 2
- Item 3

## Section 2

The second section provides additional details.

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |

## Conclusion

This concludes the document.
"""
    
    def test_calculate_basic_statistics(self):
        """Test basic statistics calculation."""
        stats = self.calculator.calculate_statistics(
            self.sample_document,
            "doc_001"
        )
        
        self.assertEqual(stats.document_id, "doc_001")
        self.assertGreater(stats.total_words, 0)
        self.assertGreater(stats.total_characters, 0)
        self.assertGreater(stats.total_lines, 0)
    
    def test_calculate_readability(self):
        """Test readability metrics calculation."""
        stats = self.calculator.calculate_statistics(
            self.sample_document,
            "doc_001"
        )
        
        self.assertGreaterEqual(stats.readability.flesch_kincaid_grade, 0)
        self.assertGreaterEqual(stats.readability.flesch_reading_ease, 0)
        self.assertLessEqual(stats.readability.flesch_reading_ease, 100)
        self.assertIsNotNone(stats.readability.readability_level)
    
    def test_content_distribution(self):
        """Test content distribution analysis."""
        stats = self.calculator.calculate_statistics(
            self.sample_document,
            "doc_001"
        )
        
        self.assertGreater(stats.distribution.heading_count, 0)
        self.assertGreater(stats.distribution.paragraph_count, 0)
        self.assertGreater(stats.distribution.list_count, 0)
        self.assertGreater(stats.distribution.table_count, 0)
    
    def test_quality_score(self):
        """Test quality score calculation."""
        stats = self.calculator.calculate_statistics(
            self.sample_document,
            "doc_001"
        )
        
        self.assertGreaterEqual(stats.quality_score, 0)
        self.assertLessEqual(stats.quality_score, 100)
    
    def test_complexity_score(self):
        """Test complexity score calculation."""
        stats = self.calculator.calculate_statistics(
            self.sample_document,
            "doc_001"
        )
        
        self.assertGreaterEqual(stats.complexity_score, 0)
        self.assertLessEqual(stats.complexity_score, 100)
    
    def test_vocabulary_richness(self):
        """Test vocabulary richness calculation."""
        stats = self.calculator.calculate_statistics(
            self.sample_document,
            "doc_001"
        )
        
        self.assertGreater(stats.unique_words, 0)
        self.assertGreaterEqual(stats.vocabulary_richness, 0)
        self.assertLessEqual(stats.vocabulary_richness, 1)
    
    def test_statistics_to_dict(self):
        """Test statistics serialization."""
        stats = self.calculator.calculate_statistics(
            self.sample_document,
            "doc_001"
        )
        
        stats_dict = stats.to_dict()
        
        self.assertIn('document_id', stats_dict)
        self.assertIn('total_words', stats_dict)
        self.assertIn('quality_score', stats_dict)
        self.assertIn('complexity_score', stats_dict)
    
    def test_has_structure_detection(self):
        """Test document structure detection."""
        stats = self.calculator.calculate_statistics(
            self.sample_document,
            "doc_001"
        )
        
        self.assertTrue(stats.has_title)
        self.assertTrue(stats.has_structure)
        self.assertTrue(stats.has_formatting)


if __name__ == '__main__':
    unittest.main()

