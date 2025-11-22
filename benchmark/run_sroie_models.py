"""
Run SROIE Models on SROIE Dataset

This script runs the SROIE Task 3 (Bi-LSTM) model on the SROIE dataset
and generates results for comparison with Azure Document Intelligence.
"""

import sys
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


def find_sroie_data():
    """Find SROIE dataset."""
    paths = [
        Path("docs/datasets/SROIE_GitHub/data"),
        Path("benchmark/SROIE/data")
    ]
    
    for path in paths:
        if path.exists() and (path / "img").exists():
            return path
    
    return None


def check_prerequisites():
    """Check if all prerequisites are met."""
    logger.info("=" * 80)
    logger.info("SROIE MODELS - PREREQUISITE CHECK")
    logger.info("=" * 80)
    
    # Check data
    logger.info("\n📊 Checking SROIE dataset...")
    data_dir = find_sroie_data()
    if not data_dir:
        logger.error("✗ SROIE dataset not found!")
        return False
    logger.info(f"✓ Found SROIE data at: {data_dir}")
    
    # Check SROIE modules
    logger.info("\n🤖 Checking SROIE modules...")
    task3_path = Path("benchmark/SROIE/task3/src")
    if not task3_path.exists():
        logger.error("✗ SROIE Task 3 not found!")
        return False
    logger.info(f"✓ Found SROIE Task 3 at: {task3_path}")
    
    # Check model weights
    logger.info("\n⚖️ Checking pre-trained models...")
    model_path = Path("benchmark/SROIE/task3/model.pth")
    if not model_path.exists():
        logger.warning(f"⚠️ Model weights not found at: {model_path}")
        logger.warning("   Download from: https://github.com/patrick22414/sroie-task3")
        return False
    logger.info(f"✓ Found model weights at: {model_path}")
    
    # Check PyTorch
    logger.info("\n🔧 Checking PyTorch...")
    try:
        import torch
        logger.info(f"✓ PyTorch {torch.__version__} available")
        logger.info(f"  CUDA available: {torch.cuda.is_available()}")
    except ImportError:
        logger.error("✗ PyTorch not installed!")
        logger.error("  Install with: pip install torch torchvision")
        return False
    
    return True


def run_benchmark(sample_size: int = 50, start_id: int = 0):
    """Run SROIE models on dataset."""
    
    if not check_prerequisites():
        logger.error("\n✗ Prerequisites not met!")
        return False
    
    logger.info("\n" + "=" * 80)
    logger.info("SROIE MODELS - BENCHMARK")
    logger.info("=" * 80)
    
    try:
        from sroie_models import SROIETask3Model
        import torch
        
        # Initialize model
        logger.info(f"\n🚀 Initializing SROIE Task 3 model...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = SROIETask3Model(device=device)
        
        # Load weights
        logger.info(f"📥 Loading model weights...")
        if not model.load_model("benchmark/SROIE/task3/model.pth"):
            logger.error("✗ Failed to load model!")
            return False
        
        # Find data
        data_dir = find_sroie_data()
        img_dir = data_dir / "img"
        key_dir = data_dir / "key"
        
        # Get image list
        images = sorted(list(img_dir.glob("*.jpg")))[:sample_size]
        logger.info(f"\n📊 Testing {len(images)} images...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "model": "SROIE Task 3 (Bi-LSTM)",
            "total_images": len(images),
            "device": device,
            "results": []
        }
        
        # Process images
        for idx, img_path in enumerate(images):
            image_id = img_path.stem
            key_path = key_dir / f"{image_id}.json"
            
            if not key_path.exists():
                logger.warning(f"⚠️ Ground truth not found for {image_id}")
                continue
            
            # Load ground truth
            with open(key_path, 'r', encoding='utf-8') as f:
                ground_truth = json.load(f)
            
            # Run inference (placeholder)
            logger.info(f"  [{idx+1}/{len(images)}] Processing {image_id}...")
            
            result = {
                "image_id": image_id,
                "ground_truth": ground_truth,
                "predicted": {},
                "status": "pending"
            }
            
            results["results"].append(result)
        
        # Save results
        output_file = f"benchmark/results_sroie_task3_{len(images)}_{start_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n✓ Results saved to: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    sample_size = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    start_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    success = run_benchmark(sample_size, start_id)
    exit(0 if success else 1)


if __name__ == "__main__":
    main()

