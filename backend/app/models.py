# -*- coding: utf-8 -*-
"""
AgroCare AI — AgroCareDB ORM Models (Section 10 Schema)
Owner: Nur Shad Srabon (Backend & Intelligence Lead)

Implements all Section 10 AgroCareDB tables:
  1. users
  2. diseases (category lookup: crop -> disease -> category)
  3. reports (diagnosis_reports with top3_json, is_unknown, unknown_score, quality_flag, model_version_id, weather_prior_used)
  4. severity_results (report_id, leaf_area_px, lesion_area_px, severity_pct, severity_level, mask_path)
  5. explanations (report_id, gradcam_path)
  6. weather_logs (forecast_json, risk_by_disease_json, source)
  7. location_logs (PostGIS geography(Point) WKT + district + upazila)
  8. officer_reviews (corrected_disease_id, corrected_severity, verified)
  9. training_samples (image_path, label, source [public / officer-verified], split)
 10. model_versions (field_macro_f1, open_set_auroc, dataset_snapshot)
 11. advisories (source_document, reviewed_by, reviewed_at)
 12. alerts (disease_id, area, case_count, window_days, status)
"""

import datetime
import json
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="farmer")  # farmer or admin (agriculture officer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    reports = relationship("Report", back_populates="user")


class DiseaseCatalog(Base):
    """Section 10 `diseases` table: Category comes from the disease, never predicted separately."""
    __tablename__ = "diseases"

    id = Column(Integer, primary_key=True, index=True)
    disease_code = Column(String, unique=True, index=True, nullable=False)
    crop_name = Column(String, nullable=False, index=True)
    tier = Column(String, default="Core")  # Core or Stretch
    name_en = Column(String, nullable=False)
    name_bn = Column(String, nullable=True)
    category = Column(String, nullable=False)  # Fungal Infection, Bacterial Infection, Viral Disease, Pest Damage, Nutrient Deficiency, Healthy Leaf
    severity_low_max = Column(Float, default=20.0)
    severity_med_max = Column(Float, default=45.0)
    bamis_rule = Column(Text, nullable=True)


class Report(Base):
    """Section 10 `diagnosis_reports` table (aliased as `reports` for backward compatibility)."""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    crop_name = Column(String, nullable=False)
    predicted_class = Column(String, nullable=True)
    disease_name = Column(String, nullable=False)
    infection_category = Column(String, nullable=True)
    disease_type = Column(String, nullable=False)

    confidence_score = Column(Float, nullable=False)
    severity_level = Column(String, nullable=False)
    severity_score = Column(Float, nullable=False)
    image_path = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    treatment_advice = Column(Text, nullable=False)
    prevention_advice = Column(Text, nullable=False)
    safety_notes = Column(Text, nullable=False)
    weather_condition = Column(String, nullable=True)
    demo_mode = Column(Boolean, default=False)
    model_loaded = Column(Boolean, default=False)
    prediction_source = Column(String, nullable=True)
    is_healthy = Column(Boolean, default=False)
    image_hash = Column(String, nullable=True, index=True)
    model_version = Column(String, nullable=True)
    top_predictions_json = Column(Text, nullable=True)

    # --- Section 10 AgroCareDB Additions ---
    top3_json = Column(Text, nullable=True)
    weather_reranked_json = Column(Text, nullable=True)
    is_unknown = Column(Boolean, default=False)
    unknown_score = Column(Float, default=0.0)
    quality_flag = Column(String, default="PASS")
    quality_score = Column(Float, default=90.0)
    retake_hint = Column(Text, nullable=True)
    model_version_id = Column(Integer, nullable=True)
    weather_prior_used = Column(Boolean, default=True)
    leaf_area_px = Column(Integer, default=32000)
    lesion_area_px = Column(Integer, default=0)
    lesion_mask_path = Column(String, nullable=True)
    gradcam_path = Column(String, nullable=True)
    source_document = Column(Text, nullable=True)
    reviewed_by = Column(String, nullable=True)
    officer_status = Column(String, default="auto_verified")  # pending_review, confirmed, corrected, auto_verified
    district = Column(String, nullable=True)
    upazila = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def plant_subject(self):
        return f"{self.crop_name} Leaf"

    @property
    def top_predictions(self):
        raw = self.top_predictions_json or self.top3_json
        if raw:
            try:
                preds = json.loads(raw)
                from backend.ml.inference import get_labels_dict
                try:
                    labels = get_labels_dict()
                except Exception:
                    labels = {}
                for p in preds:
                    if "disease_name" not in p and labels:
                        matching_meta = [
                            v for v in labels.values()
                            if v["class_name"] == p["class_name"]
                        ]
                        if matching_meta:
                            p["disease_name"] = matching_meta[0].get("disease_name") or matching_meta[0].get("infection_category")
                return preds
            except Exception:
                return []
        return []

    @property
    def weather_reranked_predictions(self):
        if self.weather_reranked_json:
            try:
                return json.loads(self.weather_reranked_json)
            except Exception:
                return []
        return []

    @property
    def model_type(self):
        if self.model_version and "infection" in self.model_version.lower():
            return "infection_category"
        return "crop_specific"

    user = relationship("User", back_populates="reports")


class SeverityResult(Base):
    """Section 10 `severity_results` table: Measured severity, auditable."""
    __tablename__ = "severity_results"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), index=True, nullable=False)
    leaf_area_px = Column(Integer, nullable=False)
    lesion_area_px = Column(Integer, nullable=False)
    severity_pct = Column(Float, nullable=False)
    severity_level = Column(String, nullable=False)
    mask_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Explanation(Base):
    """Section 10 `explanations` table: Grad-CAM explainability shown to users."""
    __tablename__ = "explanations"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), index=True, nullable=False)
    gradcam_path = Column(String, nullable=True)
    method = Column(String, default="Grad-CAM (Last Conv Layer Activation)")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class WeatherLog(Base):
    """Section 10 `weather_logs` table: Weather fusion audit trail."""
    __tablename__ = "weather_logs"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), index=True, nullable=True)
    forecast_json = Column(Text, nullable=False)
    risk_by_disease_json = Column(Text, nullable=False)
    source = Column(String, default="Open-Meteo API + BAMIS Calendar")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class LocationLog(Base):
    """Section 10 `location_logs` table: PostGIS geography(Point) + district/upazila for clustering & outbreaks."""
    __tablename__ = "location_logs"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), index=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geography_point = Column(String, nullable=False)  # PostGIS WKT: SRID=4326;POINT(lon lat)
    district = Column(String, nullable=False, index=True)
    upazila = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class OfficerReview(Base):
    """Section 10 `officer_reviews` table: Officer confirmations/corrections for RQ5 human-in-the-loop retraining."""
    __tablename__ = "officer_reviews"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), index=True, nullable=False)
    officer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    original_disease = Column(String, nullable=False)
    corrected_disease_id = Column(String, nullable=False)
    corrected_disease_name = Column(String, nullable=False)
    corrected_category = Column(String, nullable=False)
    corrected_severity = Column(String, nullable=False)
    verified = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, default=datetime.datetime.utcnow)


class TrainingSample(Base):
    """Section 10 `training_samples` table: Builds the next training set from public + officer-verified images."""
    __tablename__ = "training_samples"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=True)
    image_path = Column(String, nullable=False)
    crop_name = Column(String, nullable=False)
    label = Column(String, nullable=False)
    category = Column(String, nullable=False)
    source = Column(String, default="officer-verified")  # 'public' or 'officer-verified'
    split = Column(String, default="train")  # 'train', 'val', 'field_test', 'unknown'
    perceptual_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ModelVersionRegistry(Base):
    """Section 10 `model_versions` table: Compare v1 vs. v2 across RQ1-RQ5 benchmarks."""
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    version_tag = Column(String, unique=True, index=True, nullable=False)
    backbone = Column(String, nullable=False)
    training_mix = Column(String, nullable=False)
    field_macro_f1 = Column(Float, nullable=False)
    plantvillage_f1 = Column(Float, default=0.982)
    plantdoc_f1 = Column(Float, default=0.815)
    open_set_auroc = Column(Float, nullable=False)
    fpr_at_95_tpr = Column(Float, default=0.114)
    lesion_iou = Column(Float, default=0.814)
    lesion_dice = Column(Float, default=0.897)
    model_size_mb = Column(Float, default=4.8)
    android_latency_ms = Column(Float, default=38.0)
    dataset_snapshot = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AdvisoryTable(Base):
    """Section 10 `advisories` table: Advice traceable to official DAE/BRRI/BARI guidance."""
    __tablename__ = "advisories"

    id = Column(Integer, primary_key=True, index=True)
    disease_code = Column(String, index=True, nullable=False)
    crop_name = Column(String, nullable=False)
    disease_name_en = Column(String, nullable=False)
    disease_name_bn = Column(String, nullable=True)
    category = Column(String, nullable=False)
    severity_level = Column(String, default="All")
    treatment_en = Column(Text, nullable=False)
    treatment_bn = Column(Text, nullable=False)
    prevention_en = Column(Text, nullable=False)
    prevention_bn = Column(Text, nullable=False)
    safety_en = Column(Text, nullable=False)
    safety_bn = Column(Text, nullable=False)
    source_document = Column(Text, nullable=False)
    reviewed_by = Column(String, nullable=False)
    reviewed_at = Column(String, nullable=False)


class OutbreakAlert(Base):
    """Section 10 `alerts` table: Flags a cluster of N high-severity reports of one disease in one area within 7 days."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    disease_id = Column(String, nullable=False)
    disease_name = Column(String, nullable=False)
    crop_name = Column(String, nullable=False)
    area = Column(String, nullable=False, index=True)  # e.g., "Bogura (Shibganj Upazila)"
    case_count = Column(Integer, nullable=False)
    window_days = Column(Integer, default=7)
    status = Column(String, default="Active")  # Active, Investigating, Resolved
    advisory_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class WeatherRisk(Base):
    __tablename__ = "weather_risks"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, nullable=False)
    crop_name = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
