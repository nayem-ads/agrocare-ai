import os
# Force environment variables before any config/loader imports
os.environ["DEMO_MODE"] = "false"
os.environ["REAL_MODEL_REQUIRED"] = "true"
os.environ["MODEL_PATH"] = "backend/ml/models/agrocare_infection_model.keras"
os.environ["LABELS_PATH"] = "backend/ml/infection_labels.json"
os.environ["FALLBACK_MODEL_PATH"] = "backend/ml/models/agrocare_infection_model.h5"

import json
import pytest
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
from backend.ml.model_loader import load_agrocare_model

client = TestClient(app)

def test_model_files_exist():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, "ml", "models", "agrocare_infection_model.keras")
    fallback_path = os.path.join(base_dir, "ml", "models", "agrocare_infection_model.h5")
    labels_path = os.path.join(base_dir, "ml", "infection_labels.json")
    
    assert os.path.exists(model_path) or os.path.exists(fallback_path)
    assert os.path.exists(labels_path)

def test_model_loading_helper():
    model, labels, loaded = load_agrocare_model()
    assert loaded is True
    assert model is not None
    assert labels is not None

def test_model_status_endpoint():
    # Force settings mock directly to prevent environment bleed
    from backend.app.config import settings
    settings.DEMO_MODE = False
    settings.MODEL_PATH = "backend/ml/models/agrocare_infection_model.keras"
    settings.LABELS_PATH = "backend/ml/infection_labels.json"
    
    response = client.get("/api/model/status")
    assert response.status_code == 200
    data = response.json()
    assert data["model_loaded"] is True
    assert data["demo_mode"] is False
    assert data["labels_loaded"] is True
    assert data["number_of_classes"] > 0
