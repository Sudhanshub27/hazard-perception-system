"""
Phase 2/9 — BDD100K Dataset Download & YOLO Format Conversion
Requires: pip install fiftyone gdown opencv-python numpy
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

def generate_mock_dataset():
    print("No raw dataset found at data/raw/bdd100k. Generating mock BDD100K-compatible dataset...")
    import numpy as np
    import cv2
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for split in ["train", "val"]:
        img_dir = OUT_DIR / "images" / split
        lbl_dir = OUT_DIR / "labels" / split
        img_dir.mkdir(parents=True, exist_ok=True)
        lbl_dir.mkdir(parents=True, exist_ok=True)
        
        # Create 10 dummy images and labels per split
        for i in range(10):
            img_name = f"mock_{split}_{i:03d}.jpg"
            img_path = img_dir / img_name
            lbl_path = lbl_dir / (Path(img_name).stem + ".txt")
            
            # Generate solid color image (1280x720 RGB)
            img = np.zeros((720, 1280, 3), dtype=np.uint8)
            # Add some colored rectangles to simulate objects
            for cls_id in range(10):
                # Calculate coordinates for bounding box
                x1 = 100 + cls_id * 80 + i * 10
                y1 = 100 + cls_id * 40
                x2 = x1 + 60
                y2 = y1 + 60
                # Draw on image
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), -1)
            cv2.imwrite(str(img_path), img)
            
            # Write labels in YOLO format
            # class_id cx cy w h
            labels = []
            for cls_id in range(10):
                x1 = 100 + cls_id * 80 + i * 10
                y1 = 100 + cls_id * 40
                x2 = x1 + 60
                y2 = y1 + 60
                cx, cy, w, h = convert_bbox_to_yolo(1280, 720, x1, y1, x2, y2)
                labels.append(f"{cls_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
                
            with open(lbl_path, "w") as f:
                f.write("\n".join(labels))
    print("Mock dataset generation completed successfully!")

def main():
    print("Converting BDD100K to YOLO format...")
    print("NOTE: Ensure you have downloaded BDD100K from https://bdd-data.berkeley.edu/")
    print(f"      and placed images at: {RAW_DIR}/images/100k/")
    print(f"      and labels at:        {RAW_DIR}/labels/det_20/")

    train_labels = RAW_DIR / "labels/det_20/det_train.json"
    if not train_labels.exists():
        generate_mock_dataset()
        return

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
