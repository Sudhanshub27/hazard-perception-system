"""
YOLO26 Model Training Pipeline

This script drives the core training logic for the BDD100K 10-class dataset.
It initializes a pretrained YOLO26 Nano (or Small) model, trains it on our 
custom .yaml config, and crucially exports it to ONNX for the fastest possible
production inference.
"""

from ultralytics import YOLO
import os
from pathlib import Path

# Paths to our monorepo structures
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH = PROJECT_ROOT / "model" / "configs" / "bdd100k.yaml"
WEIGHTS_DIR = PROJECT_ROOT / "model" / "weights"

def main():
    # 1. Initialize YOLO26 (using the 'n' Nano architecture for real-time speed)
    # Note: In a real interview/production, explain why Nano is chosen over Large!
    # A Large model achieves maybe +3 mAP but drops inference FPS from 35 down to 5.
    print("Initializing YOLO26n base model...")
    model = YOLO("yolo26n.pt") 
    
    # 2. Train the model on BDD100K
    print(f"Starting training pipeline. Reading dataset from {CONFIG_PATH}")
    results = model.train(
        data=str(CONFIG_PATH),
        epochs=50,                  # 50 to 100 epochs is standard
        imgsz=640,                  # Resize BDD100k 1280x720 down to 640x640 dynamically
        batch=16,                   # Optimize for RTX 4050 (6GB VRAM)
        device=0,                   # Target CUDA GPU 0
        patience=10,                # Early stopping: stop if no mAP improvement in 10 epochs
        optimizer='auto',
        lr0=0.01,
        project=str(PROJECT_ROOT / "runs"), # Output directory for metrics/weights
        name='bdd100k_yolo26',
        exist_ok=True,
    )

    # 3. Export the Best Weights to ONNX for Production
    # Our API service uses ONNX Runtime, NOT PyTorch, because ONNX graph optimization 
    # (operator fusion) provides a ~30-40% inference speedup.
    best_weights_path = PROJECT_ROOT / "runs" / "bdd100k_yolo26" / "weights" / "best.pt"
    if best_weights_path.exists():
        print(f"Training complete! Exporting {best_weights_path} to ONNX format...")
        
        # Load the newly trained best weights
        trained_model = YOLO(str(best_weights_path))
        
        # Exporting to ONNX op-set 17 allows compatibility with onnxruntime==1.18.0
        export_path = trained_model.export(
            format="onnx",
            opset=17,
            imgsz=640,
            half=False, # Use FP32. Toggle True for FP16 TensorRT inference later.
            dynamic=False # Fixed batch size of 1 for real-time streaming
        )
        
        print(f"\n✅ Successfully exported ONNX model to: {export_path}")
        print("Now copy the .onnx file into your `model/weights/` directory for the backend to use!")
    else:
        print("\n❌ Training failed or best.pt was not generated.")

if __name__ == "__main__":
    main()
