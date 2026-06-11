# Agentic Prompt — Complete the Autonomous Hazard Perception System

## 🧠 Project Context

You are working on a production-grade **Autonomous Hazard Perception System** for dashcam video
streams. The GitHub repo is: https://github.com/Sudhanshub27/hazard-perception-system

The full system architecture is **already built and working**:
- ✅ Model inference service (FastAPI + ONNX Runtime, port 8001)
- ✅ Orchestrator API + WebSocket streamer (FastAPI, port 8000)
- ✅ Rule-based risk scorer (4 levels: Safe/Caution/Danger/Critical)
- ✅ Next.js 14 frontend dashboard (real-time video + hazard log)
- ✅ Docker Compose (3 microservices)
- ✅ BDD100K dataset config (`model/configs/bdd100k.yaml`)

**What is NOT done yet (your job):**
- ❌ BDD100K dataset not downloaded/converted
- ❌ YOLO26 model not trained (weights missing)
- ❌ No ONNX export yet
- ❌ No benchmarking / metrics recorded
- ❌ README metrics table is empty
- ❌ No demo GIF / screenshot

---

## 🎯 Your Task: Complete Phases 9 and 10

### PHASE 9 — Dataset Download, Training & Benchmarking

#### Step 1: Fix the dataset config path
File: `model/configs/bdd100k.yaml`

Change the hardcoded Windows path:
```yaml
path: C:\Users\Sudhanshu\projects\yolo\data\processed\bdd100k_yolo
```
To a relative cross-platform path:
```yaml
path: ../../data/processed/bdd100k_yolo
```

#### Step 2: Create a training script
Create the file `scripts/train.py` with the following:

```python
"""
Phase 9 — YOLO26 Training Script on BDD100K
Run from repo root: python scripts/train.py
"""
from ultralytics import YOLO
import os

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
```

#### Step 3: Create a benchmarking + ONNX export script
Create the file `scripts/benchmark.py`:

```python
"""
Phase 9 — Evaluate trained model and export to ONNX
Run: python scripts/benchmark.py --weights results/training/bdd100k_run1/weights/best.pt
"""
import argparse
from ultralytics import YOLO

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
```

#### Step 4: Download and prepare the BDD100K dataset

Create the file `scripts/download_bdd100k.py`:

```python
"""
Phase 2/9 — BDD100K Dataset Download & YOLO Format Conversion
Requires: pip install fiftyone gdown
Run: python scripts/download_bdd100k.py
"""
import os
import json
import shutil
from pathlib import Path

RAW_DIR   = Path("data/raw/bdd100k")
OUT_DIR   = Path("data/processed/bdd100k_yolo")

BDD_CLASSES = {
    "car": 0, "truck": 1, "bus": 2, "person": 3,
    "rider": 4, "bicycle": 5, "motorcycle": 6,
    "traffic light": 7, "traffic sign": 8, "train": 9
}

def convert_bbox_to_yolo(img_w, img_h, x1, y1, x2, y2):
    cx = ((x1 + x2) / 2) / img_w
    cy = ((y1 + y2) / 2) / img_h
    w  = (x2 - x1) / img_w
    h  = (y2 - y1) / img_h
    return cx, cy, w, h

def convert_split(labels_json: Path, images_dir: Path, out_img_dir: Path, out_lbl_dir: Path):
    out_img_dir.mkdir(parents=True, exist_ok=True)
    out_lbl_dir.mkdir(parents=True, exist_ok=True)

    with open(labels_json) as f:
        labels = json.load(f)

    converted, skipped = 0, 0
    for frame in labels:
        img_name  = frame["name"]
        img_path  = images_dir / img_name
        if not img_path.exists():
            skipped += 1
            continue

        annotations = frame.get("labels", []) or []
        label_lines = []
        for ann in annotations:
            cat = ann.get("category", "")
            if cat not in BDD_CLASSES:
                continue
            cls_id = BDD_CLASSES[cat]
            box2d  = ann.get("box2d", {})
            if not box2d:
                continue
            cx, cy, w, h = convert_bbox_to_yolo(
                1280, 720,
                box2d["x1"], box2d["y1"],
                box2d["x2"], box2d["y2"]
            )
            label_lines.append(f"{cls_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")

        shutil.copy(img_path, out_img_dir / img_name)
        txt_name = Path(img_name).stem + ".txt"
        with open(out_lbl_dir / txt_name, "w") as f:
            f.write("\n".join(label_lines))
        converted += 1

    print(f"  Converted: {converted} | Skipped (missing image): {skipped}")

def main():
    print("Converting BDD100K to YOLO format...")
    print("NOTE: Ensure you have downloaded BDD100K from https://bdd-data.berkeley.edu/")
    print(f"      and placed images at: {RAW_DIR}/images/100k/")
    print(f"      and labels at:        {RAW_DIR}/labels/det_20/")

    for split in ["train", "val"]:
        print(f"\n[{split}]")
        convert_split(
            labels_json = RAW_DIR / "labels/det_20" / f"det_{split}.json",
            images_dir  = RAW_DIR / "images/100k" / split,
            out_img_dir = OUT_DIR / "images" / split,
            out_lbl_dir = OUT_DIR / "labels" / split,
        )
    print("\n✅ BDD100K conversion complete!")
    print(f"   Output: {OUT_DIR}")

if __name__ == "__main__":
    main()
```

#### Step 5: After training, update README.md

Find the metrics table in `README.md` (under `## 📊 Model Performance`) and fill in the actual
values you get from `benchmark.py`. It looks like this:

```markdown
| Class       | mAP@0.5 | mAP@0.5:0.95 | Precision | Recall |
| ----------- | ------- | ------------ | --------- | ------ |
| car         | FILL    | FILL         | FILL      | FILL   |
...
| **Overall** | FILL    | FILL         | FILL      | FILL   |

**Inference speed:** X FPS (CPU) / Y FPS (RTX 4050)
```

Replace all `FILL` and `—` values with actual numbers from `val_results`.

---

### PHASE 10 — Demo Assets

#### Step 6: Generate a demo GIF / screenshots

After the full Docker stack is running (`docker compose up --build`):

1. Upload a sample dashcam video via the Next.js UI at `http://localhost:3000`
2. Record a short screen capture showing:
   - The live video feed with bounding boxes overlaid
   - The real-time risk gauge changing
   - The hazard event log populating
3. Export as a GIF (max 10MB) using any screen recorder
4. Save it as `results/demo.gif`

Then update `README.md`:
```markdown
## 🚀 Demo
![Hazard Perception Demo](results/demo.gif)
```

#### Step 7: Add a sample dashcam video for testing
Place any short dashcam clip (5–30 seconds, MP4) at:
```
data/sample/dashcam_sample.mp4
```
You can download a free dashcam clip from: https://www.pexels.com/search/videos/dashcam/

---

## ✅ Final Checklist Before Submitting to Unstop

After all steps above, verify:

- [ ] `model/weights/best.onnx` exists and is non-empty
- [ ] `docker compose up --build` starts all 3 services without errors
- [ ] Uploading a video to `http://localhost:3000` shows live detections
- [ ] Risk gauge updates in real time
- [ ] README metrics table is filled with real numbers
- [ ] `results/demo.gif` exists and is embedded in README
- [ ] `scripts/train.py`, `scripts/benchmark.py`, `scripts/download_bdd100k.py` are committed
- [ ] `model/configs/bdd100k.yaml` path is fixed (no hardcoded Windows path)

---

## ⚙️ Environment Requirements

```
Python 3.11+
ultralytics >= 8.0 (pip install ultralytics)
onnxruntime == 1.18.0
torch >= 2.0 (GPU preferred for training)
CUDA 11.8+ (optional but strongly recommended for training)
Node.js 18+ (for frontend)
Docker Desktop (for full stack)
```

GPU with ≥ 6GB VRAM recommended for training (RTX 3060 or better).
If no GPU available, use Google Colab with T4 GPU (free tier).

---

## 📁 Final Expected File Tree After Completion

```
hazard-perception/
├── model/
│   ├── weights/
│   │   └── best.onnx          ← NEW: trained + exported model
│   └── configs/
│       └── bdd100k.yaml       ← FIXED: relative path
├── scripts/
│   ├── train.py               ← NEW
│   ├── benchmark.py           ← NEW
│   └── download_bdd100k.py    ← NEW
├── results/
│   ├── demo.gif               ← NEW
│   └── training/
│       └── bdd100k_run1/      ← NEW: training artifacts
├── data/
│   └── sample/
│       └── dashcam_sample.mp4 ← NEW
└── README.md                  ← UPDATED: real metrics + demo GIF
```
