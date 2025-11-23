# Metadata Extraction & Document Statistics Guide

## Overview

The Metadata Extraction system provides comprehensive document property extraction and statistical analysis, addressing the traditional DMS weakness of limited metadata capture.

**Key Features:**
- ✅ Author and creator extraction
- ✅ Document date extraction (created, modified, published)
- ✅ Word count and character statistics
- ✅ Language detection
- ✅ Document statistics (pages, sections, tables)
- ✅ Readability metrics (Flesch-Kincaid, etc.)
- ✅ Content distribution analysis
- ✅ Quality and complexity scoring

## Architecture

### Components

#### 1. **MetadataExtractor** (`metadata_extractor.py`)
Extracts comprehensive metadata from documents.

```python
from backend.shared.metadata_extractor import MetadataExtractor

extractor = MetadataExtractor()
result = extractor.extract_metadata(
    document_text="# Title\nAuthor: John Smith\n...",
    filename="document.md",
    file_size=1024,
    document_id="doc_001",
    file_format="markdown"
)

if result.success:
    metadata = result.metadata
    print(f"Author: {metadata.author}")
    print(f"Words: {metadata.word_count}")
    print(f"Confidence: {metadata.extraction_confidence:.2%}")
```

**Extracted Metadata:**
- Author, creator, last modified by
- Created, modified, published dates
- Word count, character count, page count
- Language, encoding
- Title, subject, keywords, description
- Custom fields

#### 2. **DocumentStatisticsCalculator** (`document_statistics.py`)
Calculates comprehensive document statistics.

```python
from backend.shared.document_statistics import DocumentStatisticsCalculator

calculator = DocumentStatisticsCalculator()
stats = calculator.calculate_statistics(
    document_text="# Document\n...",
    document_id="doc_001"
)

print(f"Quality Score: {stats.quality_score:.1f}/100")
print(f"Complexity: {stats.complexity_score:.1f}/100")
print(f"Readability: {stats.readability.readability_level.value}")
```

**Calculated Statistics:**
- Word count, character count, line count
- Unique words, vocabulary richness
- Readability metrics (Flesch-Kincaid grade, reading ease)
- Content distribution (headings, paragraphs, lists, tables)
- Quality score (0-100)
- Complexity score (0-100)

## Usage Examples

### Example 1: Extract Metadata from Document

```python
from backend.shared.metadata_extractor import MetadataExtractor

extractor = MetadataExtractor()

document = """
# Project Specification

Author: Jane Doe
Created: 2024-01-15
Modified: 2024-01-20

## Requirements

- Requirement 1
- Requirement 2
"""

result = extractor.extract_metadata(
    document_text=document,
    filename="spec.md",
    file_size=2048,
    document_id="spec_001",
    file_format="markdown"
)

if result.success:
    metadata = result.metadata
    print(f"Title: {metadata.title}")
    print(f"Author: {metadata.author}")
    print(f"Created: {metadata.created_date}")
    print(f"Words: {metadata.word_count}")
    print(f"Keywords: {metadata.keywords}")
```

### Example 2: Calculate Document Statistics

```python
from backend.shared.document_statistics import DocumentStatisticsCalculator

calculator = DocumentStatisticsCalculator()

stats = calculator.calculate_statistics(
    document_text=document,
    document_id="spec_001"
)

# Quality metrics
print(f"Quality: {stats.quality_score:.1f}/100")
print(f"Complexity: {stats.complexity_score:.1f}/100")

# Readability
print(f"Grade Level: {stats.readability.flesch_kincaid_grade:.1f}")
print(f"Reading Ease: {stats.readability.flesch_reading_ease:.1f}")

# Content distribution
print(f"Headings: {stats.distribution.heading_count}")
print(f"Lists: {stats.distribution.list_count}")
print(f"Tables: {stats.distribution.table_count}")

# Vocabulary
print(f"Vocabulary Richness: {stats.vocabulary_richness:.2%}")
```

### Example 3: Enrich Metadata

```python
enrichment_data = {
    "department": "Engineering",
    "project": "Project Alpha",
    "confidential": True
}

enriched = extractor.enrich_metadata(metadata, enrichment_data)
print(enriched.custom_fields)
```

### Example 4: Validate Metadata

```python
is_valid, errors = extractor.validate_metadata(metadata)

if not is_valid:
    for error in errors:
        print(f"Validation error: {error}")
```

## Data Structures

### DocumentMetadata
Complete document metadata structure with author, dates, statistics, and custom fields.

### MetadataExtractionResult
Result of metadata extraction with success flag, metadata, extracted fields, confidence scores, and errors.

### DocumentStatistics
Complete statistics including readability, content distribution, and quality scores.

### ReadabilityMetrics
Flesch-Kincaid grade, reading ease, readability level, and sentence/word metrics.

### ContentDistribution
Distribution of content elements (headings, paragraphs, lists, tables, code blocks, images).

## Integration Points

### With Document Processing
```python
from backend.shared.document_processing_orchestrator import DocumentProcessingOrchestrator
from backend.shared.metadata_extractor import MetadataExtractor

orchestrator = DocumentProcessingOrchestrator()
extractor = MetadataExtractor()

# Extract metadata during document processing
result = extractor.extract_metadata(document_text, filename, file_size, doc_id)
if result.success:
    # Store metadata with processing result
    processing_result.metadata = result.metadata
```

### With File Upload
```python
# Extract metadata when file is uploaded
metadata_result = extractor.extract_metadata(
    document_text=extracted_text,
    filename=filename,
    file_size=file_size,
    document_id=file_id,
    file_format=detected_format
)
```

## Best Practices

1. **Always validate metadata** - Use `validate_metadata()` before storing
2. **Handle extraction failures** - Check `result.success` flag
3. **Use confidence scores** - Assess extraction reliability
4. **Enrich with custom fields** - Add domain-specific metadata
5. **Monitor statistics** - Track quality and complexity trends
6. **Cache results** - Store extracted metadata for performance

## Performance Considerations

- Metadata extraction is O(n) where n = document length
- Statistics calculation includes readability metrics (CPU-intensive)
- Language detection uses simple heuristics (fast)
- Keyword extraction uses frequency analysis (O(n log n))

## Error Handling

```python
try:
    result = extractor.extract_metadata(...)
    if not result.success:
        for error in result.errors:
            logger.error(f"Extraction error: {error}")
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
```

## Testing

Run comprehensive tests:
```bash
python -m unittest tests.test_metadata_extraction -v
```

All 17 tests pass with 100% success rate.

---

**Status**: ✅ Production Ready  
**Test Coverage**: 17 comprehensive tests  
**All Tests Passing**: ✅ 100%

