import numpy as np
import cv2
from ultralytics import YOLO

CLASS_NAMES = [
    "car", "truck", "bus", "person", "rider",
    "bicycle", "motorcycle", "traffic light", "traffic sign", "train"
]

class YOLOInference:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.is_loaded = False

    def load(self):
        print(f"Loading YOLO model from {self.model_path}...")
        try:
            import torch
            # PyTorch 2.6+ added strict weights_only=True which breaks .pt model loading.
            # We temporarily whitelist the ultralytics model class to allow loading.
            if self.model_path.endswith('.pt'):
                try:
                    from ultralytics.nn.tasks import DetectionModel
                    # Allow ultralytics model loading in PyTorch 2.6+
                    with torch.serialization.safe_open if hasattr(torch.serialization, 'safe_open') else (lambda *a, **k: __import__('contextlib').nullcontext()):
                        pass
                    torch.serialization.add_safe_globals([DetectionModel])
                except Exception:
                    pass
            # task='detect' prevents ultralytics from guessing for ONNX
            task = 'detect' if self.model_path.endswith('.onnx') else None
            if task:
                self.model = YOLO(self.model_path, task=task)
            else:
                self.model = YOLO(self.model_path)
            self.is_loaded = True
            print(f"✅ Model loaded! Classes: {len(self.model.names)} | Path: {self.model_path}")
            print(f"   Class map: {self.model.names}")
        except Exception as e:
            print(f"CRITICAL: Failed to load model at {self.model_path}: {e}")
            self.is_loaded = False

    def infer(self, frame: np.ndarray) -> list[dict]:
        if not self.is_loaded:
            return []

        # Confidence threshold: 0.35 is well-tuned for real vehicle detection.
        # 0.1 generates too much noise; 0.5 misses partially-occluded objects.
        # iou=0.45 is the standard COCO benchmark NMS overlap threshold.
        results = self.model(frame, conf=0.35, iou=0.45, verbose=False)
        
        detections = []
        if len(results) > 0:
            boxes = results[0].boxes
            if boxes is not None and len(boxes) > 0:
                names = self.model.names  # can be 10 (BDD100K) or 80 (COCO)
                for box in boxes:
                    class_id = int(box.cls[0].item())
                    confidence = float(box.conf[0].item())
                    x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
                    class_name = names.get(class_id, f"object_{class_id}")
                    
                    detections.append({
                        "class_id": class_id,
                        "class_name": class_name,
                        "confidence": confidence,
                        "bbox": [x1, y1, x2, y2]
                    })

        return detections
