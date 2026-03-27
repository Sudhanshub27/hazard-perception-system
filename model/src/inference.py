"""
ONNX Runtime Inference Wrapper — Phase 1 Skeleton
Full implementation in Phase 5 (after model training in Phase 3).

This module will:
  1. Load the best.onnx model into an ONNX Runtime InferenceSession
  2. Pre-process input frames (resize to 640x640, normalize)
  3. Run inference and return raw detections
  4. Post-process: apply NMS, map class IDs to names

WHY ONNX Runtime instead of PyTorch directly?
  - ONNX Runtime is ~30-40% faster than PyTorch for inference
  - No dependency on torch in production (smaller Docker image)
  - Provider priority: CUDA → DirectML → CPU (automatic fallback)
  - Standardized graph optimizations (operator fusion, quantization)
"""
import os
import numpy as np


# BDD100K class names — must match bdd100k.yaml order
CLASS_NAMES = [
    "car", "truck", "bus", "person", "rider",
    "bicycle", "motorcycle", "traffic light", "traffic sign", "train"
]


class YOLOInference:
    """
    Wrapper around ONNX Runtime for YOLO26 inference.
    Instantiated once at service startup and reused per request.
    """

    def __init__(self, model_path: str):
        # Placeholder — real implementation in Phase 5
        self.model_path = model_path
        self.session = None
        self.input_name = None
        self.is_loaded = False
        print(f"[YOLOInference] Skeleton initialized. Model path: {model_path}")
        print("[YOLOInference] Real loading implemented in Phase 5.")

    def load(self):
        """
        Load the ONNX model. Called once at service startup.
        Phase 5 implementation:
            import onnxruntime as ort
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            self.session = ort.InferenceSession(self.model_path, providers=providers)
            self.input_name = self.session.get_inputs()[0].name
            self.is_loaded = True
        """
        self.is_loaded = False  # Will be True after Phase 5

    def infer(self, frame: np.ndarray) -> list[dict]:
        """
        Run inference on a single BGR frame (OpenCV format).

        Args:
            frame: np.ndarray of shape (H, W, 3), dtype uint8

        Returns:
            List of detection dicts:
            [
              {
                "class_id": int,
                "class_name": str,
                "confidence": float,
                "bbox": [x1, y1, x2, y2]   # pixel coords in original frame
              },
              ...
            ]
        """
        if not self.is_loaded:
            # Return empty detections until Phase 5
            return []

        # Phase 5 implementation goes here
        raise NotImplementedError("Inference implemented in Phase 5")
