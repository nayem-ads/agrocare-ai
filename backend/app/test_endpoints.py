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
# Initialize database tables and seed users before app import
Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    seed_users_and_reports(db)
finally:
    db.close()

from backend.app.main import app
client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

def test_labels():
    response = client.get("/api/labels")
    assert response.status_code == 200
    data = response.json()
    assert "0" in data
    assert data["0"]["class_name"] == "Bacterial_Infection"


def test_demo_sample():
    response = client.get("/api/demo-sample")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["disease_name"] == "Late Blight"

def test_auth_login():
    response = client.post(
        "/api/auth/login",
        json={"email": "farmer@agrocare.ai", "password": "farmer123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "farmer@agrocare.ai"
    assert data["user"]["role"] == "farmer"

def test_prediction_endpoint():
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
    
    response = client.post("/api/predict", files=files, data=data)
    assert response.status_code == 200
    
    res_data = response.json()
    assert res_data["success"] is True
    assert "demo_mode" in res_data
    assert res_data["crop_name"] == "Tomato"
    assert "disease_name" in res_data
    assert "treatment_advice" in res_data
