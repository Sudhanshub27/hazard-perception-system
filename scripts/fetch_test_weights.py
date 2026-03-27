from ultralytics import YOLO
import shutil
import os

print("Downloading standard pre-trained COCO YOLO model to test the dashboard...")
model = YOLO('yolov8n.pt')
print("Exporting model to ONNX format...")
path = model.export(format='onnx', opset=17)

# Move the generic model to where the API expects the BDD100K model
os.makedirs("model/weights", exist_ok=True)
shutil.move(path, "model/weights/best.onnx")
print("Successfully mocked best.onnx! The Docker model container will now pick it up.")
