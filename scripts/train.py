"""
Phase 9 — YOLO26 Training Script on BDD100K
Run from repo root: python scripts/train.py
"""
from ultralytics import YOLO, settings
import os

# Ensure datasets_dir is set to the configs folder relative to project root for cross-platform path resolution
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
settings.update({'datasets_dir': os.path.join(project_root, "model", "configs")})

CONFIG = "model/configs/bdd100k.yaml"
OUTPUT_DIR = "results/training"
EPOCHS = 50
IMGSZ = 640
BATCH = 16
DEVICE = 0  # 0 = first GPU, 'cpu' for CPU-only

def train():
    model = YOLO("yolo26n.pt")  # Start from YOLO26 Nano pretrained weights
    results = model.train(
        data=CONFIG,
        epochs=EPOCHS,
        imgsz=IMGSZ,
        batch=BATCH,
        device=DEVICE,
        project=OUTPUT_DIR,
        name="bdd100k_run1",
        patience=10,           # Early stopping
        save=True,
        cache=True,
        workers=4,
        plots=True,
        val=True,
    )
    print(f"\n[DONE] Best weights saved at: {results.save_dir}/weights/best.pt")
    return results

if __name__ == "__main__":
    train()
