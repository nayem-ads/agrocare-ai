import os
# Force demo mode off and real model check on
os.environ["DEMO_MODE"] = "false"
os.environ["REAL_MODEL_REQUIRED"] = "true"

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

def test_prediction_response_integrity():
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
    
    # Run prediction
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
    
    # 5. Check disease type matches label mapping
    disease_type = res_data["disease_type"]
    predicted_class = res_data["predicted_class"]
    assert "Tomato" in predicted_class
    
    # 6. Verify consistent advisory (if not healthy, treatment must not say 'No disease detected')
    is_healthy = res_data["is_healthy"]
    treatment_advice = res_data["treatment_advice"]
    
    if not is_healthy:
        assert "no disease detected" not in treatment_advice.lower()
        # Assert specific treatment contains some active instruction
        assert len(treatment_advice) > 10
    else:
        assert "no disease detected" in treatment_advice.lower()

    # 7. Check plant_subject field formatting
    assert res_data["plant_subject"] == "Tomato Leaf"
