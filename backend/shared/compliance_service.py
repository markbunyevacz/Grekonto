"""
Compliance Service - Validates data against PMI/BABOK standards.

Implements compliance checking against project management and business
analysis standards with gap analysis and recommendations.
"""

import logging
from typing import Dict, List, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ComplianceStandard(Enum):
    """Compliance standards."""
    PMI = "PMI"              # Project Management Institute
    BABOK = "BABOK"          # Business Analysis Body of Knowledge
    ITIL = "ITIL"            # IT Infrastructure Library
    ISO = "ISO"              # International Organization for Standardization


class ComplianceLevel(Enum):
    """Compliance levels."""
    FULLY_COMPLIANT = "FULLY_COMPLIANT"        # 90-100%
    MOSTLY_COMPLIANT = "MOSTLY_COMPLIANT"      # 70-89%
    PARTIALLY_COMPLIANT = "PARTIALLY_COMPLIANT"  # 50-69%
    MINIMALLY_COMPLIANT = "MINIMALLY_COMPLIANT"  # 30-49%
    NON_COMPLIANT = "NON_COMPLIANT"            # 0-29%


class ComplianceService:
    """Validates data against compliance standards."""
    
    def __init__(self):
        self.pmi_requirements = self._init_pmi_requirements()
        self.babok_requirements = self._init_babok_requirements()
    
    def _init_pmi_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Initialize PMI requirements."""
        return {
            "project_name": {
                "required": True,
                "description": "Project must have a clear name",
                "category": "Scope"
            },
            "project_scope": {
                "required": True,
                "description": "Project scope must be defined",
                "category": "Scope"
            },
            "project_objectives": {
                "required": True,
                "description": "Project objectives must be documented",
                "category": "Scope"
            },
            "stakeholders": {
                "required": True,
                "description": "Stakeholders must be identified",
                "category": "Stakeholder Management"
            },
            "schedule": {
                "required": True,
                "description": "Project schedule must be defined",
                "category": "Schedule"
            },
            "budget": {
                "required": True,
                "description": "Project budget must be defined",
                "category": "Cost"
            },
            "risks": {
                "required": True,
                "description": "Project risks must be identified",
                "category": "Risk"
            },
            "quality_criteria": {
                "required": True,
                "description": "Quality criteria must be defined",
                "category": "Quality"
            }
        }
    
    def _init_babok_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Initialize BABOK requirements."""
        return {
            "business_need": {
                "required": True,
                "description": "Business need must be clearly stated",
                "category": "Business Analysis Planning"
            },
            "stakeholder_analysis": {
                "required": True,
                "description": "Stakeholder analysis must be completed",
                "category": "Stakeholder Analysis"
            },
            "requirements": {
                "required": True,
                "description": "Requirements must be documented",
                "category": "Requirements Analysis"
            },
            "acceptance_criteria": {
                "required": True,
                "description": "Acceptance criteria must be defined",
                "category": "Requirements Analysis"
            },
            "solution_design": {
                "required": True,
                "description": "Solution design must be documented",
                "category": "Solution Design"
            },
            "traceability_matrix": {
                "required": True,
                "description": "Traceability matrix must be maintained",
                "category": "Requirements Management"
            },
            "change_management": {
                "required": True,
                "description": "Change management process must be defined",
                "category": "Change Management"
            }
        }
    
    def check_pmi_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check PMI compliance.
        
        Returns:
            {
                "is_compliant": bool,
                "compliance_level": str,
                "score": 0.0-1.0,
                "met_requirements": [str],
                "missing_requirements": [str],
                "gaps": [{"requirement": str, "category": str, "recommendation": str}],
                "recommendations": [str]
            }
        """
        met = []
        missing = []
        gaps = []
        
        for req_name, req_info in self.pmi_requirements.items():
            if req_info["required"]:
                if req_name in data and data[req_name]:
                    met.append(req_name)
                else:
                    missing.append(req_name)
                    gaps.append({
                        "requirement": req_name,
                        "category": req_info["category"],
                        "description": req_info["description"],
                        "recommendation": f"Document {req_name} according to PMI standards"
                    })
        
        total_requirements = len(self.pmi_requirements)
        compliance_score = len(met) / total_requirements if total_requirements > 0 else 0.0
        
        # Determine compliance level
        if compliance_score >= 0.90:
            compliance_level = ComplianceLevel.FULLY_COMPLIANT
        elif compliance_score >= 0.70:
            compliance_level = ComplianceLevel.MOSTLY_COMPLIANT
        elif compliance_score >= 0.50:
            compliance_level = ComplianceLevel.PARTIALLY_COMPLIANT
        elif compliance_score >= 0.30:
            compliance_level = ComplianceLevel.MINIMALLY_COMPLIANT
        else:
            compliance_level = ComplianceLevel.NON_COMPLIANT
        
        recommendations = [
            f"Complete missing requirements: {', '.join(missing)}" if missing else None,
            "Ensure all requirements are documented and traceable" if len(gaps) > 3 else None,
            "Review PMI standards for best practices" if compliance_score < 0.7 else None
        ]
        recommendations = [r for r in recommendations if r]
        
        return {
            "is_compliant": compliance_score >= 0.7,
            "compliance_level": compliance_level.value,
            "score": round(compliance_score, 3),
            "met_requirements": met,
            "missing_requirements": missing,
            "gaps": gaps,
            "recommendations": recommendations,
            "gap_count": len(gaps)
        }
    
    def check_babok_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check BABOK compliance.
        
        Returns similar structure to check_pmi_compliance
        """
        met = []
        missing = []
        gaps = []
        
        for req_name, req_info in self.babok_requirements.items():
            if req_info["required"]:
                if req_name in data and data[req_name]:
                    met.append(req_name)
                else:
                    missing.append(req_name)
                    gaps.append({
                        "requirement": req_name,
                        "category": req_info["category"],
                        "description": req_info["description"],
                        "recommendation": f"Complete {req_name} according to BABOK standards"
                    })
        
        total_requirements = len(self.babok_requirements)
        compliance_score = len(met) / total_requirements if total_requirements > 0 else 0.0
        
        # Determine compliance level
        if compliance_score >= 0.90:
            compliance_level = ComplianceLevel.FULLY_COMPLIANT
        elif compliance_score >= 0.70:
            compliance_level = ComplianceLevel.MOSTLY_COMPLIANT
        elif compliance_score >= 0.50:
            compliance_level = ComplianceLevel.PARTIALLY_COMPLIANT
        elif compliance_score >= 0.30:
            compliance_level = ComplianceLevel.MINIMALLY_COMPLIANT
        else:
            compliance_level = ComplianceLevel.NON_COMPLIANT
        
        recommendations = [
            f"Complete missing requirements: {', '.join(missing)}" if missing else None,
            "Ensure all requirements are documented and traceable" if len(gaps) > 3 else None,
            "Review BABOK standards for best practices" if compliance_score < 0.7 else None
        ]
        recommendations = [r for r in recommendations if r]
        
        return {
            "is_compliant": compliance_score >= 0.7,
            "compliance_level": compliance_level.value,
            "score": round(compliance_score, 3),
            "met_requirements": met,
            "missing_requirements": missing,
            "gaps": gaps,
            "recommendations": recommendations,
            "gap_count": len(gaps)
        }

