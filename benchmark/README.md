# Grekonto OCR Benchmark

This directory contains benchmarking tools to compare different OCR solutions for invoice processing.

## Overview

We benchmark the following solutions:
1. **Azure Document Intelligence** (prebuilt-invoice model) - Current production solution
2. **SROIE Baseline Models** (CTPN + CRNN + Bi-LSTM) - Academic baseline from ICDAR 2019

## Dataset

**SROIE (Scanned Receipts OCR and Information Extraction)**
- Source: ICDAR 2019 Competition
- Repository: [zzzDavid/ICDAR-2019-SROIE](https://github.com/zzzDavid/ICDAR-2019-SROIE)
- Size: 626 scanned receipt images with annotations
- Fields: company, date, total, address

## Setup

### 1. Install Dependencies

```bash
# Backend dependencies (already installed)
cd backend
pip install -r requirements.txt

# Additional dependencies for SROIE models (if needed)
cd ../benchmark/SROIE
conda env create -f environment.yml
conda activate sroie
```

### 2. Configure Azure Credentials

Set environment variables in `backend/local.settings.json`:

```json
{
  "Values": {
    "DOCUMENT_INTELLIGENCE_ENDPOINT": "https://grekonto.cognitiveservices.azure.com/",
    "DOCUMENT_INTELLIGENCE_KEY": "your-key-here"
  }
}
```

Or export them:

```bash
export DOCUMENT_INTELLIGENCE_ENDPOINT="https://grekonto.cognitiveservices.azure.com/"
export DOCUMENT_INTELLIGENCE_KEY="your-key-here"
```

## Running Benchmarks

### Azure Document Intelligence Benchmark

Test Azure's prebuilt-invoice model on SROIE dataset:

```bash
# Test first 50 images
python benchmark/test_azure_on_sroie.py 50

# Test first 100 images
python benchmark/test_azure_on_sroie.py 100

# Test images 100-150
python benchmark/test_azure_on_sroie.py 50 100

# Test all images (626) - WARNING: This will take time and cost money!
python benchmark/test_azure_on_sroie.py 626
```

**Output:**
- Console: Real-time progress and summary
- File: `benchmark/results_azure_sroie_{sample_size}_{start_id}.json`

**Example Output:**
```
================================================================================
AZURE DOCUMENT INTELLIGENCE - SROIE BENCHMARK RESULTS
================================================================================
Total Images Tested: 50
Successful: 48
Errors: 2
--------------------------------------------------------------------------------
Company Name Accuracy: 85.42%
Date Accuracy: 91.67%
Total Amount Accuracy: 93.75%
Address Accuracy: 72.92%
--------------------------------------------------------------------------------
Exact Match Rate (all fields): 68.75%
================================================================================
```

### SROIE Baseline Models Benchmark

(To be implemented in Phase 3)

```bash
# Run SROIE baseline models
cd benchmark/SROIE
python task2/main.py  # OCR
python task3/src/main.py  # Key Information Extraction
```

## Metrics

We measure the following metrics:

1. **Field-level Accuracy**: Percentage of correctly extracted fields
   - Company Name
   - Date
   - Total Amount
   - Address

2. **Exact Match Rate**: Percentage of receipts where ALL fields are correct

3. **Error Rate**: Percentage of failed processing attempts

## Comparison

| Solution | Company | Date | Total | Address | Exact Match | Notes |
|----------|---------|------|-------|---------|-------------|-------|
| Azure DI | TBD | TBD | TBD | TBD | TBD | Prebuilt-invoice model |
| SROIE Baseline | 75.58% | - | - | - | 75.58% | From paper (Task 3) |

## Cost Considerations

**Azure Document Intelligence Pricing:**
- Free Tier: 500 pages/month
- Standard: $1.50 per 1000 pages

**Recommendations:**
- Start with small samples (50-100 images)
- Use free tier for development
- Full benchmark (626 images) costs ~$0.94

## Next Steps

- [ ] Run Azure benchmark on 50 images
- [ ] Analyze results and identify failure cases
- [ ] Set up SROIE baseline models (Phase 3)
- [ ] Compare Azure vs. SROIE baseline
- [ ] Document findings and recommendations

## References

- [ICDAR 2019 SROIE Competition](https://rrc.cvc.uab.es/?ch=13)
- [Azure Document Intelligence Documentation](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/)
- [SROIE GitHub Repository](https://github.com/zzzDavid/ICDAR-2019-SROIE)

