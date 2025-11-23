"""
Grounding Service - Validates data against domain knowledge.

Implements grounding validation that checks extracted data against
known domain knowledge, business rules, and reference data.
Provides confidence scores for validation results.
"""

import logging
from typing import Dict, List, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class GroundingLevel(Enum):
    """Grounding confidence levels."""
    FULLY_GROUNDED = "FULLY_GROUNDED"        # 90-100%
    WELL_GROUNDED = "WELL_GROUNDED"          # 70-89%
    PARTIALLY_GROUNDED = "PARTIALLY_GROUNDED"  # 50-69%
    POORLY_GROUNDED = "POORLY_GROUNDED"      # 30-49%
    UNGROUNDED = "UNGROUNDED"                # 0-29%


class GroundingService:
    """Validates data against domain knowledge with confidence scoring."""
    
    def __init__(self):
        # Domain knowledge bases
        self.known_vendors = set()
        self.known_tax_ids = set()
        self.known_currencies = {"USD", "EUR", "GBP", "JPY", "CAD", "AUD"}
        self.known_countries = {"US", "DE", "FR", "UK", "JP", "CA", "AU"}
    
    def add_known_vendor(self, vendor_name: str):
        """Add a known vendor to the knowledge base."""
        self.known_vendors.add(vendor_name.lower())
    
    def add_known_tax_id(self, tax_id: str):
        """Add a known tax ID to the knowledge base."""
        self.known_tax_ids.add(tax_id)
    
    def ground_vendor(self, vendor_name: str) -> Tuple[bool, float, str]:
        """
        Ground vendor name against known vendors.
        
        Returns: (is_grounded, confidence, message)
        """
        if not vendor_name:
            return False, 0.0, "Vendor name is empty"
        
        vendor_lower = vendor_name.lower()
        
        # Exact match
        if vendor_lower in self.known_vendors:
            return True, 1.0, f"Vendor '{vendor_name}' is in knowledge base"
        
        # Partial match (at least 70% similarity)
        for known_vendor in self.known_vendors:
            if self._string_similarity(vendor_lower, known_vendor) > 0.7:
                return True, 0.8, f"Vendor '{vendor_name}' matches known vendor '{known_vendor}'"
        
        # Unknown vendor
        return False, 0.3, f"Vendor '{vendor_name}' is not in knowledge base"
    
    def ground_tax_id(self, tax_id: str) -> Tuple[bool, float, str]:
        """
        Ground tax ID against known tax IDs.
        
        Returns: (is_grounded, confidence, message)
        """
        if not tax_id:
            return False, 0.0, "Tax ID is empty"
        
        # Exact match
        if tax_id in self.known_tax_ids:
            return True, 1.0, f"Tax ID '{tax_id}' is in knowledge base"
        
        # Format validation (basic check)
        if len(tax_id) >= 10 and tax_id.isdigit():
            return True, 0.6, f"Tax ID '{tax_id}' has valid format"
        
        return False, 0.2, f"Tax ID '{tax_id}' has invalid format or is unknown"
    
    def ground_currency(self, currency_code: str) -> Tuple[bool, float, str]:
        """
        Ground currency code against known currencies.
        
        Returns: (is_grounded, confidence, message)
        """
        if not currency_code:
            return False, 0.0, "Currency code is empty"
        
        currency_upper = currency_code.upper()
        
        if currency_upper in self.known_currencies:
            return True, 1.0, f"Currency '{currency_upper}' is valid"
        
        return False, 0.1, f"Currency '{currency_upper}' is unknown"
    
    def ground_country(self, country_code: str) -> Tuple[bool, float, str]:
        """
        Ground country code against known countries.
        
        Returns: (is_grounded, confidence, message)
        """
        if not country_code:
            return False, 0.0, "Country code is empty"
        
        country_upper = country_code.upper()
        
        if country_upper in self.known_countries:
            return True, 1.0, f"Country '{country_upper}' is valid"
        
        return False, 0.1, f"Country '{country_upper}' is unknown"
    
    def ground_amount(self, amount: Any) -> Tuple[bool, float, str]:
        """
        Ground amount value (check if it's reasonable).
        
        Returns: (is_grounded, confidence, message)
        """
        try:
            amount_val = float(amount)
            
            # Check if amount is positive
            if amount_val <= 0:
                return False, 0.2, f"Amount {amount_val} is not positive"
            
            # Check if amount is reasonable (not too large)
            if amount_val > 1_000_000:
                return False, 0.4, f"Amount {amount_val} seems unusually large"
            
            # Check if amount is reasonable (not too small)
            if amount_val < 0.01:
                return False, 0.4, f"Amount {amount_val} seems unusually small"
            
            return True, 0.9, f"Amount {amount_val} is reasonable"
        
        except (ValueError, TypeError):
            return False, 0.0, f"Amount '{amount}' is not numeric"
    
    def ground_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ground all data fields against domain knowledge.
        
        Returns:
            {
                "is_grounded": bool,
                "confidence": 0.0-1.0,
                "grounding_level": str,
                "results": {
                    "field_name": {
                        "is_grounded": bool,
                        "confidence": 0.0-1.0,
                        "message": str
                    }
                },
                "issues": [{"field": str, "message": str}]
            }
        """
        results = {}
        issues = []
        confidence_scores = []
        
        # Ground vendor
        if "vendor" in data or "company" in data:
            vendor = data.get("vendor") or data.get("company")
            is_grounded, confidence, message = self.ground_vendor(vendor)
            results["vendor"] = {
                "is_grounded": is_grounded,
                "confidence": confidence,
                "message": message
            }
            confidence_scores.append(confidence)
            if not is_grounded:
                issues.append({"field": "vendor", "message": message})
        
        # Ground tax ID
        if "tax_id" in data or "vendor_tax_id" in data:
            tax_id = data.get("tax_id") or data.get("vendor_tax_id")
            is_grounded, confidence, message = self.ground_tax_id(tax_id)
            results["tax_id"] = {
                "is_grounded": is_grounded,
                "confidence": confidence,
                "message": message
            }
            confidence_scores.append(confidence)
            if not is_grounded:
                issues.append({"field": "tax_id", "message": message})
        
        # Ground currency
        if "currency" in data:
            is_grounded, confidence, message = self.ground_currency(data["currency"])
            results["currency"] = {
                "is_grounded": is_grounded,
                "confidence": confidence,
                "message": message
            }
            confidence_scores.append(confidence)
            if not is_grounded:
                issues.append({"field": "currency", "message": message})
        
        # Ground amount
        if "total" in data or "amount" in data:
            amount = data.get("total") or data.get("amount")
            is_grounded, confidence, message = self.ground_amount(amount)
            results["amount"] = {
                "is_grounded": is_grounded,
                "confidence": confidence,
                "message": message
            }
            confidence_scores.append(confidence)
            if not is_grounded:
                issues.append({"field": "amount", "message": message})
        
        # Calculate overall confidence
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Determine grounding level
        if overall_confidence >= 0.90:
            grounding_level = GroundingLevel.FULLY_GROUNDED
        elif overall_confidence >= 0.70:
            grounding_level = GroundingLevel.WELL_GROUNDED
        elif overall_confidence >= 0.50:
            grounding_level = GroundingLevel.PARTIALLY_GROUNDED
        elif overall_confidence >= 0.30:
            grounding_level = GroundingLevel.POORLY_GROUNDED
        else:
            grounding_level = GroundingLevel.UNGROUNDED
        
        return {
            "is_grounded": len(issues) == 0,
            "confidence": round(overall_confidence, 3),
            "grounding_level": grounding_level.value,
            "results": results,
            "issues": issues,
            "issue_count": len(issues)
        }
    
    @staticmethod
    def _string_similarity(a: str, b: str) -> float:
        """Calculate string similarity using simple algorithm."""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, a, b).ratio()

