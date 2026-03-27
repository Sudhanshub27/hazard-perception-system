"""
Splits the raw BDD100K images and parsed YOLO labels
into the strict directory structure required by YOLO26.

YOLO26 looks for directories organized like this (as defined in bdd100k.yaml):

data/processed/bdd100k_yolo/
    ├── images/
    │   ├── train/     # 80K images
    │   ├── val/       # 10K images
    │   └── test/      # 10K images
    └── labels/
        ├── train/     # 80K .txt files
        ├── val/       # 10K .txt files
        └── test/      # 10K .txt files

Note: BDD100K already provides a 70k (Train) and 10k (Val) and 20k (Test) split out of the box. 
We will just map their "train" folder to YOLO "train", "val" to YOLO "val", and take 10k from their "test" to YOLO "test".
"""

import os
import shutil
from pathlib import Path
from tqdm import tqdm

def create_yolo_structure(output_dir: Path):
    """Creates the necessary subdirectories under data/processed"""
    for split in ["train", "val", "test"]:
        (output_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (output_dir / "labels" / split).mkdir(parents=True, exist_ok=True)

def copy_files(source_img_dir: Path, source_lbl_dir: Path, output_dir: Path, split_name: str):
    """
    Copies images and their corresponding label files into the YOLO structure.
    """
    dest_img_dir = output_dir / "images" / split_name
    dest_lbl_dir = output_dir / "labels" / split_name
    
    print(f"Processing split: {split_name}...")
    
    # Get all .jpg images in the source directory
    images = list(source_img_dir.glob("*.jpg"))
    if not images:
        print(f"  WARNING: No images found in {source_img_dir}")
        return

    skipped_files = 0
    
    for img_path in tqdm(images):
        lbl_path = source_lbl_dir / f"{img_path.stem}.txt"
        
        # We strictly only move images that have a matching label file
        if lbl_path.exists():
            shutil.copy2(img_path, dest_img_dir / img_path.name)
            shutil.copy2(lbl_path, dest_lbl_dir / lbl_path.name)
        else:
            skipped_files += 1
            
    if skipped_files > 0:
        print(f"  Skipped {skipped_files} images because they lacked a YOLO .txt file.")
    print(f"  Completed {split_name} split.\n")

def main():
    root = Path(__file__).parent.parent
    yolo_dir = root / "data" / "processed" / "bdd100k_yolo"
    raw_img_dir = root / "data" / "raw" / "bdd100k" / "images" / "100k"
    parsed_lbl_dir = root / "data" / "processed" / "parsed_labels"
    
    print("Creating YOLO26 dataset structure...")
    create_yolo_structure(yolo_dir)
    
    # Map BDD100K Train set
    copy_files(
        source_img_dir=raw_img_dir / "train",
        source_lbl_dir=parsed_lbl_dir / "train",
        output_dir=yolo_dir,
        split_name="train"
    )
    
    # Map BDD100K Validation set
    copy_files(
        source_img_dir=raw_img_dir / "val",
        source_lbl_dir=parsed_lbl_dir / "val",
        output_dir=yolo_dir,
        split_name="val"
    )
    
    # Test set parsing (if available, otherwise it can be empty for YOLO training)
    if (raw_img_dir / "test").exists() and (parsed_lbl_dir / "test").exists():
        copy_files(
            source_img_dir=raw_img_dir / "test",
            source_lbl_dir=parsed_lbl_dir / "test",
            output_dir=yolo_dir,
            split_name="test"
        )
    else:
        print("Test split skipped (annotations or images not found). Training can proceed without it.")
        
    print(f"Dataset securely structured at {yolo_dir.absolute()}")

if __name__ == "__main__":
    main()
