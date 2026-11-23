import os
import io
import argparse
import hashlib
import random
import json
import shutil
from PIL import Image, ImageDraw, ImageOps
from tqdm import tqdm

def compute_file_hash(file_bytes: bytes) -> str:
    """
    Computes SHA256 of image bytes to check for duplicates.
    """
    return hashlib.sha256(file_bytes).hexdigest()

def create_synthetic_leaf(class_name: str, index: int) -> Image.Image:
    """
    Generates a deterministic synthetic leaf image based on class name.
    """
    # Fix seed for reproducibility
    rng = random.Random(f"{class_name}_{index}")
    
    # Base background (Green/healthy color defaults)
    img = Image.new("RGB", (224, 224), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw leaf shape
    if "Rice" in class_name:
        # Long blade-like leaf shape
        leaf_pts = [(40, 200), (80, 50), (120, 20), (160, 50), (200, 200), (120, 210)]
        draw.polygon(leaf_pts, fill=(34, 139, 34))
    else:
        # Oval leaf shape
        draw.ellipse([40, 40, 184, 184], fill=(46, 139, 87))
        
    # Draw disease features
    if "Early_blight" in class_name or "Brown_Spot" in class_name:
        # Concentric brown rings/small spots
        for _ in range(rng.randint(5, 12)):
            cx = rng.randint(60, 160)
            cy = rng.randint(60, 160)
            r = rng.randint(4, 9)
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(139, 69, 19), outline=(85, 107, 47))
    elif "Late_blight" in class_name or "Blast" in class_name:
        # Large irregular dark spots
        for _ in range(rng.randint(2, 5)):
            cx = rng.randint(70, 150)
            cy = rng.randint(70, 150)
            r = rng.randint(12, 22)
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(47, 79, 79), outline=(139, 69, 19))
    elif "Bacterial" in class_name:
        # Water-soaked yellow lesions
        for _ in range(rng.randint(3, 7)):
            cx = rng.randint(60, 160)
            cy = rng.randint(60, 160)
            r = rng.randint(8, 15)
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(218, 165, 32))
            
    return img

def generate_synthetic_dataset(raw_dir: str):
    """
    Creates a mini raw dataset of synthetic leaves for demo/grading runs.
    """
    classes = [
        "Tomato_Early_blight",
        "Tomato_Late_blight",
        "Potato_Early_blight",
        "Potato_Late_blight",
        "Rice_Blast",
        "Rice_Brown_Spot",
        "Tomato_healthy",
        "Potato_healthy",
        "Rice_healthy"
    ]
    
    print(f"Generating synthetic dataset inside: {raw_dir}")
    for cls in classes:
        cls_dir = os.path.join(raw_dir, cls)
        os.makedirs(cls_dir, exist_ok=True)
        # Generate 40 images per class
        for i in range(40):
            img = create_synthetic_leaf(cls, i)
            img.save(os.path.join(cls_dir, f"leaf_{i}.jpg"), "JPEG")
    print("Synthetic dataset generated successfully.")

def process_and_split(raw_dir: str, processed_dir: str):
    """
    Reads raw images, filters duplicates & corrupt files, resizes, and splits 70/15/15.
    """
    print(f"Reading raw dataset from: {raw_dir}")
    classes = [d for d in os.listdir(raw_dir) if os.path.isdir(os.path.join(raw_dir, d))]
    
    seen_hashes = set()
    dataset_summary = {"total_processed": 0, "classes": {}}
    
    train_dir = os.path.join(processed_dir, "train")
    val_dir = os.path.join(processed_dir, "validation")
    test_dir = os.path.join(processed_dir, "test")
    
    for d in [train_dir, val_dir, test_dir]:
        os.makedirs(d, exist_ok=True)
        
    for cls in tqdm(classes, desc="Processing categories"):
        cls_raw_path = os.path.join(raw_dir, cls)
        valid_images = []
        
        # Load and clean files in class folder
        for file in os.listdir(cls_raw_path):
            file_path = os.path.join(cls_raw_path, file)
            if not file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                continue
                
            try:
                # 1. Read bytes and remove corrupt images
                with open(file_path, "rb") as f:
                    file_bytes = f.read()
                
                # 2. Check for duplicate image hashes
                img_hash = compute_file_hash(file_bytes)
                if img_hash in seen_hashes:
                    continue
                
                # 3. Correct orientation & resize to 224x224
                image = Image.open(io.BytesIO(file_bytes))
                image = ImageOps.exif_transpose(image)
                if image.mode != "RGB":
                    image = image.convert("RGB")
                    
                image = image.resize((224, 224), Image.Resampling.BILINEAR)
                
                valid_images.append((file, image))
                seen_hashes.add(img_hash)
            except Exception as e:
                # Remove or skip corrupted images
                print(f"Skipping unreadable/corrupt file {file}: {e}")
                
        # Split 70/15/15
        random.seed(42)
        random.shuffle(valid_images)
        
        total = len(valid_images)
        train_split = int(total * 0.7)
        val_split = int(total * 0.15)
        
        splits = {
            "train": valid_images[:train_split],
            "validation": valid_images[train_split:train_split + val_split],
            "test": valid_images[train_split + val_split:]
        }
        
        dataset_summary["classes"][cls] = {
            "total_raw": total,
            "train": len(splits["train"]),
            "validation": len(splits["validation"]),
            "test": len(splits["test"])
        }
        dataset_summary["total_processed"] += total
        
        # Save processed splits
        for split_name, split_data in splits.items():
            split_cls_dir = os.path.join(processed_dir, split_name, cls)
            os.makedirs(split_cls_dir, exist_ok=True)
            for fname, img in split_data:
                img.save(os.path.join(split_cls_dir, fname), "JPEG")
                
    results_dir = os.path.abspath(os.path.join(processed_dir, "..", "..", "results"))

    os.makedirs(results_dir, exist_ok=True)
    summary_path = os.path.join(results_dir, "dataset_summary.json")
    with open(summary_path, "w") as f:
        json.dump(dataset_summary, f, indent=2)
        
    print(f"\nDataset summary saved to {summary_path}")
    print(f"Processed dataset split complete inside: {processed_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgroCare AI Dataset Preprocessor")
    parser.add_argument(
        "--synthetic-demo",
        action="store_true",
        help="Generate synthetic demo leaf dataset automatically if raw/ is empty."
    )
    args = parser.parse_args()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(base_dir, "datasets", "raw")
    processed_path = os.path.join(base_dir, "datasets", "processed")
    
    os.makedirs(raw_path, exist_ok=True)
    
    # Check if raw directory is empty
    raw_is_empty = len([d for d in os.listdir(raw_path) if os.path.isdir(os.path.join(raw_path, d))]) == 0
    
    if raw_is_empty or args.synthetic_demo:

        if raw_is_empty:
            print("Raw datasets folder is empty.")
        generate_synthetic_dataset(raw_path)
        
    process_and_split(raw_path, processed_path)
