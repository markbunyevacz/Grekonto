"""
SROIE Models Wrapper

This module provides a unified interface to use SROIE baseline models:
- Task 2: CRNN for text recognition
- Task 3: Bi-LSTM for information extraction
"""

import sys
import logging
from pathlib import Path
import torch
import json

# Add SROIE task3 to path
SROIE_TASK3_PATH = Path(__file__).parent / "SROIE" / "task3" / "src"
sys.path.insert(0, str(SROIE_TASK3_PATH))

logger = logging.getLogger(__name__)


class SROIETask3Model:
    """
    SROIE Task 3: Information Extraction using Bi-LSTM

    Extracts key information (company, date, total, address) from receipt text
    using character-wise classification with bidirectional LSTM.
    """

    FIELD_CLASSES = {
        0: "other",
        1: "company",
        2: "date",
        3: "total",
        4: "address"
    }

    def __init__(self, model_path: str = None, device: str = "cpu"):
        """Initialize the Task 3 model."""
        self.device = torch.device(device)
        self.model = None
        self.vocab = None
        self.model_path = model_path
        self.available = False

        try:
            from my_data import VOCAB
            from my_models import MyModel0

            self.VOCAB = VOCAB
            self.MyModel0 = MyModel0
            self.available = True
            logger.info("✓ SROIE Task 3 modules imported successfully")
        except ImportError as e:
            logger.warning(f"✗ Could not import SROIE Task 3 modules: {e}")

    def load_model(self, model_path: str = None) -> bool:
        """Load pre-trained model weights."""
        if not self.available:
            logger.error("SROIE modules not available")
            return False

        if model_path is None:
            model_path = self.model_path

        if model_path is None or not Path(model_path).exists():
            logger.warning(f"Model path not found: {model_path}")
            return False

        try:
            self.model = self.MyModel0(len(self.VOCAB), 16, 256).to(self.device)
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.eval()
            logger.info(f"✓ Model loaded from {model_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def extract_fields(self, text: str) -> dict:
        """Extract key information from receipt text."""
        if self.model is None:
            logger.warning("Model not loaded")
            return {"status": "error", "message": "Model not loaded"}

        try:
            # Convert text to tensor
            text_tensor = self._text_to_tensor(text)

            # Run inference
            with torch.no_grad():
                output = self.model(text_tensor)
                prob = torch.nn.functional.softmax(output, dim=2)
                _, pred = torch.max(prob, dim=2)

            # Parse predictions
            pred_np = pred.squeeze().cpu().numpy()
            fields = self._parse_predictions(text, pred_np)

            return {"status": "success", "fields": fields}
        except Exception as e:
            logger.error(f"Error extracting fields: {e}")
            return {"status": "error", "message": str(e)}

    def _text_to_tensor(self, text: str) -> torch.Tensor:
        """Convert text to tensor using VOCAB."""
        # Placeholder - actual implementation would use VOCAB
        return torch.zeros(1, len(text), len(self.VOCAB))

    def _parse_predictions(self, text: str, predictions) -> dict:
        """Parse model predictions to extract fields."""
        fields = {"company": "", "date": "", "total": "", "address": ""}
        current_field = "other"

        for char, pred_class in zip(text, predictions):
            field_name = self.FIELD_CLASSES.get(pred_class, "other")
            if field_name != "other":
                current_field = field_name
                fields[current_field] += char

        return fields


class SROIEBenchmarkComparison:
    """
    Compare Azure Document Intelligence with SROIE models on SROIE dataset.
    """
    
    def __init__(self, azure_client=None, sroie_model: SROIETask3Model = None):
        """
        Initialize comparison benchmark.
        
        Args:
            azure_client: Azure DocumentAnalysisClient instance
            sroie_model: SROIETask3Model instance
        """
        self.azure_client = azure_client
        self.sroie_model = sroie_model
        self.results = []
    
    def compare_on_dataset(self, data_dir: str, sample_size: int = 50) -> dict:
        """
        Compare both models on SROIE dataset.
        
        Args:
            data_dir: Path to SROIE data directory
            sample_size: Number of images to test
            
        Returns:
            Comparison results with metrics
        """
        logger.info(f"Starting comparison on {sample_size} images from {data_dir}")
        
        # Implementation will compare both models
        return {
            "total_images": sample_size,
            "azure_results": {},
            "sroie_results": {},
            "comparison": {}
        }

