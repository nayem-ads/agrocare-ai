import os
import argparse
import numpy as np
from PIL import Image
import tensorflow as tf
from backend.ml.model_loader import load_agrocare_model
from backend.ml.preprocessing import preprocess_image
from backend.ml.severity import estimate_severity

def test_single_image(image_path: str, crop_name: str):
    """
    Runs model inference on a single image and prints diagnostic outputs.
    """
    if not os.path.exists(image_path):
        print(f"Error: Target image file not found at: {image_path}")
        return
        
    print(f"Loading single image: {image_path}")
    print(f"Target crop: {crop_name}")
    
    # 1. Load model and labels
    model, labels, model_loaded = load_agrocare_model()
    if not model_loaded:
        print("Error: Real trained model could not be loaded. Please run model training first.")
        return
        
    # 2. Preprocess image
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            
        processed_img = preprocess_image(image_bytes)
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return
        
    # 3. Model inference
    try:
        predictions = model(processed_img, training=False).numpy()[0]
    except Exception as e:
        print(f"Error during model inference: {e}")
        return
        
    # 4. Filter by crop
    crop_clean = crop_name.strip().lower()
    matching_indices = [
        int(k) for k, v in labels.items()
        if v["crop_name"].lower() == crop_clean
    ]
    
    if not matching_indices:
        print(f"Error: Crop '{crop_name}' is not supported by the current trained model.")
        print(f"Available crops: {list(set([v['crop_name'] for v in labels.values()]))}")
        return
        
    filtered_preds = [
        {"idx": idx, "prob": float(predictions[idx])}
        for idx in matching_indices
    ]
    filtered_preds.sort(key=lambda x: x["prob"], reverse=True)
    
    # Final prediction
    top_idx = filtered_preds[0]["idx"]
    confidence = filtered_preds[0]["prob"]
    meta = labels[str(top_idx)]
    
    severity_level, severity_score = estimate_severity(image_bytes, confidence)
    
    # Print results
    print("\n" + "=" * 50)
    print(" INFERENCE RESULTS")
    print("=" * 50)
    print(f"Predicted Class:   {meta['class_name']}")
    print(f"Disease Name:      {meta['disease_name']}")
    print(f"Crop Name:         {meta['crop_name']}")
    print(f"Confidence Score:  {confidence * 100:.2f}%")
    print(f"Severity Level:    {severity_level} ({severity_score}% affected)")
    
    print("\nTop 3 Crop-Filtered Softmax Predictions:")
    for i, item in enumerate(filtered_preds[:3]):
        cls_name = labels[str(item["idx"])]["class_name"]
        print(f"  {i+1}. {cls_name}: {item['prob'] * 100:.2f}%")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgroCare AI Single Image Evaluator")
    parser.add_argument("--image", required=True, help="Path to leaf image file")
    parser.add_argument("--crop", required=True, help="Crop type (e.g. Tomato, Rice, Potato)")
    
    args = parser.parse_args()
    test_single_image(args.image, args.crop)
