import os
# Force environment variables before importing any config/loader modules to prevent caching issues
os.environ["MODEL_PATH"] = "backend/ml/models/agrocare_infection_model.keras"
os.environ["LABELS_PATH"] = "backend/ml/infection_labels.json"
os.environ["FALLBACK_MODEL_PATH"] = "backend/ml/models/agrocare_infection_model.h5"

import argparse
import numpy as np
from PIL import Image
import tensorflow as tf
from backend.ml.model_loader import load_agrocare_model
from backend.ml.preprocessing import preprocess_image
from backend.ml.severity import estimate_severity
from backend.app.services.advisory_engine import get_advisory

def test_infection_image(image_path: str):
    """
    Classifies a single image and prints Broad Infection Category diagnostic outputs.
    """
    if not os.path.exists(image_path):
        print(f"Error: Target image file not found at: {image_path}")
        return
        
    print(f"Loading image: {image_path}")
    
    # Load model and labels
    model, labels, model_loaded = load_agrocare_model()
    if not model_loaded:
        print("Error: Real trained infection model could not be loaded. Please run model training first.")
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
        
    # Build predictions list
    preds_list = []
    for idx, prob in enumerate(predictions):
        meta = labels[str(idx)]
        preds_list.append({
            "idx": idx,
            "class_name": meta["class_name"],
            "infection_category": meta["infection_category"],
            "confidence": float(prob)
        })
        
    # Sort by probability descending
    preds_list.sort(key=lambda x: x["confidence"], reverse=True)
    
    # Final prediction
    top_pred = preds_list[0]
    conf = top_pred["confidence"]
    cat_meta = labels[str(top_pred["idx"])]
    
    severity_level, severity_score = estimate_severity(image_bytes, conf)
    
    # Fetch advisory notes
    advisory = get_advisory(
        predicted_class=cat_meta["class_name"],
        disease_type=cat_meta["infection_category"],
        severity_level=severity_level,
        is_healthy=cat_meta["is_healthy"],
        lang="en"
    )
    
    # Print results
    print("\n" + "=" * 50)
    print(" INFECTION DIAGNOSIS RESULTS")
    print("=" * 50)
    print(f"Model Loaded:       {'Yes' if model_loaded else 'No'}")
    print(f"Infection Category: {cat_meta['infection_category']}")
    print(f"Confidence Score:   {conf * 100:.2f}%")
    print(f"Severity Level:     {severity_level} ({severity_score}% affected)")
    
    print("\nTop 3 Softmax Predictions:")
    for i, item in enumerate(preds_list[:3]):
        print(f"  {i+1}. {item['infection_category']}: {item['confidence'] * 100:.2f}%")
        
    print("\nAdvisory Details:")
    print(f"  Treatment:  {advisory['treatment_advice']}")
    print(f"  Prevention: {advisory['prevention_advice']}")
    print(f"  Safety:     {advisory['safety_notes']}")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgroCare AI Infection Model Single Image Evaluator")
    parser.add_argument("--image", required=True, help="Path to leaf image file")
    
    args = parser.parse_args()
    test_infection_image(args.image)
