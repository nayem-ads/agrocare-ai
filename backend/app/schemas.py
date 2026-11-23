from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime

# --- User Schemas ---
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = "farmer"  # farmer or admin

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# --- Report Schemas ---
class ReportResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    crop_name: str
    predicted_class: Optional[str] = None
    disease_name: str
    infection_category: Optional[str] = None
    disease_type: str

    confidence_score: float
    severity_level: str
    severity_score: float
    image_path: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    treatment_advice: str
    prevention_advice: str
    safety_notes: str
    weather_condition: Optional[str] = None
    demo_mode: bool
    model_loaded: bool
    prediction_source: Optional[str] = None
    is_healthy: bool
    plant_subject: Optional[str] = None
    image_hash: Optional[str] = None

    model_version: Optional[str] = None
    model_type: Optional[str] = None
    top_predictions: Optional[List[dict]] = None
    weather_reranked_predictions: Optional[List[dict]] = None

    # Section 10 FYP Fields
    is_unknown: Optional[bool] = False
    unknown_score: Optional[float] = 0.0
    quality_flag: Optional[str] = "PASS"
    quality_score: Optional[float] = 90.0
    retake_hint: Optional[str] = None
    weather_prior_used: Optional[bool] = True
    leaf_area_px: Optional[int] = 32000
    lesion_area_px: Optional[int] = 0
    lesion_mask_path: Optional[str] = None
    gradcam_path: Optional[str] = None
    source_document: Optional[str] = None
    reviewed_by: Optional[str] = None
    officer_status: Optional[str] = "auto_verified"
    district: Optional[str] = None
    upazila: Optional[str] = None

    created_at: datetime

    class Config:
        from_attributes = True


class OfficerReviewSubmit(BaseModel):
    corrected_disease_id: str
    corrected_severity: str
    notes: Optional[str] = None


# --- WeatherRisk Schemas ---
class WeatherRiskResponse(BaseModel):
    id: int
    location: str
    crop_name: str
    risk_level: str
    reason: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Dashboard & Analytics Schemas ---
class DashboardSummary(BaseModel):
    total_reports: int
    most_affected_crop: str
    most_common_disease: str
    high_severity_reports: int
    pending_officer_reviews: Optional[int] = 0
    active_outbreak_alerts: Optional[int] = 0

class CropDistributionItem(BaseModel):
    crop: str
    count: int

class SeverityDistributionItem(BaseModel):
    level: str
    count: int

class DiseaseTypeDistributionItem(BaseModel):
    type: str
    count: int

class MapReportPoint(BaseModel):
    id: int
    latitude: float
    longitude: float
    crop_name: str
    disease_name: str
    severity_level: str
    district: Optional[str] = None
    upazila: Optional[str] = None
    is_unknown: Optional[bool] = False
    created_at: datetime

    class Config:
        from_attributes = True
