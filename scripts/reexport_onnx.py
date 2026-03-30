"""
Re-exports ONNX from the best available .pt weights.
The BDD100K trained model has very low recall (~1%) and should not be used.
The original yolov8n.pt or model/weights/best.pt is the working fallback.
"""
import os
import sys
sys.path.insert(0, 'model')

from ultralytics import YOLO

# The model/weights/best.pt is the original pre-trained (larger, 6.5MB vs 6.2MB trained)
# We use it as it was working before BDD100K training
target_pt = 'model/weights/best.pt'
output_onnx = 'model/weights/best.onnx'

print(f"Loading: {target_pt} ({os.path.getsize(target_pt):,} bytes)")
model = YOLO(target_pt)
print(f"Loaded. Classes: {model.names}")

print(f"\nExporting to ONNX at {output_onnx}...")
model.export(format='onnx', opset=17, imgsz=640, simplify=True)

# The export saves next to the .pt file, move it to correct place
exported = target_pt.replace('.pt', '.onnx')
if os.path.exists(exported) and exported != output_onnx:
    import shutil
    shutil.move(exported, output_onnx)
    print(f"Moved to {output_onnx}")

print(f"\nDone! ONNX size: {os.path.getsize(output_onnx):,} bytes")
print("Restart the Model Service for the changes to take effect.")
