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

def test_real_prediction_determinism():
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
    
    # First Upload
    response1 = client.post("/api/predict", files=files, data=data)
    assert response1.status_code == 200
    res_data1 = response1.json()
    assert res_data1["success"] is True, f"Prediction failed with: {res_data1.get('error')}"
    assert res_data1["demo_mode"] is False
    assert res_data1["model_loaded"] is True
    
    # Second Upload
    files2 = {"image": ("dummy.jpg", dummy_image_data, "image/jpeg")}
    response2 = client.post("/api/predict", files=files2, data=data)
    assert response2.status_code == 200
    res_data2 = response2.json()
    assert res_data2["success"] is True
    assert res_data2["demo_mode"] is False
    assert res_data2["model_loaded"] is True
    
    # Assert exact matched determinism
    assert res_data1["crop_name"] == res_data2["crop_name"]
    assert res_data1["predicted_class"] == res_data2["predicted_class"]
    assert res_data1["disease_name"] == res_data2["disease_name"]
    assert res_data1["confidence_score"] == res_data2["confidence_score"]
    assert res_data1["severity_level"] == res_data2["severity_level"]
    assert res_data1["top_predictions"] == res_data2["top_predictions"]
