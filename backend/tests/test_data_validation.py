"""
Tests for Data Validation & Quality system.

Tests data validation, quality scoring, grounding, and compliance services.
"""

import sys
import os
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.data_validator import (
    DataValidator, RequiredFieldRule, TypeRule, RangeRule, PatternRule,
    EMAIL_PATTERN, PHONE_PATTERN, DATE_PATTERN, AMOUNT_PATTERN
)
from shared.quality_scorer import QualityScorer, QualityLevel
from shared.grounding_service import GroundingService, GroundingLevel
from shared.compliance_service import ComplianceService, ComplianceLevel


class TestDataValidator(unittest.TestCase):
    """Test data validation."""
    
    def setUp(self):
        self.validator = DataValidator()
    
    def test_required_field_rule(self):
        """Test required field validation."""
        self.validator.add_rule("vendor", RequiredFieldRule("vendor"))
        
        # Valid data
        result = self.validator.validate({"vendor": "Acme Corp"})
        self.assertTrue(result["is_valid"])
        self.assertEqual(len(result["errors"]), 0)
        
        # Missing field
        result = self.validator.validate({"vendor": ""})
        self.assertFalse(result["is_valid"])
        self.assertEqual(len(result["errors"]), 1)
    
    def test_type_rule(self):
        """Test type validation."""
        self.validator.add_rule("amount", TypeRule("amount", float))
        
        # Valid type
        result = self.validator.validate({"amount": 100.50})
        self.assertTrue(result["is_valid"])
        
        # Invalid type
        result = self.validator.validate({"amount": "not_a_number"})
        self.assertFalse(result["is_valid"])
    
    def test_range_rule(self):
        """Test range validation."""
        self.validator.add_rule("amount", RangeRule("amount", min_val=0, max_val=1000000))
        
        # Valid range
        result = self.validator.validate({"amount": 500})
        self.assertTrue(result["is_valid"])
        
        # Below minimum
        result = self.validator.validate({"amount": -100})
        self.assertFalse(result["is_valid"])
        
        # Above maximum
        result = self.validator.validate({"amount": 2000000})
        self.assertFalse(result["is_valid"])
    
    def test_pattern_rule(self):
        """Test pattern validation."""
        self.validator.add_rule("email", PatternRule("email", EMAIL_PATTERN))
        
        # Valid email
        result = self.validator.validate({"email": "test@example.com"})
        self.assertTrue(result["is_valid"])
        
        # Invalid email
        result = self.validator.validate({"email": "invalid_email"})
        self.assertFalse(result["is_valid"])


class TestQualityScorer(unittest.TestCase):
    """Test quality scoring."""
    
    def setUp(self):
        self.scorer = QualityScorer()
    
    def test_completeness_scoring(self):
        """Test completeness scoring."""
        data = {"vendor": "Acme", "amount": 100}
        required = ["vendor", "amount", "date"]
        
        score = self.scorer.score_completeness(data, required)
        self.assertAlmostEqual(score, 2/3, places=2)
    
    def test_accuracy_scoring(self):
        """Test accuracy scoring."""
        data = {"vendor": "Acme", "amount": 100}
        validation_results = {"errors": []}
        
        score = self.scorer.score_accuracy(data, validation_results)
        self.assertEqual(score, 1.0)
    
    def test_consistency_scoring(self):
        """Test consistency scoring."""
        data = {"total": 100, "items": [{"amount": 50}, {"amount": 50}]}
        
        score = self.scorer.score_consistency(data)
        self.assertGreater(score, 0.8)
    
    def test_overall_score(self):
        """Test overall quality score."""
        data = {"vendor": "Acme", "amount": 100, "date": "2025-01-01"}
        validation_results = {"errors": []}
        required = ["vendor", "amount", "date"]
        
        result = self.scorer.calculate_overall_score(data, validation_results, required)
        
        self.assertIn("overall_score", result)
        self.assertIn("quality_level", result)
        self.assertGreater(result["overall_score"], 0.7)


class TestGroundingService(unittest.TestCase):
    """Test grounding service."""
    
    def setUp(self):
        self.service = GroundingService()
        self.service.add_known_vendor("Acme Corp")
        self.service.add_known_tax_id("1234567890")
    
    def test_ground_vendor(self):
        """Test vendor grounding."""
        # Known vendor
        is_grounded, confidence, msg = self.service.ground_vendor("Acme Corp")
        self.assertTrue(is_grounded)
        self.assertEqual(confidence, 1.0)
        
        # Unknown vendor
        is_grounded, confidence, msg = self.service.ground_vendor("Unknown Corp")
        self.assertFalse(is_grounded)
        self.assertLess(confidence, 0.5)
    
    def test_ground_tax_id(self):
        """Test tax ID grounding."""
        # Known tax ID
        is_grounded, confidence, msg = self.service.ground_tax_id("1234567890")
        self.assertTrue(is_grounded)
        self.assertEqual(confidence, 1.0)
    
    def test_ground_currency(self):
        """Test currency grounding."""
        # Valid currency
        is_grounded, confidence, msg = self.service.ground_currency("USD")
        self.assertTrue(is_grounded)
        self.assertEqual(confidence, 1.0)
        
        # Invalid currency
        is_grounded, confidence, msg = self.service.ground_currency("XXX")
        self.assertFalse(is_grounded)
    
    def test_ground_amount(self):
        """Test amount grounding."""
        # Valid amount
        is_grounded, confidence, msg = self.service.ground_amount(100.50)
        self.assertTrue(is_grounded)
        self.assertGreater(confidence, 0.8)
        
        # Invalid amount (negative)
        is_grounded, confidence, msg = self.service.ground_amount(-100)
        self.assertFalse(is_grounded)
    
    def test_ground_data(self):
        """Test data grounding."""
        data = {
            "vendor": "Acme Corp",
            "tax_id": "1234567890",
            "currency": "USD",
            "total": 100.50
        }
        
        result = self.service.ground_data(data)
        
        self.assertIn("is_grounded", result)
        self.assertIn("confidence", result)
        self.assertIn("grounding_level", result)
        self.assertGreater(result["confidence"], 0.7)


class TestComplianceService(unittest.TestCase):
    """Test compliance service."""
    
    def setUp(self):
        self.service = ComplianceService()
    
    def test_pmi_compliance(self):
        """Test PMI compliance checking."""
        data = {
            "project_name": "Project A",
            "project_scope": "Build system",
            "project_objectives": "Deliver on time",
            "stakeholders": ["Manager", "Team"],
            "schedule": "Q1 2025",
            "budget": 100000,
            "risks": ["Technical risk"],
            "quality_criteria": "95% uptime"
        }
        
        result = self.service.check_pmi_compliance(data)
        
        self.assertTrue(result["is_compliant"])
        self.assertGreater(result["score"], 0.9)
        self.assertEqual(len(result["missing_requirements"]), 0)
    
    def test_pmi_compliance_missing(self):
        """Test PMI compliance with missing requirements."""
        data = {
            "project_name": "Project A"
        }
        
        result = self.service.check_pmi_compliance(data)
        
        self.assertFalse(result["is_compliant"])
        self.assertLess(result["score"], 0.3)
        self.assertGreater(len(result["missing_requirements"]), 5)
    
    def test_bakok_compliance(self):
        """Test BABOK compliance checking."""
        data = {
            "business_need": "Improve efficiency",
            "stakeholder_analysis": "Done",
            "requirements": ["Req1", "Req2"],
            "acceptance_criteria": "Criteria",
            "solution_design": "Design doc",
            "traceability_matrix": "Matrix",
            "change_management": "Process"
        }
        
        result = self.service.check_babok_compliance(data)
        
        self.assertTrue(result["is_compliant"])
        self.assertGreater(result["score"], 0.9)


if __name__ == "__main__":
    unittest.main()

