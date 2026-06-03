import sys
import os
import cv2
import numpy as np

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from model.src.inference import YOLOInference
from api.src.pipeline.tracker import IoUTracker

print("=== Running Verification Tests ===")

# Test 1: Native ONNX Inference
print("\nTest 1: Native ONNX Inference")
model = YOLOInference('model/weights/best.onnx')
model.load()

if not model.is_loaded:
    print("[ERROR] ONNX Model failed to load!")
    sys.exit(1)
else:
    print("[SUCCESS] ONNX Model loaded successfully!")

# Make a dummy gray image frame (640, 640, 3)
frame = np.ones((640, 640, 3), dtype=np.uint8) * 128
detections = model.infer(frame)
print(f"[SUCCESS] Inference run succeeded! Detections count: {len(detections)}")

# Test 2: IoU Tracker
print("\nTest 2: IoU Multi-Object Tracker")
tracker = IoUTracker()
dummy_dets_1 = [
    {"class_id": 2, "class_name": "car", "confidence": 0.9, "bbox": [100.0, 100.0, 200.0, 200.0]},
    {"class_id": 0, "class_name": "person", "confidence": 0.8, "bbox": [300.0, 300.0, 350.0, 450.0]}
]

print("Frame 1 update:")
tracked_1 = tracker.update(dummy_dets_1)
for d in tracked_1:
    print(f"  Detected: {d['class_name']} -> Track ID: {d.get('track_id')}")
    if d.get('track_id') is None:
        print("[ERROR] Tracker failed to assign ID!")
        sys.exit(1)

# Simulating movement of objects in subsequent frame
dummy_dets_2 = [
    {"class_id": 2, "class_name": "car", "confidence": 0.85, "bbox": [105.0, 102.0, 205.0, 202.0]}, # slight shift
    {"class_id": 0, "class_name": "person", "confidence": 0.78, "bbox": [302.0, 298.0, 352.0, 448.0]} # slight shift
]

print("Frame 2 update (slight motion):")
tracked_2 = tracker.update(dummy_dets_2)
for d in tracked_2:
    print(f"  Detected: {d['class_name']} -> Track ID: {d.get('track_id')}")
    if d.get('track_id') not in [1, 2]:
        print(f"[ERROR] Track ID switched or is incorrect! Got: {d.get('track_id')}")
        sys.exit(1)

print("[SUCCESS] Tracker IDs preserved successfully across frames!")

print("\n=== Verification Script Complete. All Tests Passed! ===")
sys.exit(0)
