"""
Converts BDD100K JSON annotations to YOLO26 format (.txt).

BDD100K labels are provided as a single large JSON list (one per split).
YOLO requires one .txt file per image, containing:
<class_index> <x_center> <y_center> <width> <height>
where coordinates are normalized between 0 and 1.
"""

import json
import os
import argparse
from pathlib import Path
from tqdm import tqdm

# BDD100K mapping matching our bdd100k.yaml
CLASS_MAPPING = {
    "car": 0,
    "truck": 1,
    "bus": 2,
    "person": 3,
    "rider": 4,
    "bicycle": 5,
    "motorcycle": 6,
    "traffic light": 7,
    "traffic sign": 8,
    "train": 9
}

# All BDD100K images are fixed at 1280x720
IMG_W = 1280.0
IMG_H = 720.0

def convert_bbox_to_yolo(box2d: dict) -> tuple:
    """Convert absolute [x1, y1, x2, y2] to normalized [x_center, y_center, w, h]"""
    # Clamp coordinates to image boundaries
    x1 = max(0.0, float(box2d["x1"]))
    y1 = max(0.0, float(box2d["y1"]))
    x2 = min(IMG_W, float(box2d["x2"]))
    y2 = min(IMG_H, float(box2d["y2"]))
    
    # Calculate box width and height
    w = x2 - x1
    h = y2 - y1
    
    # Calculate center points
    x_c = x1 + (w / 2)
    y_c = y1 + (h / 2)
    
    # Normalize heavily to [0, 1]
    return (
        x_c / IMG_W,
        y_c / IMG_H,
        w / IMG_W,
        h / IMG_H
    )

def main():
    parser = argparse.ArgumentParser(description="Convert BDD100K JSON to YOLO26 txt annotations")
    parser.add_argument("--json-path", type=str, required=True, help="Path to BDD100K json file (e.g., bdd100k_labels_images_train.json)")
    parser.add_argument("--output-dir", type=str, required=True, help="Directory to save YOLO .txt files")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading {args.json_path}...")
    with open(args.json_path, 'r') as f:
        data = json.load(f)
        
    print(f"Found {len(data)} image records. Converting to YOLO format in {args.output_dir}...")
    
    converted_count = 0
    empty_count = 0
    
    for item in tqdm(data):
        img_name = item["name"] # e.g., 'b2c9b...jpg'
        txt_name = Path(img_name).with_suffix(".txt").name
        txt_path = output_dir / txt_name
        
        yolo_lines = []
        
        # BDD100K JSON contains a list of labels per image
        if "labels" in item and item["labels"]:
            for label in item["labels"]:
                category = label.get("category")
                
                # Only keep classes we care about (ignore drivable area, lane lines)
                if category in CLASS_MAPPING and "box2d" in label:
                    class_id = CLASS_MAPPING[category]
                    x_c, y_c, w, h = convert_bbox_to_yolo(label["box2d"])
                    
                    # Format: `<class_id> <x_center> <y_center> <width> <height>`
                    line = f"{class_id} {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}"
                    yolo_lines.append(line)
                    
        if yolo_lines:
            with open(txt_path, 'w') as f:
                f.write("\n".join(yolo_lines) + "\n")
            converted_count += 1
        else:
            # Create an empty txt file for images with no objects (background frames)
            # YOLO uses these to reduce false positives
            with open(txt_path, 'w') as f:
                pass
            empty_count += 1
            
    print("\n--- Conversion Complete ---")
    print(f"Total processed: {len(data)}")
    print(f"Images with objects: {converted_count}")
    print(f"Images without objects (background): {empty_count}")

if __name__ == "__main__":
    main()
