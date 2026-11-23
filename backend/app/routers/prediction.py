import os
import json
import uuid
import shutil
import datetime
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import (
    Report, User, SeverityResult, Explanation, WeatherLog, LocationLog, OutbreakAlert
)
from backend.app.auth import get_optional_user
from backend.ml.inference import predict_disease, compute_image_hash
from backend.ml.quality_gate import evaluate_photo_quality
from backend.app.services.advisory_engine import get_advisory
from backend.app.services.weather_service import get_weather_data, rerank_with_weather_prior
from backend.app.services.map_service import resolve_district_upazila

router = APIRouter(prefix="/api", tags=["Prediction"])

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")


@router.get("/resolve-location")
def resolve_gps_location(lat: Optional[float] = None, lon: Optional[float] = None):
    """
    Resolves GPS coordinates (lat, lon) into Bangladesh District, Upazila,
    PostGIS WKT point, and live BAMIS / Open-Meteo weather metrics.
    """
    c_lat = float(lat) if lat is not None else 23.8103
    c_lon = float(lon) if lon is not None else 90.4125
    district, upazila, wkt = resolve_district_upazila(c_lat, c_lon)
    weather = get_weather_data(c_lat, c_lon)
    return {
        "success": True,
        "latitude": round(c_lat, 5),
        "longitude": round(c_lon, 5),
        "district": district,
        "upazila": upazila,
        "postgis_wkt": wkt,
        "weather": weather
    }


@router.post("/quality-check")
async def precheck_photo_quality(image: UploadFile = File(...)):
    """
    Stage 1 Photo Quality & Automatic Leaf/Crop Detector pre-check endpoint (P0 feature).
    Evaluates blur, brightness, leaf tissue coverage, and auto-detects the crop leaf.
    """
    image_bytes = await image.read()
    q_res = evaluate_photo_quality(image_bytes, filename=image.filename or "")
    return {"success": True, **q_res}


@router.post("/predict")
async def predict_crop_disease(
    image: UploadFile = File(...),
    crop_name: str = Form(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    custom_district: Optional[str] = Form(None),
    custom_upazila: Optional[str] = Form(None),
    language: Optional[str] = Form("en"),
    weather_alpha: Optional[float] = Form(0.35),
    simulate_unknown: Optional[bool] = Form(False),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    # 1. Validate File extension
    file_ext = os.path.splitext(image.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS or not image.content_type.startswith("image/"):
        return {
            "success": False,
            "demo_mode": False,
            "model_loaded": False,
            "error": "Invalid file type. Only PNG, JPG, JPEG, and WEBP images are allowed."
        }

    # Read image content
    image_bytes = await image.read()

    # 2. Validate File size
    if len(image_bytes) > MAX_IMAGE_SIZE:
        return {
            "success": False,
            "demo_mode": False,
            "model_loaded": False,
            "error": "File is too large. Maximum size allowed is 5MB."
        }

    # Reset read pointer for saving later
    await image.seek(0)

    # 3. Compute SHA256 image hash & resolve Auto-Detect crop if requested
    image_hash = compute_image_hash(image_bytes)
    model_version = "agrocare_infection_model_v1"
    if not crop_name or crop_name.strip().lower().startswith("auto"):
        q_auto = evaluate_photo_quality(image_bytes, filename=image.filename or "")
        crop_name = q_auto.get("detected_crop", "Tomato")

    # 4. Check report history for duplicate predictions using same model version & same user
    existing_report = None
    current_uid = current_user.id if current_user else None
    if not simulate_unknown:
        existing_report = db.query(Report).filter(
            Report.image_hash == image_hash,
            Report.crop_name == crop_name,
            Report.model_version == model_version,
            Report.user_id == current_uid
        ).first()

    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        pred = predict_disease(
            image_bytes=image_bytes,
            crop_name=crop_name,
            save_visuals_dir=UPLOAD_DIR,
            visual_prefix=f"{image_hash[:12]}_{crop_name.lower()}"
        )
    except ValueError as e:
        return {
            "success": False,
            "demo_mode": False,
            "model_loaded": False,
            "error": str(e)
        }

    if existing_report:
        rep_model_loaded = existing_report.model_loaded if existing_report.model_loaded is not None else (not existing_report.demo_mode)
        rep_pred_source = existing_report.prediction_source if existing_report.prediction_source else ("Real AI Model" if rep_model_loaded else "Demo Model")
        rep_is_healthy = existing_report.is_healthy if existing_report.is_healthy is not None else (existing_report.disease_type.lower() == "healthy")

        # backfill visual overlays if they were generated on this run
        updated_existing = False
        if not existing_report.lesion_mask_path and pred.get("lesion_mask_path"):
            existing_report.lesion_mask_path = pred.get("lesion_mask_path")
            updated_existing = True
        if not existing_report.gradcam_path and pred.get("gradcam_path"):
            existing_report.gradcam_path = pred.get("gradcam_path")
            updated_existing = True
        if updated_existing:
            db.commit()

        return {
            "success": True,
            "demo_mode": existing_report.demo_mode,
            "model_loaded": rep_model_loaded,
            "prediction_source": rep_pred_source,
            "model_version": existing_report.model_version,
            "model_type": existing_report.model_type,
            "image_hash": existing_report.image_hash,
            "crop_name": existing_report.crop_name,
            "plant_subject": f"{existing_report.crop_name} Leaf",
            "predicted_class": existing_report.predicted_class,
            "detection_result": existing_report.disease_name,
            "disease_name": existing_report.disease_name,
            "infection_category": existing_report.infection_category or existing_report.disease_type,
            "disease_type": existing_report.disease_type,
            "is_healthy": rep_is_healthy,
            "confidence_score": existing_report.confidence_score,
            "severity_level": existing_report.severity_level,
            "severity_score": existing_report.severity_score,
            "top_predictions": existing_report.top_predictions or pred.get("top_predictions", []),
            "weather_reranked_predictions": existing_report.weather_reranked_predictions,
            "is_unknown": existing_report.is_unknown or False,
            "unknown_score": existing_report.unknown_score or 0.0,
            "quality_flag": existing_report.quality_flag or "PASS",
            "quality_score": existing_report.quality_score or 90.0,
            "leaf_area_px": existing_report.leaf_area_px or 32000,
            "lesion_area_px": existing_report.lesion_area_px or 0,
            "lesion_mask_path": existing_report.lesion_mask_path,
            "gradcam_path": existing_report.gradcam_path,
            "source_document": existing_report.source_document,
            "reviewed_by": existing_report.reviewed_by,
            "officer_status": existing_report.officer_status or "auto_verified",
            "district": existing_report.district,
            "upazila": existing_report.upazila,
            "weather_condition": existing_report.weather_condition,
            "latitude": existing_report.latitude,
            "longitude": existing_report.longitude,
            "treatment_advice": existing_report.treatment_advice,
            "prevention_advice": existing_report.prevention_advice,
            "safety_notes": existing_report.safety_notes,
            "report_id": existing_report.id
        }

    # 5. Save uploaded raw image
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    image_relative_path = f"static/uploads/{unique_filename}"

    try:
        # 6. Fetch Open-Meteo / BAMIS weather metrics & compute Stage 4 Weather-Prior Re-ranking (RQ4)
        weather = get_weather_data(latitude, longitude)
        alpha_val = float(weather_alpha) if weather_alpha is not None else 0.35
        all_preds_input = pred.get("all_preds") or pred.get("top_predictions", [])
        weather_reranked, risk_by_disease = rerank_with_weather_prior(
            all_preds=all_preds_input,
            crop_name=pred["crop_name"],
            weather=weather,
            alpha=alpha_val
        )

        # Stage 3 Open-Set status
        open_set = pred.get("open_set", {})
        is_unknown = bool(open_set.get("is_unknown", False)) or bool(simulate_unknown)
        unknown_score = float(open_set.get("unknown_score", 0.0))
        if simulate_unknown:
            unknown_score = max(unknown_score, 0.89)

        quality_gate = pred.get("quality_gate", {})
        sev_details = pred.get("severity_details", {})

        # 7. Fetch source-cited bilingual advisory data (Rule 5 withholds chemicals if is_unknown)
        advisory = get_advisory(
            predicted_class=pred["predicted_class"],
            disease_type=pred["disease_type"],
            severity_level=pred["severity_level"],
            is_healthy=pred["is_healthy"],
            lang=language,
            disease_name=pred["disease_name"],
            is_unknown=is_unknown,
            confidence_score=pred["confidence_score"]
        )

        # Resolve District & Upazila + PostGIS point
        district, upazila, postgis_wkt = resolve_district_upazila(latitude, longitude)
        if custom_district and custom_district.strip():
            district = custom_district.strip()
        if custom_upazila and custom_upazila.strip():
            upazila = custom_upazila.strip()

        # Officer review queue routing: uncertain or High severity cases go to Officer Review Queue
        officer_status = "pending_review" if (is_unknown or pred["severity_level"] == "High") else "auto_verified"

        # 8. Save new Report to AgroCareDB
        pred_source = "Real AI Model" if pred["model_loaded"] else "Demo Model"
        top_preds_str = json.dumps(pred.get("top_predictions", []))
        weather_reranked_str = json.dumps(weather_reranked[:3])

        report = Report(
            user_id=current_user.id if current_user else None,
            crop_name=pred["crop_name"],
            predicted_class=pred["predicted_class"],
            disease_name=pred["disease_name"],
            infection_category=pred["infection_category"],
            disease_type=pred["disease_type"],
            confidence_score=pred["confidence_score"],
            severity_level=pred["severity_level"],
            severity_score=pred["severity_score"],
            image_path=image_relative_path,
            latitude=latitude if latitude is not None else 23.8103,
            longitude=longitude if longitude is not None else 90.4125,
            treatment_advice=advisory["treatment_advice"],
            prevention_advice=advisory["prevention_advice"],
            safety_notes=advisory["safety_notes"],
            weather_condition=f"{weather['temperature']}°C, {weather['humidity']}% RH, {weather['condition']}",
            demo_mode=pred["demo_mode"],
            model_loaded=pred["model_loaded"],
            prediction_source=pred_source,
            is_healthy=pred["is_healthy"],
            image_hash=image_hash if not simulate_unknown else f"{image_hash}_unk",
            model_version=model_version,
            top_predictions_json=top_preds_str,
            top3_json=top_preds_str,
            weather_reranked_json=weather_reranked_str,
            is_unknown=is_unknown,
            unknown_score=unknown_score,
            quality_flag=quality_gate.get("quality_flag", "PASS"),
            quality_score=quality_gate.get("quality_score", 90.0),
            retake_hint=quality_gate.get("retake_hint_bn" if language == "bn" else "retake_hint_en"),
            model_version_id=2,
            weather_prior_used=(alpha_val > 0),
            leaf_area_px=sev_details.get("leaf_area_px", 32000),
            lesion_area_px=sev_details.get("lesion_area_px", 0),
            lesion_mask_path=pred.get("lesion_mask_path"),
            gradcam_path=pred.get("gradcam_path"),
            source_document=advisory.get("source_document"),
            reviewed_by=advisory.get("reviewed_by"),
            officer_status=officer_status,
            district=district,
            upazila=upazila
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        # 9. Populate Section 10 audit tables (severity_results, explanations, weather_logs, location_logs)
        try:
            db.add(SeverityResult(
                report_id=report.id,
                leaf_area_px=report.leaf_area_px,
                lesion_area_px=report.lesion_area_px,
                severity_pct=report.severity_score,
                severity_level=report.severity_level,
                mask_path=report.lesion_mask_path
            ))
            db.add(Explanation(
                report_id=report.id,
                gradcam_path=report.gradcam_path,
                method="Grad-CAM Spatial Activation"
            ))
            db.add(WeatherLog(
                report_id=report.id,
                forecast_json=json.dumps(weather),
                risk_by_disease_json=json.dumps(risk_by_disease),
                source=weather.get("source", "Open-Meteo API + BAMIS")
            ))
            db.add(LocationLog(
                report_id=report.id,
                latitude=report.latitude,
                longitude=report.longitude,
                geography_point=postgis_wkt,
                district=district,
                upazila=upazila
            ))

            # Check Outbreak Alert cluster threshold (>= 3 High severity reports in same district within 7 days)
            if report.severity_level == "High" and not report.is_healthy:
                seven_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
                cluster_cnt = db.query(Report).filter(
                    Report.district == district,
                    Report.disease_name == report.disease_name,
                    Report.severity_level == "High",
                    Report.created_at >= seven_days_ago
                ).count()
                if cluster_cnt >= 3:
                    area_label = f"{district} ({upazila})"
                    existing_alert = db.query(OutbreakAlert).filter(
                        OutbreakAlert.area == area_label,
                        OutbreakAlert.disease_name == report.disease_name,
                        OutbreakAlert.status == "Active"
                    ).first()
                    if existing_alert:
                        existing_alert.case_count = cluster_cnt
                    else:
                        db.add(OutbreakAlert(
                            disease_id=pred.get("disease_code", report.predicted_class or "Disease"),
                            disease_name=report.disease_name,
                            crop_name=report.crop_name,
                            area=area_label,
                            case_count=cluster_cnt,
                            window_days=7,
                            status="Active",
                            advisory_note=f"Cluster of {cluster_cnt} High-Severity {report.disease_name} cases detected in {area_label} within 7 days."
                        ))
            db.commit()
        except Exception as audit_err:
            db.rollback()
            print(f"[WARN] Non-fatal audit table log issue: {audit_err}")

        return {
            "success": True,
            "demo_mode": pred["demo_mode"],
            "model_loaded": pred["model_loaded"],
            "prediction_source": pred_source,
            "model_version": model_version,
            "model_type": pred["model_type"],
            "image_hash": image_hash,
            "crop_name": pred["crop_name"],
            "plant_subject": f"{pred['crop_name']} Leaf",
            "predicted_class": pred["predicted_class"],
            "detection_result": pred["disease_name"],
            "disease_name": pred["disease_name"],
            "infection_category": pred["infection_category"],
            "disease_type": pred["disease_type"],
            "is_healthy": pred["is_healthy"],
            "confidence_score": pred["confidence_score"],
            "severity_level": pred["severity_level"],
            "severity_score": pred["severity_score"],
            "top_predictions": pred.get("top_predictions", []),
            "weather_reranked_predictions": weather_reranked[:3],
            "is_unknown": report.is_unknown,
            "unknown_score": report.unknown_score,
            "quality_flag": report.quality_flag,
            "quality_score": report.quality_score,
            "retake_hint": report.retake_hint,
            "leaf_area_px": report.leaf_area_px,
            "lesion_area_px": report.lesion_area_px,
            "lesion_mask_path": report.lesion_mask_path,
            "gradcam_path": report.gradcam_path,
            "source_document": report.source_document,
            "reviewed_by": report.reviewed_by,
            "officer_status": report.officer_status,
            "district": report.district,
            "upazila": report.upazila,
            "weather_condition": report.weather_condition,
            "latitude": report.latitude,
            "longitude": report.longitude,
            "treatment_advice": advisory["treatment_advice"],
            "prevention_advice": advisory["prevention_advice"],
            "safety_notes": advisory["safety_notes"],
            "report_id": report.id
        }

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return {
            "success": False,
            "demo_mode": False,
            "model_loaded": False,
            "error": f"An error occurred during diagnosis: {str(e)}"
        }


@router.get("/model/status")
def get_model_status():
    from backend.ml.model_loader import get_model_status_info
    return get_model_status_info()
