#!/usr/bin/env bash
# AgroCare AI — One-Command Startup Script (Backend + Frontend)
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "=========================================================="
echo " Starting AgroCare AI (FastAPI Backend + React Frontend)  "
echo "=========================================================="

# 1. Start FastAPI Backend on port 8001
cd "$PROJECT_ROOT/backend"
MODEL_PATH=backend/ml/models/agrocare_infection_model.keras \
LABELS_PATH=backend/ml/infection_labels.json \
FALLBACK_MODEL_PATH=backend/ml/models/agrocare_infection_model.h5 \
PYTHONPATH=.. uvicorn app.main:app --host 127.0.0.1 --port 8001 &
BACKEND_PID=$!

# 2. Start Vite Frontend on port 3000
cd "$PROJECT_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Backend API running at: http://127.0.0.1:8001"
echo "Frontend UI running at: http://localhost:3000"
echo "Press CTRL+C to stop both servers."

trap "kill -9 $BACKEND_PID $FRONTEND_PID 2>/dev/null || true" EXIT
wait
