import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./agrocare.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretjwtkeyforagrocareai123")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    REAL_MODEL_REQUIRED: bool = os.getenv("REAL_MODEL_REQUIRED", "true").lower() == "true"
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "false").lower() == "true"
    MODEL_PATH: str = os.getenv("MODEL_PATH", "backend/ml/models/agrocare_infection_model.keras")
    FALLBACK_MODEL_PATH: str = os.getenv("FALLBACK_MODEL_PATH", "backend/ml/models/agrocare_infection_model.h5")
    LABELS_PATH: str = os.getenv("LABELS_PATH", "backend/ml/infection_labels.json")



settings = Settings()

