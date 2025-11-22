# Phase 3: SROIE Model Integration

## Overview

Phase 3 integrates the SROIE baseline models (Task 2: CRNN OCR and Task 3: Bi-LSTM extraction) into the Grekonto project for comparison with Azure Document Intelligence.

## Architecture

### SROIE Task 3: Bi-LSTM Information Extraction

**Purpose**: Extract key fields (company, date, total, address) from receipt text using character-wise classification.

**Model**: 2-layer Bidirectional LSTM
- Input: Receipt text as character sequence
- Output: Classification labels for each character (5 classes: company, date, total, address, other)
- Framework: PyTorch

**Key Files**:
- `benchmark/SROIE/task3/src/my_models/__init__.py` - Model definition
- `benchmark/SROIE/task3/src/my_data.py` - Data loading and vocabulary
- `benchmark/SROIE/task3/src/my_utils.py` - Utility functions
- `benchmark/SROIE/task3/src/test.py` - Inference script

### SROIE Task 2: CRNN Text Recognition

**Purpose**: Recognize text lines from receipt images using CNN + RNN + CTC.

**Model**: CRNN (Convolutional Recurrent Neural Network)
- Input: Single-line text image
- Output: Recognized text
- Framework: PyTorch

**Note**: Requires bounding boxes from Task 1 (text detection)

## Implementation Status

### ✅ Completed
- [x] SROIE repository cloned to `benchmark/SROIE/`
- [x] Dataset verified (626 images with annotations)
- [x] Created `benchmark/sroie_models.py` wrapper module
- [x] Created `benchmark/compare_models.py` comparison script

### 🔄 In Progress
- [ ] Set up PyTorch environment
- [ ] Download pre-trained Task 3 model weights
- [ ] Implement Task 3 inference wrapper
- [ ] Test Task 3 on sample receipts
- [ ] Generate comparison metrics

### ⏳ Pending
- [ ] Download pre-trained Task 2 model weights
- [ ] Implement Task 2 inference wrapper
- [ ] Full end-to-end comparison
- [ ] Performance analysis and recommendations

## Setup Instructions

### 1. Create SROIE Environment

```bash
# Option A: Using conda
conda env create -f benchmark/SROIE/environment.yml
conda activate sroie

# Option B: Using pip
pip install torch torchvision opencv-python pillow numpy regex colorama
```

### 2. Download Pre-trained Models

**Task 3 Model**:
- Download from: [SROIE Task 3 Repository](https://github.com/patrick22414/sroie-task3)
- Place in: `benchmark/SROIE/task3/model.pth`

**Task 2 Model**:
- Download from: [SROIE Task 2 Repository](https://github.com/meijieru/crnn.pytorch)
- Place in: `benchmark/SROIE/task2/expr/model.pth`

### 3. Run Comparison

```bash
# Run Azure DI benchmark
python benchmark/test_azure_on_sroie.py 50

# Run SROIE models
python benchmark/run_sroie_models.py 50

# Generate comparison report
python benchmark/generate_comparison_report.py
```

## Expected Results

### Azure Document Intelligence
- Company accuracy: ~80%
- Date accuracy: ~20% (format mismatch)
- Total accuracy: ~40% (rounding errors)
- Address accuracy: ~0% (structured vs string)

### SROIE Baseline (from paper)
- Overall accuracy: 75.58%
- Company: ~85%
- Date: ~70%
- Total: ~80%
- Address: ~65%

## Next Steps

1. **Environment Setup**: Create conda environment with PyTorch
2. **Model Download**: Get pre-trained weights from SROIE repositories
3. **Inference Implementation**: Complete the wrapper functions
4. **Testing**: Run on 50-100 sample images
5. **Analysis**: Generate detailed comparison report
6. **Optimization**: Identify best approach for Grekonto

## References

- SROIE Dataset: https://github.com/zzzDavid/ICDAR-2019-SROIE
- Task 3 (Extraction): https://github.com/patrick22414/sroie-task3
- Task 2 (OCR): https://github.com/meijieru/crnn.pytorch

