import os
import json
import random
import argparse
import numpy as np
import tensorflow as tf
from backend.ml.preprocessing import preprocess_image

def test_distribution(dataset_path: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "models", "agrocare_infection_model.keras")
    labels_path = os.path.join(base_dir, "infection_labels.json")
    results_dir = os.path.join(base_dir, "results")
    
    os.makedirs(results_dir, exist_ok=True)
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file missing at: {model_path}")
    if not os.path.exists(labels_path):
        raise FileNotFoundError(f"Labels file missing at: {labels_path}")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset path missing at: {dataset_path}")
        
    with open(labels_path, "r") as f:
        labels_dict = json.load(f)
    
    print("Loading model for distribution check...")
    model = tf.keras.models.load_model(model_path)
    
    metadata_path = os.path.join(base_dir, "models", "infection_model_metadata.json")
    model_family = "mobilenet"
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                meta = json.load(f)
                model_family = meta.get("model_family", "mobilenet")
        except Exception:
            pass
            
    distribution_results = {}
    total_images_tested = 0
    predictions_count = {labels_dict[k]["infection_category"]: 0 for k in labels_dict}
    
    subdirs = [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]
    
    for subdir in subdirs:
        subdir_path = os.path.join(dataset_path, subdir)
        files = [f for f in os.listdir(subdir_path) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
        
        sample_size = min(30, len(files))
        random.seed(42)
        sampled_files = random.sample(files, sample_size)
        
        distribution_results[subdir] = {
            "tested_count": sample_size,
            "predictions": {}
        }
        
        for file in sampled_files:
            file_path = os.path.join(subdir_path, file)
            with open(file_path, "rb") as f:
                image_bytes = f.read()
            
            processed = preprocess_image(image_bytes, model_family=model_family)
            preds = model(processed, training=False).numpy()[0]
            
            is_softmax = np.isclose(np.sum(preds), 1.0, atol=1e-3)
            if not is_softmax:
                exp_preds = np.exp(preds - np.max(preds))
                preds = exp_preds / np.sum(exp_preds)
                
            pred_idx = np.argmax(preds)
            pred_label = labels_dict[str(pred_idx)]["infection_category"]
            
            predictions_count[pred_label] = predictions_count.get(pred_label, 0) + 1
            distribution_results[subdir]["predictions"][pred_label] = distribution_results[subdir]["predictions"].get(pred_label, 0) + 1
            total_images_tested += 1

    print("\n" + "=" * 50)
    print(" PREDICTION DISTRIBUTION ON RANDOM SAMPLES")
    print("=" * 50)
    for category, count in predictions_count.items():
        percentage = (count / total_images_tested * 100) if total_images_tested > 0 else 0
        print(f"{category}: {count} predictions ({percentage:.2f}%)")
    print("=" * 50 + "\n")
    
    output_data = {
        "total_images_tested": total_images_tested,
        "overall_distribution": predictions_count,
        "detailed_distribution": distribution_results
    }
    
    dist_json_path = os.path.join(results_dir, "prediction_distribution.json")
    with open(dist_json_path, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"Prediction distribution saved to: {dist_json_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test prediction distribution")
    parser.add_argument("--dataset", default="ml/datasets/processed_infection/test", help="Test dataset path")
    args = parser.parse_args()
    test_distribution(args.dataset)
