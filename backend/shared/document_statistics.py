"""
Document statistics and analysis module.

Provides comprehensive statistical analysis of documents including
readability metrics, content distribution, and quality indicators.

Features:
- Readability scoring (Flesch-Kincaid, etc.)
- Content distribution analysis
- Complexity metrics
- Quality indicators
- Comparative statistics
"""

import logging
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ReadabilityLevel(Enum):
    """Readability levels based on Flesch-Kincaid grade."""
    VERY_EASY = "VERY_EASY"  # Grade 0-3
    EASY = "EASY"  # Grade 4-6
    MEDIUM = "MEDIUM"  # Grade 7-9
    DIFFICULT = "DIFFICULT"  # Grade 10-12
    VERY_DIFFICULT = "VERY_DIFFICULT"  # Grade 13+


@dataclass
class ReadabilityMetrics:
    """Readability analysis metrics."""
    flesch_kincaid_grade: float = 0.0
    flesch_reading_ease: float = 0.0
    readability_level: ReadabilityLevel = ReadabilityLevel.MEDIUM
    average_sentence_length: float = 0.0
    average_word_length: float = 0.0
    syllable_count: int = 0
    sentence_count: int = 0


@dataclass
class ContentDistribution:
    """Content distribution analysis."""
    headings_percentage: float = 0.0
    paragraphs_percentage: float = 0.0
    lists_percentage: float = 0.0
    tables_percentage: float = 0.0
    code_blocks_percentage: float = 0.0
    images_percentage: float = 0.0
    
    heading_count: int = 0
    paragraph_count: int = 0
    list_count: int = 0
    table_count: int = 0
    code_block_count: int = 0
    image_count: int = 0


@dataclass
class DocumentStatistics:
    """Complete document statistics."""
    document_id: str
    
    # Basic counts
    total_words: int = 0
    total_characters: int = 0
    total_lines: int = 0
    total_paragraphs: int = 0
    
    # Content elements
    unique_words: int = 0
    vocabulary_richness: float = 0.0  # unique_words / total_words
    
    # Readability
    readability: ReadabilityMetrics = field(default_factory=ReadabilityMetrics)
    
    # Content distribution
    distribution: ContentDistribution = field(default_factory=ContentDistribution)
    
    # Quality indicators
    has_title: bool = False
    has_structure: bool = False
    has_formatting: bool = False
    quality_score: float = 0.0
    
    # Complexity
    complexity_score: float = 0.0  # 0-100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'document_id': self.document_id,
            'total_words': self.total_words,
            'total_characters': self.total_characters,
            'total_lines': self.total_lines,
            'total_paragraphs': self.total_paragraphs,
            'unique_words': self.unique_words,
            'vocabulary_richness': self.vocabulary_richness,
            'readability': {
                'flesch_kincaid_grade': self.readability.flesch_kincaid_grade,
                'flesch_reading_ease': self.readability.flesch_reading_ease,
                'readability_level': self.readability.readability_level.value,
                'average_sentence_length': self.readability.average_sentence_length,
                'average_word_length': self.readability.average_word_length,
            },
            'distribution': {
                'headings_percentage': self.distribution.headings_percentage,
                'paragraphs_percentage': self.distribution.paragraphs_percentage,
                'lists_percentage': self.distribution.lists_percentage,
                'tables_percentage': self.distribution.tables_percentage,
            },
            'quality_score': self.quality_score,
            'complexity_score': self.complexity_score,
        }


class DocumentStatisticsCalculator:
    """Calculates comprehensive document statistics."""
    
    def __init__(self):
        """Initialize calculator."""
        self.vowels = set('aeiououáéíóöőüűAEIOUÓÖŐÜŰ')
    
    def calculate_statistics(self, document_text: str, 
                            document_id: str) -> DocumentStatistics:
        """
        Calculate comprehensive statistics for document.
        
        Args:
            document_text: Full document text
            document_id: Document identifier
            
        Returns:
            DocumentStatistics with all metrics
        """
        logger.info(f"Calculating statistics for document: {document_id}")
        
        stats = DocumentStatistics(document_id=document_id)
        
        # Basic counts
        stats.total_characters = len(document_text)
        stats.total_lines = len(document_text.split('\n'))
        
        words = document_text.split()
        stats.total_words = len(words)
        stats.unique_words = len(set(word.lower() for word in words))
        stats.vocabulary_richness = stats.unique_words / max(stats.total_words, 1)
        
        # Paragraphs
        stats.total_paragraphs = len([p for p in document_text.split('\n\n') if p.strip()])
        
        # Readability metrics
        stats.readability = self._calculate_readability(document_text, words)
        
        # Content distribution
        stats.distribution = self._analyze_content_distribution(document_text)
        
        # Quality indicators
        stats.has_title = bool(re.search(r'^#+\s+', document_text, re.MULTILINE))
        stats.has_structure = stats.distribution.heading_count > 0
        stats.has_formatting = bool(re.search(r'[*_`\[\]()|-]', document_text)) or stats.distribution.table_count > 0
        
        # Quality score (0-100)
        stats.quality_score = self._calculate_quality_score(stats)
        
        # Complexity score (0-100)
        stats.complexity_score = self._calculate_complexity_score(stats)
        
        logger.info(f"Statistics calculated: words={stats.total_words}, "
                   f"quality={stats.quality_score:.1f}, "
                   f"complexity={stats.complexity_score:.1f}")
        
        return stats
    
    def _calculate_readability(self, text: str, words: List[str]) -> ReadabilityMetrics:
        """Calculate readability metrics."""
        metrics = ReadabilityMetrics()
        
        # Sentence count
        sentences = re.split(r'[.!?]+', text)
        metrics.sentence_count = len([s for s in sentences if s.strip()])
        
        # Average sentence length
        metrics.average_sentence_length = len(words) / max(metrics.sentence_count, 1)
        
        # Average word length
        metrics.average_word_length = sum(len(w) for w in words) / max(len(words), 1)
        
        # Syllable count
        metrics.syllable_count = sum(self._count_syllables(word) for word in words)
        
        # Flesch-Kincaid Grade
        if metrics.sentence_count > 0 and len(words) > 0:
            metrics.flesch_kincaid_grade = (
                0.39 * metrics.average_sentence_length +
                11.8 * (metrics.syllable_count / max(len(words), 1)) - 15.59
            )
            metrics.flesch_kincaid_grade = max(0, metrics.flesch_kincaid_grade)
        
        # Flesch Reading Ease
        if metrics.sentence_count > 0 and len(words) > 0:
            metrics.flesch_reading_ease = (
                206.835 - 1.015 * metrics.average_sentence_length -
                84.6 * (metrics.syllable_count / max(len(words), 1))
            )
            metrics.flesch_reading_ease = max(0, min(100, metrics.flesch_reading_ease))
        
        # Determine readability level
        if metrics.flesch_kincaid_grade < 3:
            metrics.readability_level = ReadabilityLevel.VERY_EASY
        elif metrics.flesch_kincaid_grade < 6:
            metrics.readability_level = ReadabilityLevel.EASY
        elif metrics.flesch_kincaid_grade < 9:
            metrics.readability_level = ReadabilityLevel.MEDIUM
        elif metrics.flesch_kincaid_grade < 12:
            metrics.readability_level = ReadabilityLevel.DIFFICULT
        else:
            metrics.readability_level = ReadabilityLevel.VERY_DIFFICULT
        
        return metrics
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word."""
        word = word.lower()
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in self.vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent e
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _analyze_content_distribution(self, text: str) -> ContentDistribution:
        """Analyze content distribution."""
        dist = ContentDistribution()
        
        # Count elements
        dist.heading_count = len(re.findall(r'^#+\s+', text, re.MULTILINE))
        dist.paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        dist.list_count = len(re.findall(r'^\s*[-*•]\s+', text, re.MULTILINE))
        dist.table_count = len(re.findall(r'\|.*\|', text))
        dist.code_block_count = len(re.findall(r'```', text))
        dist.image_count = len(re.findall(r'!\[.*?\]\(.*?\)', text))
        
        # Calculate percentages
        total_elements = (dist.heading_count + dist.paragraph_count + 
                         dist.list_count + dist.table_count + 
                         dist.code_block_count + dist.image_count)
        
        if total_elements > 0:
            dist.headings_percentage = (dist.heading_count / total_elements) * 100
            dist.paragraphs_percentage = (dist.paragraph_count / total_elements) * 100
            dist.lists_percentage = (dist.list_count / total_elements) * 100
            dist.tables_percentage = (dist.table_count / total_elements) * 100
            dist.code_blocks_percentage = (dist.code_block_count / total_elements) * 100
            dist.images_percentage = (dist.image_count / total_elements) * 100
        
        return dist
    
    def _calculate_quality_score(self, stats: DocumentStatistics) -> float:
        """Calculate overall quality score (0-100)."""
        score = 0.0
        
        # Has title (10 points)
        if stats.has_title:
            score += 10
        
        # Has structure (15 points)
        if stats.has_structure:
            score += 15
        
        # Has formatting (10 points)
        if stats.has_formatting:
            score += 10
        
        # Vocabulary richness (20 points)
        score += min(20, stats.vocabulary_richness * 100)
        
        # Readability (25 points)
        if stats.readability.readability_level in [ReadabilityLevel.EASY, ReadabilityLevel.MEDIUM]:
            score += 25
        elif stats.readability.readability_level == ReadabilityLevel.DIFFICULT:
            score += 15
        
        # Content distribution (20 points)
        if stats.distribution.heading_count > 0:
            score += 10
        if stats.distribution.list_count > 0:
            score += 10
        
        return min(100, score)
    
    def _calculate_complexity_score(self, stats: DocumentStatistics) -> float:
        """Calculate document complexity (0-100)."""
        score = 0.0
        
        # Readability difficulty (40 points)
        grade = stats.readability.flesch_kincaid_grade
        score += min(40, (grade / 16) * 40)
        
        # Vocabulary richness (30 points)
        score += stats.vocabulary_richness * 30
        
        # Content diversity (30 points)
        element_types = sum([
            1 if stats.distribution.heading_count > 0 else 0,
            1 if stats.distribution.list_count > 0 else 0,
            1 if stats.distribution.table_count > 0 else 0,
            1 if stats.distribution.code_block_count > 0 else 0,
        ])
        score += (element_types / 4) * 30
        
        return min(100, score)

