# Data Validation & Quality - Complete Guide

**Projekt**: Grekonto AI Automatizáció  
**Verzió**: 1.0
**Utolsó frissítés**: 2025-11-23
**Commit**: TBD

## 🎯 Quick Start

### 1. Import Required Modules

```python
from shared.data_validator import DataValidator, RequiredFieldRule, RangeRule, PatternRule
from shared.quality_scorer import QualityScorer
from shared.grounding_service import GroundingService
from shared.compliance_service import ComplianceService
```

### 2. Validate Data

```python
# Create validator
validator = DataValidator()

# Add validation rules
validator.add_rule("vendor", RequiredFieldRule("vendor"))
validator.add_rule("amount", RangeRule("amount", min_val=0, max_val=1000000))
validator.add_rule("email", PatternRule("email", EMAIL_PATTERN))

# Validate data
data = {"vendor": "Acme Corp", "amount": 500, "email": "test@example.com"}
result = validator.validate(data)

if result["is_valid"]:
    print("✅ Data is valid")
else:
    print(f"❌ Validation errors: {result['errors']}")
```

### 3. Score Quality

```python
# Create scorer
scorer = QualityScorer()

# Calculate quality score
quality_result = scorer.calculate_overall_score(
    data=data,
    validation_results=result,
    required_fields=["vendor", "amount", "email"]
)

print(f"Quality Level: {quality_result['quality_level']}")
print(f"Overall Score: {quality_result['overall_score']}")
print(f"Issues: {quality_result['issues']}")
```

### 4. Ground Data

```python
# Create grounding service
grounding = GroundingService()

# Add known vendors
grounding.add_known_vendor("Acme Corp")
grounding.add_known_tax_id("1234567890")

# Ground data
grounding_result = grounding.ground_data(data)

print(f"Grounding Level: {grounding_result['grounding_level']}")
print(f"Confidence: {grounding_result['confidence']}")
```

### 5. Check Compliance

```python
# Create compliance service
compliance = ComplianceService()

# Check PMI compliance
pmi_result = compliance.check_pmi_compliance(project_data)
print(f"PMI Compliance: {pmi_result['compliance_level']}")
print(f"Gaps: {pmi_result['gaps']}")

# Check BABOK compliance
babok_result = compliance.check_babok_compliance(project_data)
print(f"BABOK Compliance: {babok_result['compliance_level']}")
```

## 🔄 Common Patterns

### Pattern 1: Complete Validation Pipeline

```python
def validate_and_score_invoice(invoice_data):
    # Step 1: Validate
    validator = DataValidator()
    validator.add_rule("vendor", RequiredFieldRule("vendor"))
    validator.add_rule("amount", RangeRule("amount", min_val=0, max_val=1000000))
    
    validation_result = validator.validate(invoice_data)
    if not validation_result["is_valid"]:
        return {"status": "INVALID", "errors": validation_result["errors"]}
    
    # Step 2: Score quality
    scorer = QualityScorer()
    quality_result = scorer.calculate_overall_score(
        invoice_data, validation_result, ["vendor", "amount"]
    )
    
    # Step 3: Ground data
    grounding = GroundingService()
    grounding_result = grounding.ground_data(invoice_data)
    
    return {
        "status": "VALID",
        "quality": quality_result,
        "grounding": grounding_result
    }
```

### Pattern 2: Quality-Based Routing

```python
def process_invoice(invoice_data):
    result = validate_and_score_invoice(invoice_data)
    
    if result["quality"]["quality_level"] == "EXCELLENT":
        # Auto-process
        return auto_process(invoice_data)
    elif result["quality"]["quality_level"] in ["GOOD", "FAIR"]:
        # Manual review
        return queue_for_review(invoice_data)
    else:
        # Reject
        return reject_invoice(invoice_data, result["quality"]["issues"])
```

### Pattern 3: Compliance Checking

```python
def validate_project(project_data):
    compliance = ComplianceService()
    
    pmi_result = compliance.check_pmi_compliance(project_data)
    babok_result = compliance.check_babok_compliance(project_data)
    
    if not pmi_result["is_compliant"]:
        print(f"PMI Gaps: {pmi_result['gaps']}")
        print(f"Recommendations: {pmi_result['recommendations']}")
    
    if not babok_result["is_compliant"]:
        print(f"BABOK Gaps: {babok_result['gaps']}")
        print(f"Recommendations: {babok_result['recommendations']}")
    
    return {
        "pmi_compliant": pmi_result["is_compliant"],
        "babok_compliant": babok_result["is_compliant"],
        "all_compliant": pmi_result["is_compliant"] and babok_result["is_compliant"]
    }
```

## 📊 Quality Levels

| Level | Score | Meaning | Action |
|-------|-------|---------|--------|
| EXCELLENT | 90-100% | High quality | Auto-process |
| GOOD | 70-89% | Acceptable | Review |
| FAIR | 50-69% | Questionable | Manual review |
| POOR | 30-49% | Low quality | Reject/Fix |
| CRITICAL | 0-29% | Very low | Reject |

## 🎯 Grounding Levels

| Level | Confidence | Meaning |
|-------|-----------|---------|
| FULLY_GROUNDED | 90-100% | All data verified |
| WELL_GROUNDED | 70-89% | Most data verified |
| PARTIALLY_GROUNDED | 50-69% | Some data verified |
| POORLY_GROUNDED | 30-49% | Little data verified |
| UNGROUNDED | 0-29% | No data verified |

## 🏆 Best Practices

1. **Always validate first** - Before scoring or grounding
2. **Use quality scores for routing** - Route based on quality level
3. **Ground against known data** - Build knowledge base over time
4. **Check compliance early** - Catch gaps before processing
5. **Log all validations** - For audit trail
6. **Monitor quality metrics** - Track trends over time
7. **Update rules regularly** - As business rules change
8. **Test edge cases** - Ensure robustness

---

## DOKUMENTÁCIÓ VERZIÓ ÉS FRISSÍTÉSI TÖRTÉNET

**Verzió:** 1.0  
**Utolsó frissítés:** 2025-11-23  
**Commit:** TBD

