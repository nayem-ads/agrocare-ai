import os
os.environ["DEMO_MODE"] = "false"
os.environ["REAL_MODEL_REQUIRED"] = "true"
os.environ["DISABLE_EXTERNAL_WEATHER"] = "true"
os.environ["MODEL_PATH"] = "backend/ml/models/agrocare_infection_model.keras"
os.environ["LABELS_PATH"] = "backend/ml/infection_labels.json"
os.environ["FALLBACK_MODEL_PATH"] = "backend/ml/models/agrocare_infection_model.h5"

import io
from PIL import Image
from fastapi.testclient import TestClient

from backend.app.database import engine, Base, SessionLocal
from backend.app.main import app, seed_users_and_reports

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    seed_users_and_reports(db)
finally:
    db.close()

client = TestClient(app)


def test_rq1_to_rq5_research_benchmarks_endpoint():
    resp = client.get("/api/research-benchmarks")
    assert resp.status_code == 200
    data = resp.json()
    assert "rq1_cross_domain_benchmark" in data
    assert len(data["rq1_cross_domain_benchmark"]["runs_table"]) == 5
    assert "rq2_open_set_rejection" in data
    assert "rq3_severity_segmentation" in data
    assert "rq4_weather_and_ablations" in data
    assert "rq5_hitl_retraining" in data
    assert "faculty_defense_qa" in data


def test_photo_quality_gate_endpoint():
    # Dark non-leaf image should be flagged by Stage 1 Quality Gate
    dark_img = Image.new("RGB", (224, 224), color=(8, 8, 8))
    buf = io.BytesIO()
    dark_img.save(buf, format="JPEG")
    files = {"image": ("dark.jpg", buf.getvalue(), "image/jpeg")}
    resp = client.post("/api/quality-check", files=files)
    assert resp.status_code == 200
    q = resp.json()
    assert q["passed"] is False
    assert q["quality_flag"] == "TOO_DARK"
    assert len(q["retake_hint_bn"]) > 5


def test_open_set_rejection_withholds_chemicals():
    # Test RQ2 & Section 9 Rule 5: Open-set unknown case routes to officer & withholds chemical advice
    img = Image.new("RGB", (224, 224), color=(40, 140, 40))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    files = {"image": ("unknown_test.jpg", buf.getvalue(), "image/jpeg")}
    data = {
        "crop_name": "Tomato",
        "latitude": 24.8481,
        "longitude": 89.3730,
        "language": "en",
        "simulate_unknown": "true"
    }
    resp = client.post("/api/predict", files=files, data=data)
    assert resp.status_code == 200
    res = resp.json()
    assert res["success"] is True
    assert res["is_unknown"] is True
    assert res["officer_status"] == "pending_review"
    assert "officer" in res["treatment_advice"].lower()
    assert res["lesion_mask_path"] is not None
    assert res["gradcam_path"] is not None
    assert res["leaf_area_px"] > 0
    assert isinstance(res["weather_reranked_predictions"], list)
