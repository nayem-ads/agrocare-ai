FROM python:3.11-slim

WORKDIR /app

# Install minimal system runtime libraries required by OpenCV headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend code, trained models, and pre-built React frontend dist
COPY backend /app/backend
COPY frontend/dist /app/frontend/dist
COPY README.md /app/README.md

ENV PYTHONPATH=/app
ENV MODEL_PATH=backend/ml/models/agrocare_infection_model.keras
ENV FALLBACK_MODEL_PATH=backend/ml/models/agrocare_infection_model.h5
ENV LABELS_PATH=backend/ml/infection_labels.json
ENV REAL_MODEL_REQUIRED=true
ENV DEMO_MODE=false

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
