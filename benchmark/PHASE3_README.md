# Phase 3: SROIE Model Integration - Implementation Guide

## 📋 Overview

Phase 3 integrates SROIE baseline models into Grekonto for benchmarking against Azure Document Intelligence.

## 🎯 Objectives

1. ✅ Set up PyTorch environment
2. ✅ Create SROIE models wrapper (`benchmark/sroie_models.py`)
3. ✅ Create comparison framework (`benchmark/compare_models.py`)
4. ⏳ Download pre-trained models
5. ⏳ Run inference on SROIE dataset
6. ⏳ Generate comparison report

## 📁 Files Created

### Core Implementation
- **`benchmark/sroie_models.py`** - SROIE models wrapper
  - `SROIETask3Model`: Bi-LSTM information extraction
  - `SROIEBenchmarkComparison`: Comparison framework

- **`benchmark/compare_models.py`** - Comparison orchestration script
  - Checks prerequisites
  - Validates data and credentials
  - Provides next steps

### Documentation
- **`benchmark/PHASE3_IMPLEMENTATION.md`** - Detailed implementation guide
- **`benchmark/PHASE3_README.md`** - This file

## 🚀 Quick Start

### 1. Set Up Environment

```bash
# Create conda environment
conda env create -f benchmark/SROIE/environment.yml
conda activate sroie

# Or use pip
pip install torch torchvision opencv-python pillow numpy regex colorama
```

### 2. Download Pre-trained Models

**Task 3 (Information Extraction)**:
```bash
# Download from SROIE Task 3 repository
# https://github.com/patrick22414/sroie-task3
# Place model.pth in: benchmark/SROIE/task3/model.pth
```

**Task 2 (Text Recognition)**:
```bash
# Download from SROIE Task 2 repository  
# https://github.com/meijieru/crnn.pytorch
# Place model.pth in: benchmark/SROIE/task2/expr/model.pth
```

### 3. Run Comparison

```bash
# Check prerequisites
python benchmark/compare_models.py

# Run Azure DI benchmark (already working)
python benchmark/test_azure_on_sroie.py 50

# Run SROIE models (when models are downloaded)
python benchmark/run_sroie_models.py 50
```

## 📊 Model Architecture

### Task 3: Bi-LSTM Information Extraction

```
Input Text
    ↓
Character Embedding
    ↓
Bidirectional LSTM (2 layers, 256 hidden)
    ↓
Classification (5 classes: company, date, total, address, other)
    ↓
Field Extraction
```

**Key Features**:
- Character-wise classification
- Bidirectional context
- 5-class output (4 fields + other)
- Simple and efficient

### Task 2: CRNN Text Recognition

```
Receipt Image
    ↓
CNN Feature Extraction
    ↓
Bidirectional RNN
    ↓
CTC Decoding
    ↓
Recognized Text
```

**Key Features**:
- Handles variable-length text
- CNN + RNN + CTC architecture
- Supports multi-word recognition

## 🔧 Implementation Details

### SROIETask3Model Class

```python
from benchmark.sroie_models import SROIETask3Model

# Initialize
model = SROIETask3Model(device="cpu")

# Load weights
model.load_model("benchmark/SROIE/task3/model.pth")

# Extract fields
result = model.extract_fields("BOOK TA K 25/12/2018 9.00 NO.53 JALAN SAGU")
# Returns: {"company": "BOOK TA K", "date": "25/12/2018", ...}
```

### Comparison Framework

```python
from benchmark.sroie_models import SROIEBenchmarkComparison

comparison = SROIEBenchmarkComparison(azure_client, sroie_model)
results = comparison.compare_on_dataset("docs/datasets/SROIE_GitHub/data", 50)
```

## 📈 Expected Performance

### Azure Document Intelligence
- Company: 80% accuracy
- Date: 20% accuracy (format issues)
- Total: 40% accuracy (rounding)
- Address: 0% accuracy (structure mismatch)

### SROIE Baseline (from paper)
- Overall: 75.58% accuracy
- Company: ~85%
- Date: ~70%
- Total: ~80%
- Address: ~65%

## ⚠️ Known Issues

1. **Python Environment**: Some issues with module imports in certain shells
2. **Model Weights**: Pre-trained models need to be downloaded separately
3. **Text Preprocessing**: Receipt text needs proper formatting before inference

## 🔗 References

- SROIE Dataset: https://github.com/zzzDavid/ICDAR-2019-SROIE
- Task 3 Repository: https://github.com/patrick22414/sroie-task3
- Task 2 Repository: https://github.com/meijieru/crnn.pytorch
- ICDAR 2019 Competition: https://rrc.cvc.uab.es/?ch=13

## 📝 Next Steps

1. Download pre-trained model weights
2. Complete inference implementation
3. Test on sample receipts
4. Generate comparison metrics
5. Create visualization dashboard
6. Document findings and recommendations

