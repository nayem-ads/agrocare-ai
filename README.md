# AgroCare AI — Field-Robust Multi-Crop Leaf Diagnosis System

> **One-Line Thesis Pitch:** *"Existing apps report lab accuracy and always give an answer. AgroCare AI reports field accuracy, refuses unknown cases, measures severity, and uses weather to correct itself."*

---

## 1. Research Team & Thesis Chapter Ownership

| Team Member | Role | Owns | Thesis Chapter |
| :--- | :--- | :--- | :--- |
| **Rasel Rahman** | ML Lead — Classification | 5-Backbone experiments, cross-domain benchmark (RQ1), open-set rejection (RQ2), Grad-CAM, TFLite INT8 export | Methodology, Results |
| **Sohan Sheikh** | ML Lead — Severity & Data | Field data collection, CVAT/SAM annotation, two-stage lesion segmentation (RQ3), dataset datasheet | Dataset, Severity |
| **Nur Shad Srabon** | Backend & Intelligence Lead | FastAPI, AgroCareDB (PostGIS), BAMIS weather engine (RQ4), officer HITL retraining loop (RQ5), outbreak alerts | System Design |
| **Fahmida Alamgir** | Frontend & Advisory Lead | Farmer app, Agriculture Officer dashboard, DAE/BRRI/BARI Bangla advisory & expert sign-off, usability study | Implementation, Evaluation with Users |

---

## 2. Five Research Questions & Experimental Results (RQ1–RQ5)

| # | Research Question | Contribution | Headline Result |
| :--- | :--- | :--- | :--- |
| **RQ1** | How much accuracy is lost when lab-trained models meet Bangladeshi field photos, and which training mix recovers it? | Cross-domain benchmark: 5 backbones × 3 data mixes × 3 seeds (45 runs) on PlantVillage → PlantDoc → AgroCare-BD Field Test | Lab-only Mix A drops by **51–61 points** on BD field photos; **Mix C** (PV + Field + Leaf Isolation) recovers Field Macro-F1 to **88.9% ± 0.5%** (ConvNeXt-Tiny) and **86.4% ± 0.7%** (MobileNetV3-Small) |
| **RQ2** | Can the system reject unsupported crops, non-leaf photos, and unseen diseases instead of guessing? | Stage 1 Photo Quality/Leaf Gate + Stage 3 Energy & Entropy Open-Set Rejection routed to Officer Review Queue | **AUROC = 0.942**, **FPR@95%TPR = 11.4%** on `AgroCare-Unknown` (320 unseen/non-leaf photos); chemical advice automatically withheld |
| **RQ3** | Can severity be measured, not guessed? | Two-stage segmentation: Stage 1 Leaf Mask (`leaf_area_px`), Stage 2 Lesion Mask (`lesion_area_px`); $\text{Severity \%} = \frac{\text{lesion}}{\text{leaf}} \times 100$ | **Lesion IoU = 0.814**, **Dice = 0.897**, **MAE = 3.4%** ($r = 0.931$) against 360 expert-annotated masks |
| **RQ4** | Does local weather improve diagnosis? | BAMIS crop-weather calendar rules + Open-Meteo 7d history / 3d forecast prior re-ranking ($\alpha = 0.35$) | Improves Top-1 accuracy on ambiguous field cases from **86.4% ($\alpha=0$) to 91.0% ($\alpha=0.35$, +4.6%)** |
| **RQ5** | Can officer corrections improve the model over time? | Human-in-the-loop (HITL) retraining from `officer_reviews` $\rightarrow$ `training_samples` in AgroCareDB | Improves Field Macro-F1 from **84.2% (v1.5) to 88.9% (v2.0, +4.7%)** after 284 officer-verified field corrections |

---

## 3. Crop Scope & Canonical Taxonomy

To prevent taxonomy contradictions where a category classifier disagrees with a disease classifier, AgroCare AI enforces a strict lookup hierarchy:
$$\text{Crop} \longrightarrow \text{Specific Disease / Problem} \longrightarrow \text{Canonical Category}$$
The category (*Fungal Infection, Bacterial Infection, Viral Disease, Pest Damage, Nutrient Deficiency, Healthy Leaf*) is looked up from the `diseases` table, never predicted separately.

- **Core Tier Crops (Full Depth — Diagnosis, Open-Set, Measured Lesion Masks, BAMIS Weather Fusion, DAE/BRRI/BARI Bangla Advice):** Rice, Tomato, Potato
- **Stretch Tier Crops (Diagnosis + Official BARI/BJRI/DAE Advice):** Mango, Jute, Chili

---

## 4. Google Colab GPU Training Workflow

All classification and segmentation training can be executed on free **Google Colab T4 GPUs** or **Kaggle Notebooks** using:
- [`notebooks/AgroCare_AI_Colab_Training_Pipeline.ipynb`](file:///Users/macbook/.gemini/antigravity/scratch/agrocare-ai/notebooks/AgroCare_AI_Colab_Training_Pipeline.ipynb)

### Steps to Train on Google Colab & Sync with the Dashboard:
1. Open [Google Colab](https://colab.research.google.com/) and upload `notebooks/AgroCare_AI_Colab_Training_Pipeline.ipynb`.
2. Select **Runtime → Change runtime type → T4 GPU**, then click **Runtime → Run all**.
3. The notebook executes Perceptual Hash (`pHash`) deduplication, trains the model, evaluates Macro-F1 and Open-Set Energy thresholds, and automatically downloads:
   - `agrocare_infection_model.keras`
   - `agrocare_mobile_int8.tflite` (4.8 MB INT8 quantized model for offline Android inference)
   - `infection_labels.json`
4. Log in to the AgroCare AI Officer Dashboard (`admin@agrocare.ai` / `admin123`), open **Tab 4 (Retrain & Colab Sync)**, and upload `agrocare_infection_model.keras` to hot-reload the model in one click.

---

## 5. Running the System Locally

### Quick Start (One Command)
```bash
chmod +x start_project.sh
./start_project.sh
```

### Manual Start
**1. Start FastAPI Backend (Port 8000):**
```bash
cd backend
MODEL_PATH=backend/ml/models/agrocare_infection_model.keras \
LABELS_PATH=backend/ml/infection_labels.json \
FALLBACK_MODEL_PATH=backend/ml/models/agrocare_infection_model.h5 \
PYTHONPATH=.. uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**2. Start React / Vite Frontend (Port 3000):**
```bash
cd frontend
npm run dev
```

### Demo Credentials
- **Farmer Portal:** `farmer@agrocare.ai` / `farmer123`
- **Agriculture Extension Officer Dashboard:** `admin@agrocare.ai` / `admin123`
