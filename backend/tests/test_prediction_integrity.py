import os
# Force environment variables before any config/loader imports
os.environ["DEMO_MODE"] = "false"
os.environ["REAL_MODEL_REQUIRED"] = "true"
os.environ["MODEL_PATH"] = "backend/ml/models/agrocare_infection_model.keras"
os.environ["LABELS_PATH"] = "backend/ml/infection_labels.json"
os.environ["FALLBACK_MODEL_PATH"] = "backend/ml/models/agrocare_infection_model.h5"


import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from backend.app.database import engine, Base, SessionLocal
from backend.app.main import seed_users_and_reports
# Initialize database tables and seed users
Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    seed_users_and_reports(db)
finally:
    db.close()

from backend.app.main import app
client = TestClient(app)

def test_prediction_integrity():
    # 1. Generate valid 224x224 JPEG leaf image dynamically
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    dummy_image_data = img_byte_arr.getvalue()
    
    files = {"image": ("dummy.jpg", dummy_image_data, "image/jpeg")}
    data = {
        "crop_name": "Tomato",
        "latitude": 23.8103,
        "longitude": 90.4125,
        "language": "en"
    }
    
    # Run prediction API
    response = client.post("/api/predict", files=files, data=data)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True, f"Prediction failed with: {res_data.get('error')}"
    
    # 2. Check model loaded status
    assert res_data["model_loaded"] is True
    assert res_data["prediction_source"] == "Real AI Model"
    
    # 3. Check confidence range (must be greater than 0 and <= 1)
    confidence = res_data["confidence_score"]
    assert isinstance(confidence, float)
    assert 0.0 < confidence <= 1.0
    
    # 4. Check top predictions details
    top_preds = res_data["top_predictions"]
    assert isinstance(top_preds, list)
    assert len(top_preds) >= 3
    
    # Top prediction confidence must match confidence_score
    assert top_preds[0]["confidence"] == confidence
    
    # 5. Check infection_category validity
    infection_category = res_data["infection_category"]
    valid_categories = [
        "Fungal Infection",
        "Bacterial Infection",
        "Viral Disease",
        "Pest Damage",
        "Nutrient Deficiency",
        "Healthy Leaf"
    ]
    assert infection_category in valid_categories
    
    # 6. Verify consistent advisory (if not healthy, treatment must not say 'No disease detected')
    is_healthy = res_data["is_healthy"]
    treatment_advice = res_data["treatment_advice"]
    
    if not is_healthy:
        assert "no disease detected" not in treatment_advice.lower()
        assert len(treatment_advice) > 10
    else:
        assert "no disease detected" in treatment_advice.lower()

    # 7. Check that report details show the same saved values
    report_id = res_data["report_id"]
    rep_response = client.get(f"/api/reports/{report_id}")
    assert rep_response.status_code == 200
    rep_data = rep_response.json()
    
    assert rep_data["crop_name"] == res_data["crop_name"]
    assert rep_data["disease_name"] == res_data["disease_name"]
    assert rep_data["infection_category"] == res_data["infection_category"]
    assert rep_data["confidence_score"] == res_data["confidence_score"]
    assert rep_data["treatment_advice"] == res_data["treatment_advice"]
    assert rep_data["prevention_advice"] == res_data["prevention_advice"]
    assert rep_data["safety_notes"] == res_data["safety_notes"]
    assert rep_data["model_type"] == "infection_category"

def test_prediction_rice_accepted():
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    dummy_image_data = img_byte_arr.getvalue()
    
    files = {"image": ("dummy.jpg", dummy_image_data, "image/jpeg")}
    data = {
        "crop_name": "Rice",
        "latitude": 23.8103,
        "longitude": 90.4125,
        "language": "en"
    }
    
    response = client.post("/api/predict", files=files, data=data)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True, f"Prediction failed with: {res_data.get('error')}"
    assert res_data["crop_name"] == "Rice"
    assert res_data["model_type"] == "infection_category"

