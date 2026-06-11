"""
Phase 9 — Evaluate trained model and export to ONNX
Run: python scripts/benchmark.py --weights results/training/bdd100k_run1/weights/best.pt
"""
import argparse
from ultralytics import YOLO, settings
import os

# Ensure datasets_dir is set to the configs folder relative to project root for cross-platform path resolution
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
settings.update({'datasets_dir': os.path.join(project_root, "model", "configs")})

def benchmark(weights: str):
    model = YOLO(weights)

    # Validate on BDD100K val set
    print("\n[1/3] Running validation on BDD100K val set...")
    val_results = model.val(
        data="model/configs/bdd100k.yaml",
        imgsz=640,
        batch=16,
        conf=0.35,
        iou=0.45,
        device=0,
        plots=True,
        save_json=True,
    )

    print("\n===== BENCHMARK RESULTS =====")
    print(f"mAP@0.5:       {val_results.box.map50:.4f}")
    print(f"mAP@0.5:0.95:  {val_results.box.map:.4f}")
    print(f"Precision:     {val_results.box.mp:.4f}")
    print(f"Recall:        {val_results.box.mr:.4f}")
    per_class = val_results.box.ap_class_index
    print(f"Per-class AP:  {val_results.box.ap50}")

    # Export to ONNX
    print("\n[2/3] Exporting to ONNX (opset 17)...")
    onnx_path = model.export(
        format="onnx",
        imgsz=640,
        opset=17,
        dynamic=False,
        simplify=True,
    )
    print(f"ONNX model saved: {onnx_path}")

    # Copy best.onnx to model/weights/
    import shutil, os
    os.makedirs("model/weights", exist_ok=True)
    shutil.copy(onnx_path, "model/weights/best.onnx")
    print("Copied to model/weights/best.onnx")

    # Speed benchmark
    print("\n[3/3] Speed benchmark (CPU)...")
    speed_results = model.benchmark(
        imgsz=640,
        device="cpu",
        half=False,
    )
    print(f"Inference speed: {speed_results}")

    return val_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", default="results/training/bdd100k_run1/weights/best.pt")
    args = parser.parse_args()
    benchmark(args.weights)
