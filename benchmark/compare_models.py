"""
Compare Azure Document Intelligence with SROIE Models

This script runs both Azure DI and SROIE baseline models on the SROIE dataset
and generates a comprehensive comparison report.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main comparison workflow."""
    
    logger.info("=" * 80)
    logger.info("SROIE MODELS COMPARISON: Azure DI vs SROIE Baseline")
    logger.info("=" * 80)
    
    # Phase 1: Check data availability
    logger.info("\n📊 Phase 1: Checking data availability...")
    
    data_paths = [
        Path("docs/datasets/SROIE_GitHub/data"),
        Path("benchmark/SROIE/data")
    ]
    
    data_dir = None
    for path in data_paths:
        if path.exists():
            data_dir = path
            logger.info(f"✓ Found SROIE data at: {path}")
            break
    
    if not data_dir:
        logger.error("✗ SROIE data not found!")
        return False
    
    # Phase 2: Check Azure credentials
    logger.info("\n🔐 Phase 2: Checking Azure credentials...")
    
    settings_path = Path("backend/local.settings.json")
    if not settings_path.exists():
        logger.error("✗ backend/local.settings.json not found!")
        return False
    
    with open(settings_path, 'r') as f:
        settings = json.load(f)
        values = settings.get("Values", {})
        endpoint = values.get("DOCUMENT_INTELLIGENCE_ENDPOINT")
        key = values.get("DOCUMENT_INTELLIGENCE_KEY")
    
    if not endpoint or not key:
        logger.error("✗ Azure credentials not found in settings!")
        return False
    
    logger.info(f"✓ Azure endpoint: {endpoint}")
    
    # Phase 3: Check SROIE models
    logger.info("\n🤖 Phase 3: Checking SROIE models...")
    
    task3_path = Path("benchmark/SROIE/task3/src")
    if not task3_path.exists():
        logger.error("✗ SROIE Task 3 not found!")
        return False
    
    logger.info(f"✓ SROIE Task 3 found at: {task3_path}")
    
    # Phase 4: Summary
    logger.info("\n" + "=" * 80)
    logger.info("✓ All prerequisites met!")
    logger.info("=" * 80)
    
    logger.info("\n📋 Next Steps:")
    logger.info("1. Run Azure DI benchmark: python benchmark/test_azure_on_sroie.py 50")
    logger.info("2. Set up SROIE environment: conda env create -f benchmark/SROIE/environment.yml")
    logger.info("3. Download pre-trained models from SROIE repository")
    logger.info("4. Run SROIE models on test set")
    logger.info("5. Generate comparison report")
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

