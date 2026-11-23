import os
# Force environment variables before any config/loader imports
os.environ["DEMO_MODE"] = "true"
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

def test_prediction_consistency():
    # 1. Generate valid 224x224 JPEG leaf image dynamically
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    dummy_image_data = img_byte_arr.getvalue()
    
    responses = []
    
    # 2. Diagnose same image 5 times consecutively
    for i in range(5):
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
        assert res_data["success"] is True
        responses.append(res_data)
        
    # 3. Assert all predictions, confidence levels, and severity classifications align exactly
    first = responses[0]
    for r in responses[1:]:
        assert r["crop_name"] == first["crop_name"]
        assert r["predicted_class"] == first["predicted_class"]
        assert r["disease_name"] == first["disease_name"]
        assert r["disease_type"] == first["disease_type"]
        assert r["confidence_score"] == first["confidence_score"]
        assert r["severity_level"] == first["severity_level"]
        assert r["severity_score"] == first["severity_score"]
        assert r["top_predictions"] == first["top_predictions"]
