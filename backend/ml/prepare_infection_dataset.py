import os
import json
import shutil
import hashlib
import random
import numpy as np
from PIL import Image, ImageOps, ImageDraw

RAW_DIR = "ml/datasets/raw"
PROCESSED_DIR = "ml/datasets/processed_infection"
SUMMARY_PATH = "ml/results/infection_dataset_summary.json"
MAPPING_PATH = "ml/results/source_class_mapping.json"
UNMAPPED_DIR = "ml/datasets/unmapped"
UNMAPPED_JSON = "ml/results/unmapped_classes.json"

CATEGORIES = {
    "Fungal_Infection": "Fungal Infection",
    "Bacterial_Infection": "Bacterial Infection",
    "Viral_Disease": "Viral Disease",
    "Pest_Damage": "Pest Damage",
    "Nutrient_Deficiency": "Nutrient Deficiency",
    "Healthy_Leaf": "Healthy Leaf"
}

MAPPING_RULES = {
    "Fungal_Infection": [
        "blight", "late_blight", "early_blight", "leaf_spot", "spot", "mold", 
        "mildew", "rust", "anthracnose", "scab", "rot", "blast", "smut", 
        "septoria", "cercospora", "alternaria", "powdery"
    ],
    "Bacterial_Infection": [
        "bacterial", "bacterial_spot", "bacterial_leaf_blight", "bacterial_wilt", 
        "black_rot", "bacterial_black_spot"
    ],
    "Viral_Disease": [
        "virus", "viral", "mosaic", "leaf_curl", "yellow_leaf_curl", "tungro", "curl"
    ],
    "Pest_Damage": [
        "pest", "insect", "mite", "aphid", "whitefly", "borer", "caterpillar", 
        "leaf_miner", "thrips", "pest_damage", "damage"
    ],
    "Nutrient_Deficiency": [
        "deficiency", "nitrogen", "potassium", "magnesium", "calcium", "iron", 
        "zinc", "phosphorus", "chlorosis", "nutrient"
    ],
    "Healthy_Leaf": [
        "healthy", "normal"
    ]
}

def clean_exif_and_convert_to_rgb(img_path: str) -> Image.Image:
    img = Image.open(img_path)
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img

def compute_sha256(img: Image.Image) -> str:
    return hashlib.sha256(img.tobytes()).hexdigest()

def parse_metadata_from_name(name: str):
    clean_name = name.replace("_", " ").replace("-", " ")
    parts = clean_name.split()
    if not parts:
        return "General", "Healthy Leaf", "Healthy Leaf"
        
    crop = parts[0].capitalize()
    name_lower = name.lower()
    
    if "healthy" in name_lower or "normal" in name_lower:
        return crop, "Healthy Leaf", "Healthy Leaf"
        
    disease_words = []
    for p in parts[1:]:
        if p.isdigit():
            break
        disease_words.append(p.capitalize())
        
    disease = " ".join(disease_words) if disease_words else "Unknown Disease"
    
    category = "Fungal Infection"
    for cat_name, keywords in MAPPING_RULES.items():
        if any(kw in name_lower for kw in keywords):
            category = CATEGORIES[cat_name]
            break
            
    return crop, disease, category

def augment_image(img: Image.Image) -> Image.Image:
    aug_type = random.randint(0, 3)
    if aug_type == 0:
        return img.rotate(random.randint(-30, 30), fillcolor=(34, 139, 34))
    elif aug_type == 1:
        return img.transpose(Image.FLIP_LEFT_RIGHT)
    elif aug_type == 2:
        return img.transpose(Image.FLIP_TOP_BOTTOM)
    else:
        factor = random.uniform(0.8, 1.2)
        arr = np.array(img, dtype=np.float32) * factor
        arr = np.clip(arr, 0, 255).astype(np.uint8)
        return Image.fromarray(arr)

def generate_synthetic_leaf(category_name: str, index: int) -> Image.Image:
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    draw = ImageDraw.Draw(img)
    draw.ellipse([20, 50, 204, 174], fill=(46, 139, 87))
    
    if category_name == "Fungal_Infection":
        for _ in range(8):
            cx, cy = random.randint(40, 180), random.randint(70, 150)
            r = random.randint(4, 12)
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(139, 69, 19))
    elif category_name == "Bacterial_Infection":
        for _ in range(6):
            cx, cy = random.randint(40, 180), random.randint(70, 150)
            r = random.randint(6, 14)
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(218, 165, 32))
            draw.ellipse([cx-r//2, cy-r//2, cx+r//2, cy+r//2], fill=(47, 79, 79))
    elif category_name == "Viral_Disease":
        for _ in range(5):
            x1, y1 = random.randint(30, 150), random.randint(60, 120)
            x2, y2 = x1 + random.randint(20, 50), y1 + random.randint(20, 50)
            draw.line([x1, y1, x2, y2], fill=(154, 205, 50), width=6)
    elif category_name == "Pest_Damage":
        for _ in range(4):
            cx, cy = random.randint(50, 170), random.randint(70, 140)
            r = random.randint(8, 16)
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(128, 128, 128))
    elif category_name == "Nutrient_Deficiency":
        draw.ellipse([20, 50, 204, 174], outline=(238, 232, 170), width=8)
    
    return img

def run_preparation():
    print("Starting Infection Category Dataset Preparation...")
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs("ml/results", exist_ok=True)
    
    if os.path.exists(UNMAPPED_DIR):
        shutil.rmtree(UNMAPPED_DIR)
    os.makedirs(UNMAPPED_DIR, exist_ok=True)
    
    # 1. Determine if raw directory has images or needs synthetic fallback
    original_raw_counts = {cat: 0 for cat in CATEGORIES.keys()}
    for cat in CATEGORIES.keys():
        cat_dir = os.path.join(RAW_DIR, cat)
        if os.path.exists(cat_dir):
            files = [f for f in os.listdir(cat_dir) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
            original_raw_counts[cat] = len(files)

    for cat in CATEGORIES.keys():
        if original_raw_counts[cat] < 20:
            print(f"Category '{CATEGORIES[cat]}' has only {original_raw_counts[cat]} raw images. Supplementing with synthetic data...")
            cat_dir = os.path.join(RAW_DIR, cat)
            os.makedirs(cat_dir, exist_ok=True)
            crop_prefix = "tomato"
            if "viral" in cat.lower():
                crop_prefix = "rice"
            elif "deficiency" in cat.lower():
                crop_prefix = "jute"
            elif "pest" in cat.lower():
                crop_prefix = "chili"
            
            needed = 40 - original_raw_counts[cat]
            for i in range(needed):
                img = generate_synthetic_leaf(cat, i)
                filename = f"synth_{crop_prefix}_{cat.lower()}_{i:03d}.jpg"
                img.save(os.path.join(cat_dir, filename), "JPEG")

    # 2. Walk raw folder, categorize, deduplicate, find unmapped
    all_mapped_images = {cat: [] for cat in CATEGORIES.keys()}
    image_hashes = set()
    source_mapping = {}
    unmapped_classes_set = set()

    if os.path.exists(PROCESSED_DIR):
        shutil.rmtree(PROCESSED_DIR)
        
    for cat in CATEGORIES.keys():
        for split in ["train", "validation", "test"]:
            os.makedirs(os.path.join(PROCESSED_DIR, split, cat), exist_ok=True)

    for root, dirs, files in os.walk(RAW_DIR):
        for file in files:
            if not file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                continue
                
            file_path = os.path.join(root, file)
            parent_folder = os.path.basename(root)
            
            # Determine target category
            target_cat = None
            if parent_folder in CATEGORIES:
                target_cat = parent_folder
            else:
                name_to_check = f"{parent_folder}_{file}"
                for cat_key, keywords in MAPPING_RULES.items():
                    if any(kw in name_to_check.lower() for kw in keywords):
                        target_cat = cat_key
                        break
                        
            if not target_cat:
                unmapped_subdir = os.path.join(UNMAPPED_DIR, parent_folder)
                os.makedirs(unmapped_subdir, exist_ok=True)
                shutil.copy(file_path, os.path.join(unmapped_subdir, file))
                unmapped_classes_set.add(parent_folder)
                continue
                
            try:
                img = clean_exif_and_convert_to_rgb(file_path)
                h = compute_sha256(img)
                if h in image_hashes:
                    continue
                image_hashes.add(h)
                
                img_resized = img.resize((224, 224), Image.Resampling.BILINEAR)
                crop, disease, category = parse_metadata_from_name(f"{parent_folder}_{file}")
                
                all_mapped_images[target_cat].append((img_resized, file))
                source_mapping[h] = {
                    "crop_name": crop,
                    "disease_name": disease,
                    "infection_category": category,
                    "is_healthy": (target_cat == "Healthy_Leaf")
                }

            except Exception as e:
                print(f"Skipping corrupted image {file_path}: {e}")

    # 3. Perform 70/15/15 split and Balance training split
    train_counts = {}
    val_counts = {}
    test_counts = {}
    low_data_classes = []
    missing_classes = []
    
    for cat in CATEGORIES.keys():
        lbl = CATEGORIES[cat]
        orig_count = original_raw_counts.get(cat, 0)
        if orig_count == 0:
            missing_classes.append(lbl)
        elif orig_count < 100:
            low_data_classes.append(lbl)

    max_train_count = 0
    raw_splits = {}

    for cat, items in all_mapped_images.items():
        random.seed(42)
        random.shuffle(items)
        
        num_items = len(items)
        train_end = int(num_items * 0.70)
        val_end = train_end + int(num_items * 0.15)
        
        raw_splits[cat] = {
            "train": items[:train_end],
            "validation": items[train_end:val_end],
            "test": items[val_end:]
        }
        
        if train_end > max_train_count:
            max_train_count = train_end

    target_train_size = max(300, max_train_count)

    for cat, splits in raw_splits.items():
        # Save Validation & Test exactly (no duplication)
        val_counts[CATEGORIES[cat]] = len(splits["validation"])
        for img, filename in splits["validation"]:
            img.save(os.path.join(PROCESSED_DIR, "validation", cat, filename), "JPEG")
            
        test_counts[CATEGORIES[cat]] = len(splits["test"])
        for img, filename in splits["test"]:
            img.save(os.path.join(PROCESSED_DIR, "test", cat, filename), "JPEG")

        # Balance Training Set
        train_items = splits["train"]
        train_counts[CATEGORIES[cat]] = target_train_size
        
        for img, filename in train_items:
            img.save(os.path.join(PROCESSED_DIR, "train", cat, filename), "JPEG")
            
        if len(train_items) > 0:
            needed = target_train_size - len(train_items)
            for i in range(needed):
                base_img, base_filename = random.choice(train_items)
                aug_img = augment_image(base_img)
                aug_filename = f"aug_{i:04d}_{base_filename}"
                aug_img.save(os.path.join(PROCESSED_DIR, "train", cat, aug_filename), "JPEG")

    # 4. Save metadata summary
    total_images_processed = sum(len(items) for items in all_mapped_images.values())
    counts_list = [len(items) for items in all_mapped_images.values() if len(items) > 0]
    imbalance_ratio = float(max(counts_list) / min(counts_list)) if counts_list else 1.0

    summary = {
        "total_images": total_images_processed,
        "category_counts": {CATEGORIES[c]: len(all_mapped_images[c]) for c in CATEGORIES},
        "train_counts": train_counts,
        "validation_counts": val_counts,
        "test_counts": test_counts,
        "class_imbalance_ratio": imbalance_ratio,
        "missing_classes": missing_classes,
        "low_data_classes": low_data_classes,
        "categories_status": {}
    }
    
    for cat in CATEGORIES.keys():
        orig_count = original_raw_counts.get(cat, 0)
        if orig_count >= 100:
            summary["categories_status"][CATEGORIES[cat]] = "Adequate Data"
        elif orig_count > 0:
            summary["categories_status"][CATEGORIES[cat]] = "Low Data (Oversampled / Augmented)"
        else:
            summary["categories_status"][CATEGORIES[cat]] = "Missing Data (Requires real images)"

    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Dataset summary saved to: {SUMMARY_PATH}")
    
    with open(MAPPING_PATH, "w") as f:
        json.dump(source_mapping, f, indent=2)
    print(f"Source class mapping metadata saved to: {MAPPING_PATH}")
    
    with open(UNMAPPED_JSON, "w") as f:
        json.dump(list(unmapped_classes_set), f, indent=2)
    print(f"Unmapped classes logged to: {UNMAPPED_JSON}")
    
    print("\nDataset preparation and balancing completed successfully!")
    print(f"Total original processed images: {total_images_processed}")
    print(f"Balanced training images per class: {target_train_size}")

if __name__ == "__main__":
    run_preparation()
