"""
Quick test to see if the ONNX model is actually producing detections on a real image frame.
Run from the project root.
"""
import cv2
import numpy as np
import sys

sys.path.insert(0, 'model')
from src.inference import YOLOInference

# Load model
model = YOLOInference('model/weights/best.onnx')
model.load()

# Create a realistic test frame (not black, use a highway-scene color distribution)
test_frame = np.ones((640, 640, 3), dtype=np.uint8) * 100  # grey road-ish background

print(f"Model loaded: {model.is_loaded}")
print(f"Model classes: {model.model.names}")
print()

# Test 1: Grey frame
detections = model.infer(test_frame)
print(f"[Test 1 - Grey frame] Detections: {len(detections)}")

# Test 2: Load an actual uploaded video frame if it exists
import os
upload_dir = 'data/uploads'
if os.path.exists(upload_dir):
    files = os.listdir(upload_dir)
    print(f"Upload dir files: {files}")
    for f in files:
        if f.endswith(('.mp4', '.avi', '.mov')):
            path = os.path.join(upload_dir, f)
            cap = cv2.VideoCapture(path)
            ret, frame = cap.read()
            cap.release()
            if ret:
                print(f"\n[Test 2 - Real frame from {f}]")
                print(f"  Frame shape: {frame.shape}")
                detections = model.infer(frame)
                print(f"  Detections (conf=0.25): {len(detections)}")
                for d in detections:
                    print(f"    - {d['class_name']} ({d['confidence']:.3f})")
                
                # Also try with very low confidence
                results = model.model(frame, conf=0.01, verbose=False)
                boxes = results[0].boxes
                if boxes is not None and len(boxes) > 0:
                    print(f"  Detections at conf=0.01: {len(boxes)}")
                    for box in boxes:
                        cid = int(box.cls[0].item())
                        conf = float(box.conf[0].item())
                        print(f"    - class_{cid} ({model.model.names.get(cid, '?')}) conf={conf:.4f}")
                else:
                    print("  Detections at conf=0.01: NONE")
            break
else:
    print("No upload dir found.")
