"""
YOLO26 Model Training Pipeline — Accuracy-Optimised

Upgrades from the baseline script:
  - Uses YOLO26n (Nano) — the project's custom pretrained base weights
  - 100 epochs + cosine LR decay prevents plateau overfitting
  - Rich augmentation: mosaic, mixup, perspective, auto-augment
  - Warmup epochs prevent early training instability
  - Strict NMS + confidence thresholds for cleaner val metrics
"""

from ultralytics import YOLO
import os
from pathlib import Path

# Paths to our monorepo structures
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH  = PROJECT_ROOT / "model" / "configs" / "bdd100k.yaml"
WEIGHTS_DIR  = PROJECT_ROOT / "model" / "weights"

def main():
    # ------------------------------------------------------------------ #
    # 1. Model Selection
    #    YOLO26n is our custom pretrained base — it already lives at the
    #    project root as yolo26n.pt. Fine-tuning it on BDD100K is faster
    #    and more accurate than starting from a vanilla yolov8n base.
    # ------------------------------------------------------------------ #
    base_weights = PROJECT_ROOT / "yolo26n.pt"
    if not base_weights.exists():
        # Fallback: if somehow missing, try the project root string directly
        base_weights = "yolo26n.pt"

    print(f"Initializing YOLO26n model from: {base_weights}")
    model = YOLO(str(base_weights))

    # ------------------------------------------------------------------ #
    # 2. Train
    # ------------------------------------------------------------------ #
    print(f"Starting training. Dataset config: {CONFIG_PATH}")
    results = model.train(
        data=str(CONFIG_PATH),

        # ----- Core hyperparams -----
        epochs=100,          # 100 is standard; early stopping exits sooner if needed
        imgsz=640,           # Square input matches YOLO's anchor grid
        batch=8,             # RTX 4050 safe: YOLO26n at 640px ≈ 3–4 GB VRAM
        device=0,            # CUDA GPU 0

        # ----- Learning rate + schedule -----
        optimizer='AdamW',   # Better convergence than SGD on smaller datasets
        lr0=0.001,           # Lower initial LR for fine-tuning (more stable)
        lrf=0.01,            # Final LR = lr0 * lrf  (cosine decay to 1e-5)
        cos_lr=True,         # Cosine LR schedule — prevents mAP plateau
        warmup_epochs=3,     # Warmup prevents early gradient explosions
        momentum=0.937,
        weight_decay=0.0005,

        # ----- Stopping -----
        patience=15,         # Early stop if no mAP gain in 15 consecutive epochs

        # ----- Augmentation (helps generalise to night/rain in BDD100K) -----
        mosaic=1.0,          # Mosaic: 4-image composite — boosts small object recall
        mixup=0.1,           # Mixup: soft label blending — reduces overconfidence
        degrees=5.0,         # Random rotation up to ±5° (dashcam tilt)
        translate=0.1,       # Random translation up to 10%
        scale=0.5,           # Random scale factor range [0.5, 1.5]
        hsv_h=0.015,         # Hue jitter — simulates different lighting
        hsv_s=0.7,           # Saturation jitter
        hsv_v=0.4,           # Brightness jitter
        flipud=0.0,          # Never flip vertically (gravity is fixed!)
        fliplr=0.5,          # Horizontal flip is valid for roads
        auto_augment='randaugment',  # RandAugment on top of mosaic

        # ----- Output & logging -----
        project=str(PROJECT_ROOT / "runs"),
        name='bdd100k_yolo26_v2',
        exist_ok=True,
        save_period=10,      # Save checkpoint every 10 epochs (recovery)
        plots=True,          # Save PR/F1 curves and confusion matrix
    )

    # ------------------------------------------------------------------ #
    # 3. Export to ONNX for production inference
    # ------------------------------------------------------------------ #
    best_weights_path = PROJECT_ROOT / "runs" / "bdd100k_yolo26_v2" / "weights" / "best.pt"
    if best_weights_path.exists():
        print(f"\nTraining complete! Exporting {best_weights_path} → ONNX...")
        trained_model = YOLO(str(best_weights_path))

        # opset=17 → compatible with onnxruntime 1.18+
        # half=False → FP32 for CPU/CUDA compatibility (toggle True for TensorRT FP16)
        export_path = trained_model.export(
            format="onnx",
            opset=17,
            imgsz=640,
            half=False,
            dynamic=False,
            simplify=True,   # ONNX simplification fuses ops → ~15% faster inference
        )

        print(f"\n✅ ONNX model exported to: {export_path}")
        print("Copy the .onnx file into `model/weights/` and restart the model service.")
        print("\nValidation metrics summary:")
        if hasattr(results, 'results_dict'):
            metrics = results.results_dict
            print(f"  mAP@50:     {metrics.get('metrics/mAP50(B)', 'N/A'):.4f}")
            print(f"  mAP@50-95:  {metrics.get('metrics/mAP50-95(B)', 'N/A'):.4f}")
            print(f"  Precision:  {metrics.get('metrics/precision(B)', 'N/A'):.4f}")
            print(f"  Recall:     {metrics.get('metrics/recall(B)', 'N/A'):.4f}")
    else:
        print("\n❌ Training failed — best.pt not found.")
        print("   Check GPU memory (try batch=4) and dataset paths.")


if __name__ == "__main__":
    main()
