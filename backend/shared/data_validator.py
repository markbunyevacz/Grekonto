"""
Data Validation Service - Validates content against domain knowledge.

Implements comprehensive data validation with specific rules for different
data types and domains. Provides detailed validation results with error messages.
"""

import logging
import re
from typing import Dict, List, Tuple, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ValidationRule:
    """Base class for validation rules."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def validate(self, value: Any) -> Tuple[bool, str]:
        """Validate value. Returns (is_valid, error_message)."""
        raise NotImplementedError


class RequiredFieldRule(ValidationRule):
    """Validates that a field is present and not empty."""
    
    def __init__(self, field_name: str):
        super().__init__(f"required_{field_name}", f"Field '{field_name}' is required")
        self.field_name = field_name
    
    def validate(self, value: Any) -> Tuple[bool, str]:
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, f"Field '{self.field_name}' is required and cannot be empty"
        return True, ""


class TypeRule(ValidationRule):
    """Validates that a value is of the correct type."""
    
    def __init__(self, field_name: str, expected_type: type):
        super().__init__(f"type_{field_name}", f"Field '{field_name}' must be {expected_type.__name__}")
        self.field_name = field_name
        self.expected_type = expected_type
    
    def validate(self, value: Any) -> Tuple[bool, str]:
        if not isinstance(value, self.expected_type):
            return False, f"Field '{self.field_name}' must be {self.expected_type.__name__}, got {type(value).__name__}"
        return True, ""


class RangeRule(ValidationRule):
    """Validates that a numeric value is within a range."""
    
    def __init__(self, field_name: str, min_val: float = None, max_val: float = None):
        super().__init__(f"range_{field_name}", f"Field '{field_name}' must be in range")
        self.field_name = field_name
        self.min_val = min_val
        self.max_val = max_val
    
    def validate(self, value: Any) -> Tuple[bool, str]:
        try:
            num_val = float(value)
            if self.min_val is not None and num_val < self.min_val:
                return False, f"Field '{self.field_name}' must be >= {self.min_val}"
            if self.max_val is not None and num_val > self.max_val:
                return False, f"Field '{self.field_name}' must be <= {self.max_val}"
            return True, ""
        except (ValueError, TypeError):
            return False, f"Field '{self.field_name}' must be numeric"


class PatternRule(ValidationRule):
    """Validates that a value matches a regex pattern."""
    
    def __init__(self, field_name: str, pattern: str, description: str = ""):
        super().__init__(f"pattern_{field_name}", description or f"Field '{field_name}' format invalid")
        self.field_name = field_name
        self.pattern = pattern
    
    def validate(self, value: Any) -> Tuple[bool, str]:
        if not re.match(self.pattern, str(value)):
            return False, f"Field '{self.field_name}' format is invalid"
        return True, ""


class DataValidator:
    """Validates data against a set of rules."""
    
    def __init__(self):
        self.rules: Dict[str, List[ValidationRule]] = {}
    
    def add_rule(self, field_name: str, rule: ValidationRule):
        """Add a validation rule for a field."""
        if field_name not in self.rules:
            self.rules[field_name] = []
        self.rules[field_name].append(rule)
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data against all rules.
        
        Returns:
            {
                "is_valid": bool,
                "errors": [{"field": str, "message": str}],
                "warnings": [{"field": str, "message": str}],
                "validated_data": dict
            }
        """
        errors = []
        warnings = []
        validated_data = {}
        
        for field_name, field_rules in self.rules.items():
            value = data.get(field_name)
            validated_data[field_name] = value
            
            for rule in field_rules:
                is_valid, error_msg = rule.validate(value)
                if not is_valid:
                    errors.append({
                        "field": field_name,
                        "rule": rule.name,
                        "message": error_msg
                    })
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "validated_data": validated_data,
            "error_count": len(errors),
            "warning_count": len(warnings)
        }


# Common validation patterns
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PHONE_PATTERN = r'^\+?1?\d{9,15}$'
DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}$'
AMOUNT_PATTERN = r'^\d+(\.\d{2})?$'
INVOICE_ID_PATTERN = r'^[A-Z0-9\-]{3,20}$'
TAX_ID_PATTERN = r'^\d{10,12}$'

