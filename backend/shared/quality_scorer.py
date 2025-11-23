"""
Quality Scoring Service - Scores data quality and completeness.

Implements comprehensive quality scoring based on:
- Completeness (all required fields present)
- Accuracy (values match expected patterns)
- Consistency (values are logically consistent)
- Confidence (extraction confidence scores)
"""

import logging
from typing import Dict, List, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """Quality levels for scored data."""
    EXCELLENT = "EXCELLENT"  # 90-100%
    GOOD = "GOOD"             # 70-89%
    FAIR = "FAIR"             # 50-69%
    POOR = "POOR"             # 30-49%
    CRITICAL = "CRITICAL"     # 0-29%


class QualityScorer:
    """Scores data quality based on multiple dimensions."""
    
    def __init__(self):
        self.weights = {
            "completeness": 0.30,
            "accuracy": 0.30,
            "consistency": 0.20,
            "confidence": 0.20
        }
    
    def score_completeness(self, data: Dict[str, Any], required_fields: List[str]) -> float:
        """
        Score completeness: percentage of required fields present and non-empty.
        
        Returns: 0.0 to 1.0
        """
        if not required_fields:
            return 1.0
        
        present_count = 0
        for field in required_fields:
            value = data.get(field)
            if value is not None and (not isinstance(value, str) or value.strip()):
                present_count += 1
        
        return present_count / len(required_fields)
    
    def score_accuracy(self, data: Dict[str, Any], validation_results: Dict[str, Any]) -> float:
        """
        Score accuracy: percentage of fields that pass validation.
        
        Returns: 0.0 to 1.0
        """
        if not data:
            return 0.0
        
        total_fields = len(data)
        if total_fields == 0:
            return 1.0
        
        # Count fields without validation errors
        error_count = len(validation_results.get("errors", []))
        valid_fields = total_fields - error_count
        
        return max(0.0, valid_fields / total_fields)
    
    def score_consistency(self, data: Dict[str, Any]) -> float:
        """
        Score consistency: check for logical consistency between fields.
        
        Returns: 0.0 to 1.0
        """
        consistency_score = 1.0
        issues = 0
        total_checks = 0
        
        # Check: if total is present, it should be > 0
        if "total" in data and data["total"]:
            total_checks += 1
            try:
                total_val = float(data["total"])
                if total_val <= 0:
                    issues += 1
            except (ValueError, TypeError):
                pass
        
        # Check: if date is present, it should be valid
        if "date" in data and data["date"]:
            total_checks += 1
            try:
                from datetime import datetime
                datetime.strptime(str(data["date"]), "%Y-%m-%d")
            except (ValueError, TypeError):
                issues += 1
        
        # Check: if items are present, total should match sum
        if "items" in data and "total" in data:
            total_checks += 1
            try:
                items = data.get("items", [])
                if isinstance(items, list) and items:
                    items_sum = sum(float(item.get("amount", 0)) for item in items if item.get("amount"))
                    total_val = float(data["total"])
                    # Allow 5% tolerance for rounding
                    if abs(items_sum - total_val) > total_val * 0.05:
                        issues += 1
            except (ValueError, TypeError):
                pass
        
        if total_checks > 0:
            consistency_score = max(0.0, (total_checks - issues) / total_checks)
        
        return consistency_score
    
    def score_confidence(self, data: Dict[str, Any]) -> float:
        """
        Score confidence: average of extraction confidence scores.
        
        Returns: 0.0 to 1.0
        """
        if not data:
            return 0.0
        
        confidence_scores = []
        for key, value in data.items():
            if isinstance(value, dict) and "confidence" in value:
                confidence_scores.append(value["confidence"])
            elif key.endswith("_confidence"):
                try:
                    confidence_scores.append(float(value))
                except (ValueError, TypeError):
                    pass
        
        if not confidence_scores:
            return 0.5  # Default to neutral if no confidence data
        
        return sum(confidence_scores) / len(confidence_scores)
    
    def calculate_overall_score(
        self,
        data: Dict[str, Any],
        validation_results: Dict[str, Any],
        required_fields: List[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate overall quality score.
        
        Returns:
            {
                "overall_score": 0.0-1.0,
                "quality_level": QualityLevel,
                "scores": {
                    "completeness": 0.0-1.0,
                    "accuracy": 0.0-1.0,
                    "consistency": 0.0-1.0,
                    "confidence": 0.0-1.0
                },
                "issues": [{"dimension": str, "message": str}]
            }
        """
        if required_fields is None:
            required_fields = list(data.keys())
        
        # Calculate individual scores
        completeness = self.score_completeness(data, required_fields)
        accuracy = self.score_accuracy(data, validation_results)
        consistency = self.score_consistency(data)
        confidence = self.score_confidence(data)
        
        # Calculate weighted overall score
        overall_score = (
            completeness * self.weights["completeness"] +
            accuracy * self.weights["accuracy"] +
            consistency * self.weights["consistency"] +
            confidence * self.weights["confidence"]
        )
        
        # Determine quality level
        if overall_score >= 0.90:
            quality_level = QualityLevel.EXCELLENT
        elif overall_score >= 0.70:
            quality_level = QualityLevel.GOOD
        elif overall_score >= 0.50:
            quality_level = QualityLevel.FAIR
        elif overall_score >= 0.30:
            quality_level = QualityLevel.POOR
        else:
            quality_level = QualityLevel.CRITICAL
        
        # Identify issues
        issues = []
        if completeness < 0.80:
            issues.append({
                "dimension": "completeness",
                "message": f"Only {completeness*100:.0f}% of required fields are present"
            })
        if accuracy < 0.80:
            issues.append({
                "dimension": "accuracy",
                "message": f"Only {accuracy*100:.0f}% of fields pass validation"
            })
        if consistency < 0.80:
            issues.append({
                "dimension": "consistency",
                "message": "Data contains logical inconsistencies"
            })
        if confidence < 0.70:
            issues.append({
                "dimension": "confidence",
                "message": f"Extraction confidence is low ({confidence*100:.0f}%)"
            })
        
        return {
            "overall_score": round(overall_score, 3),
            "quality_level": quality_level.value,
            "scores": {
                "completeness": round(completeness, 3),
                "accuracy": round(accuracy, 3),
                "consistency": round(consistency, 3),
                "confidence": round(confidence, 3)
            },
            "issues": issues,
            "issue_count": len(issues)
        }

