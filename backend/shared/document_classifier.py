"""
Document Classification and Categorization Module.

Advanced classification system for intelligent document routing and processing:
- Multi-label classification
- Confidence scoring
- Automatic routing rules
- Custom training data support
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ClassificationConfidence(Enum):
    """Confidence levels for classification."""
    HIGH = 0.8
    MEDIUM = 0.6
    LOW = 0.4


@dataclass
class ClassificationResult:
    """Result of document classification."""
    primary_category: str
    secondary_categories: List[Tuple[str, float]]
    confidence_score: float
    classification_timestamp: str
    keywords_matched: List[str]
    routing_rules_triggered: List[str]


class DocumentClassifier:
    """
    Multi-level document classifier with confidence scoring and automatic routing.
    
    Features:
    - Keyword-based classification
    - Pattern matching
    - Confidence scoring
    - Automatic routing
    - Custom classification rules
    """
    
    def __init__(self):
        """Initialize classifier with built-in category definitions."""
        self.categories = self._define_categories()
        self.routing_rules = self._define_routing_rules()
    
    def _define_categories(self) -> Dict[str, Dict[str, any]]:
        """Define document categories with keywords and patterns."""
        return {
            "INVOICE": {
                "keywords": [
                    "invoice", "számla", "szamla", "invoice number", "invoice id",
                    "bill", "billing", "vendor", "vendor name", "total amount",
                    "due date", "payment", "pénz", "szerződés", "ár", "egységár"
                ],
                "patterns": [
                    r"INV-\d+", r"SZ\d{4,}", r"#\d{8,}", r"\d+\s*Ft\b"
                ],
                "weight": 1.0
            },
            "RECEIPT": {
                "keywords": [
                    "receipt", "nyugta", "acquittance", "payment received",
                    "received", "confirmed", "thank you", "transact", "checkout"
                ],
                "patterns": [
                    r"REC-\d+", r"RCPT\d+", r"paid.*\d{4}", r"total.*\d+"
                ],
                "weight": 0.9
            },
            "CONTRACT": {
                "keywords": [
                    "agreement", "contract", "szerződés", "szerzodes", "terms",
                    "conditions", "party", "effective", "term", "term end",
                    "signature", "sign", "clause", "provision", "liability"
                ],
                "patterns": [
                    r"CONTRACT\s*#\d+", r"AGREEMENT\s*#\d+", r"Parties:\s*\n",
                    r"Effective\s*Date:"
                ],
                "weight": 0.95
            },
            "SPECIFICATION": {
                "keywords": [
                    "specification", "spec", "requirement", "functional", "non-functional",
                    "acceptance", "criteria", "test", "scenario", "given", "when",
                    "then", "user story", "use case", "feature", "story", "epic"
                ],
                "patterns": [
                    r"(?:Given|When|Then)\s+", r"As\s+a\s+", r"I\s+want\s+to",
                    r"Acceptance\s+Criteria:", r"Definition\s+of\s+Done:"
                ],
                "weight": 0.9
            },
            "REPORT": {
                "keywords": [
                    "report", "analysis", "summary", "findings", "conclusion",
                    "executive", "metric", "dashboard", "overview", "status",
                    "performance", "trend", "benchmark", "statistical", "data"
                ],
                "patterns": [
                    r"(?:Daily|Weekly|Monthly|Annual)\s+Report", r"Status\s+Report",
                    r"Project\s+Report", r"Q\d\s+Report"
                ],
                "weight": 0.85
            },
            "EMAIL": {
                "keywords": [
                    "to:", "from:", "subject:", "cc:", "bcc:", "dear", "regards",
                    "sincerely", "best", "hello", "hi", "message", "body"
                ],
                "patterns": [
                    r"^From:\s+", r"^To:\s+", r"^Subject:\s+",
                    r"^Date:\s+\d{1,2}/\d{1,2}/\d{4}"
                ],
                "weight": 0.8
            },
            "LETTER": {
                "keywords": [
                    "letter", "correspondence", "dear", "sir", "madam",
                    "yours", "truly", "faithfully", "recipient", "address"
                ],
                "patterns": [
                    r"^[A-Za-z\s]+,\s*$", r"Dear\s+[A-Za-z\s]+,",
                    r"Yours\s+(?:sincerely|faithfully)"
                ],
                "weight": 0.75
            },
            "FORM": {
                "keywords": [
                    "form", "field", "input", "checkbox", "radio", "dropdown",
                    "required", "optional", "fill", "submit", "application",
                    "registration", "questionnaire"
                ],
                "patterns": [
                    r"\[\s*\]\s+", r"\(o\)\s+", r"___+\s*", r"Form\s+#"
                ],
                "weight": 0.8
            },
            "TECHNICAL": {
                "keywords": [
                    "api", "endpoint", "parameter", "response", "request",
                    "authentication", "authorization", "error", "exception",
                    "debug", "log", "trace", "code", "implementation"
                ],
                "patterns": [
                    r"GET\s+/", r"POST\s+/", r"HTTP/\d\.\d", r"JSON", r"XML",
                    r"```python", r"```javascript", r"import\s+"
                ],
                "weight": 0.85
            },
            "FINANCIAL": {
                "keywords": [
                    "budget", "revenue", "expense", "cost", "profit", "loss",
                    "asset", "liability", "equity", "cash", "statement",
                    "balance", "income", "forecast", "projection"
                ],
                "patterns": [
                    r"\$\s*\d+,?\d+", r"€\s*\d+", r"HUF\s*\d+",
                    r"Financial\s+Report", r"P&L"
                ],
                "weight": 0.85
            },
            "LEGAL": {
                "keywords": [
                    "legal", "law", "statute", "regulation", "compliance",
                    "copyright", "trademark", "patent", "liability", "lawsuit",
                    "jurisdiction", "governing", "court"
                ],
                "patterns": [
                    r"Section\s+\d+", r"Article\s+\d+", r"Paragraph\s+\d+",
                    r"Copyright\s+©"
                ],
                "weight": 0.9
            }
        }
    
    def _define_routing_rules(self) -> Dict[str, List[Dict]]:
        """Define routing rules based on classification."""
        return {
            "INVOICE": [
                {
                    "condition": "confidence > 0.9",
                    "route": "auto_processing",
                    "priority": "HIGH"
                },
                {
                    "condition": "confidence < 0.6",
                    "route": "manual_review",
                    "priority": "MEDIUM"
                }
            ],
            "SPECIFICATION": [
                {
                    "condition": "confidence > 0.8",
                    "route": "requirement_analysis",
                    "priority": "HIGH"
                },
                {
                    "condition": "contains acceptance_criteria",
                    "route": "ticket_generation",
                    "priority": "HIGH"
                }
            ],
            "CONTRACT": [
                {
                    "condition": "always",
                    "route": "legal_review",
                    "priority": "CRITICAL"
                }
            ],
            "EMAIL": [
                {
                    "condition": "contains attachment",
                    "route": "extract_attachment",
                    "priority": "MEDIUM"
                }
            ]
        }
    
    def classify(self, text: str, document_type_hint: Optional[str] = None) -> ClassificationResult:
        """
        Classify document with confidence scoring.
        
        Args:
            text: Document text to classify
            document_type_hint: Optional hint about document type
            
        Returns:
            ClassificationResult with primary and secondary categories
        """
        import re
        from datetime import datetime
        
        logger.info("Classifying document")
        
        text_lower = text.lower()
        scores = {}
        matched_keywords = {}
        
        # Score each category
        for category, definition in self.categories.items():
            score = 0.0
            keywords_found = []
            
            # Keyword matching
            for keyword in definition["keywords"]:
                if keyword.lower() in text_lower:
                    score += 0.1
                    keywords_found.append(keyword)
            
            # Pattern matching
            for pattern in definition["patterns"]:
                matches = len(re.findall(pattern, text, re.IGNORECASE | re.MULTILINE))
                score += matches * 0.15
            
            # Boost score if type hint matches
            if document_type_hint and document_type_hint.upper() == category:
                score *= 1.5
            
            # Apply category weight
            score *= definition["weight"]
            
            # Cap at 1.0
            score = min(score, 1.0)
            
            scores[category] = score
            matched_keywords[category] = keywords_found
        
        # Get sorted results
        sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_category = sorted_categories[0][0]
        primary_score = sorted_categories[0][1]
        
        # Secondary categories
        secondary_categories = [
            (cat, score) for cat, score in sorted_categories[1:]
            if score > ClassificationConfidence.LOW.value
        ]
        
        # Get routing rules
        routing_triggered = self._check_routing_rules(
            primary_category, primary_score, matched_keywords[primary_category]
        )
        
        result = ClassificationResult(
            primary_category=primary_category,
            secondary_categories=secondary_categories,
            confidence_score=primary_score,
            classification_timestamp=datetime.utcnow().isoformat(),
            keywords_matched=matched_keywords[primary_category][:10],
            routing_rules_triggered=routing_triggered,
        )
        
        logger.info(f"Classification complete: {primary_category} (confidence: {primary_score:.2%})")
        
        return result
    
    def _check_routing_rules(self, category: str, confidence: float,
                            keywords: List[str]) -> List[str]:
        """Check which routing rules are triggered."""
        triggered = []
        
        if category not in self.routing_rules:
            return triggered
        
        for rule in self.routing_rules[category]:
            condition = rule.get("condition", "")
            
            if ">" in condition and "confidence" in condition:
                threshold = float(condition.split(">")[1].strip())
                if confidence > threshold:
                    triggered.append(rule.get("route", ""))
            elif condition == "always":
                triggered.append(rule.get("route", ""))
            elif "contains" in condition:
                keyword = condition.split("contains")[1].strip()
                if any(keyword.lower() in kw.lower() for kw in keywords):
                    triggered.append(rule.get("route", ""))
        
        return triggered
    
    def get_classification_confidence_level(self, score: float) -> str:
        """Get confidence level name from score."""
        if score >= ClassificationConfidence.HIGH.value:
            return "HIGH"
        elif score >= ClassificationConfidence.MEDIUM.value:
            return "MEDIUM"
        else:
            return "LOW"


def get_document_classifier() -> DocumentClassifier:
    """Get or create global document classifier."""
    return DocumentClassifier()
