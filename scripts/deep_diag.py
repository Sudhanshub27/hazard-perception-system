"""
Deep diagnostic - test the ONNX model with the yolov8n base weights 
to check if COCO-trained classes (car=2, person=0) are being detected.
"""
import cv2
import os
import sys

# Use system python / conda ultralytics since it can load the .pt
from ultralytics import YOLO

# Test with base yolov8n.pt (COCO pre-trained)
print("=== Testing yolov8n.pt (base pre-trained COCO model) ===")
model = YOLO('yolov8n.pt')
print(f"Classes: {model.names}")

# Find a video file
upload_dir = 'data/uploads'
video_file = None
if os.path.exists(upload_dir):
    for f in os.listdir(upload_dir):
        if f.endswith(('.mp4', '.avi', '.mov')):
            video_file = os.path.join(upload_dir, f)
            break

if video_file:
    cap = cv2.VideoCapture(video_file)
    ret, frame = cap.read()
    cap.release()
    if ret:
        print(f"\nFrame shape: {frame.shape}")
        results = model(frame, conf=0.1, verbose=False)
        boxes = results[0].boxes
        if boxes is not None:
            print(f"Detections at conf=0.10: {len(boxes)}")
            for box in boxes:
                cid = int(box.cls[0].item())
                print(f"  - {model.names[cid]} ({float(box.conf[0]):.3f})")
        else:
            print("No detections at all")
else:
    print("No video found")

# Now test the custom ONNX
print("\n=== Testing model/weights/best.onnx ===")
model2 = YOLO('model/weights/best.onnx', task='detect')
print(f"Classes: {model2.names}")
if video_file and ret:
    results2 = model2(frame, conf=0.05, verbose=False)
    boxes2 = results2[0].boxes
    if boxes2 is not None:
        print(f"Detections at conf=0.05: {len(boxes2)}")
        for box in boxes2:
            cid = int(box.cls[0].item())
            print(f"  - class{cid} ({model2.names.get(cid,'?')}) ({float(box.conf[0]):.3f})")
    else:
        print("No detections")
