import os
import json
import random
import numpy as np
import tensorflow as tf
from backend.app.config import settings

# Global thread-safe cache
_model = None
_labels = None
_model_loaded = False
_initialized = False
_metadata = {}

def init_deterministic_seeds():
    """
    Sets all environment seeds to ensure reproducibility of predictions.
    """
    random.seed(42)
    np.random.seed(42)
    tf.random.set_seed(42)
    try:
        tf.config.experimental.enable_op_determinism()
    except Exception:
        pass

def load_agrocare_model(force_reload: bool = False) -> tuple:
    """
    Loads the trained Keras model (checks .keras first, then .h5) and labels.json.
    Returns:
        tuple (model, labels, model_loaded)
    """
    global _model, _labels, _model_loaded, _initialized, _metadata
    
    if _initialized and not force_reload:
        return _model, _labels, _model_loaded
        
    init_deterministic_seeds()
    
    model_path = settings.MODEL_PATH
    fallback_model_path = settings.FALLBACK_MODEL_PATH
    labels_path = settings.LABELS_PATH
    
    # Resolve relative paths anchored to the location of model_loader.py (backend/ml/)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    def resolve_rel_path(path_str: str) -> str:
        if os.path.isabs(path_str):
            return path_str
        # Strip redundant folder prefixes
        clean_path = path_str.replace("backend/ml/", "").replace("backend/", "")
        return os.path.abspath(os.path.join(base_dir, clean_path))
        
    model_path = resolve_rel_path(model_path)
    fallback_model_path = resolve_rel_path(fallback_model_path)
    labels_path = resolve_rel_path(labels_path)

        
    # Check model path existence: keras file takes priority, falls back to .h5
    active_model_path = None
    if os.path.exists(model_path):
        active_model_path = model_path
    elif os.path.exists(fallback_model_path):
        active_model_path = fallback_model_path
        
    print(f"AgroCare AI Model Loader checking paths:\nModel Path: {active_model_path}\nLabels: {labels_path}")
    
    # 1. Load labels independently (required for demo predictions if model is missing)
    if os.path.exists(labels_path):
        try:
            with open(labels_path, "r") as f:
                _labels = json.load(f)
            print("Class labels configuration loaded successfully.")
        except Exception as e:
            print(f"Error loading labels file: {e}")
            _labels = None
    else:
        print(f"Labels configuration file is missing at: {labels_path}")
        _labels = None
        
    # 2. Load model metadata
    metadata_path = os.path.join(os.path.dirname(labels_path), "models", "infection_model_metadata.json")
    if not os.path.exists(metadata_path):
        metadata_path = os.path.join(os.path.dirname(labels_path), "models", "model_metadata.json")
        
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                _metadata = json.load(f)
            print("Model metadata file loaded successfully.")
        except Exception as e:
            print(f"Error loading metadata JSON: {e}")
            _metadata = {}
    else:
        _metadata = {}


    # 3. Load Keras Model if model file exists
    if active_model_path is not None and _labels is not None:
        try:
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            _model = tf.keras.models.load_model(active_model_path)
            _model_loaded = True
            print(f"Production ML model loaded successfully from: {active_model_path}")
        except Exception as e:
            print(f"Error loading Keras model: {e}")
            _model = None
            _model_loaded = False
    else:
        if active_model_path is None:
            print("Production model file is missing (both .keras and .h5 paths checked).")
        _model = None
        _model_loaded = False
        
    _initialized = True
    return _model, _labels, _model_loaded

def get_model_metadata() -> dict:
    global _metadata
    load_agrocare_model()
    return _metadata

def get_model_status_info() -> dict:
    """
    Returns diagnostic details about the active model.
    """
    global _metadata
    _, labels, loaded = load_agrocare_model()
    num_classes = len(labels) if labels else 0
    
    # Load dataset summary to identify missing/low-data categories and class_counts
    missing_categories = []
    class_counts = {}
    base_dir = os.path.dirname(os.path.abspath(__file__))
    summary_path = os.path.abspath(os.path.join(base_dir, "results", "infection_dataset_summary.json"))
    
    if os.path.exists(summary_path):
        try:
            with open(summary_path, "r") as f:
                ds_summary = json.load(f)
            for cat_name, status in ds_summary.get("categories_status", {}).items():
                if "Adequate" not in status:
                    missing_categories.append(cat_name)
            class_counts = ds_summary.get("category_counts", {})
        except Exception:
            pass
            
    # Default fallbacks for missing categories if dataset summary does not exist
    if not missing_categories and not os.path.exists(summary_path):
        missing_categories = ["Pest Damage", "Nutrient Deficiency"]
        
    if not class_counts:
        class_counts = {
            "Fungal Infection": 0,
            "Bacterial Infection": 0,
            "Viral Disease": 0,
            "Pest Damage": 0,
            "Nutrient Deficiency": 0,
            "Healthy Leaf": 0
        }
        
    # Read metrics & bias status from evaluation summary / metadata
    eval_summary_path = os.path.abspath(os.path.join(base_dir, "results", "infection_evaluation_summary.json"))
    model_bias_detected = _metadata.get("model_bias_detected", False)
    evaluation_accuracy = _metadata.get("evaluation_accuracy", 0.0)
    evaluation_f1_score = _metadata.get("evaluation_f1_score", 0.0)
    
    if os.path.exists(eval_summary_path):
        try:
            with open(eval_summary_path, "r") as f:
                eval_data = json.load(f)
            model_bias_detected = eval_data.get("model_bias_detected", model_bias_detected)
            evaluation_accuracy = eval_data.get("accuracy", evaluation_accuracy)
            evaluation_f1_score = eval_data.get("weighted_f1_score", evaluation_f1_score)
        except Exception:
            pass
        
    model_type = _metadata.get("model_type")
    if not model_type:
        if settings.MODEL_PATH and "infection" in settings.MODEL_PATH.lower():
            model_type = "infection_category"
        else:
            model_type = "crop_specific"
            
    crop_filter_required = _metadata.get("crop_filter_required")
    if crop_filter_required is None:
        crop_filter_required = False if model_type == "infection_category" else True
        
    if model_type == "infection_category":
        supported_crops = "All crops accepted as metadata for infection-category prediction"
    else:
        supported_crops = []
        if labels:
            for val in labels.values():
                c = val.get("crop_name")
                if c and c not in supported_crops:
                    supported_crops.append(c)
                    
    model_version = _metadata.get("model_version", "agrocare_infection_model_v1" if model_type == "infection_category" else "agrocare_model_v1")
        
    return {
        "model_loaded": loaded,
        "demo_mode": settings.DEMO_MODE,
        "model_type": model_type,
        "crop_filter_required": crop_filter_required,
        "model_version": model_version,
        "number_of_classes": num_classes,
        "labels_loaded": labels is not None,
        "trained_categories": [
            "Fungal Infection",
            "Bacterial Infection",
            "Viral Disease",
            "Pest Damage",
            "Nutrient Deficiency",
            "Healthy Leaf"
        ] if model_type == "infection_category" else [],
        "missing_or_low_data_categories": missing_categories if model_type == "infection_category" else [],
        "supported_crops": supported_crops,
        "model_path": settings.MODEL_PATH if loaded else "",
        "class_counts": class_counts,
        "model_bias_detected": model_bias_detected,
        "evaluation_accuracy": evaluation_accuracy,
        "evaluation_f1_score": evaluation_f1_score
    }





