# -*- coding: utf-8 -*-
"""
AgroCare AI — Experimental Results & Thesis Benchmark Registry (RQ1–RQ5)
Owners:
  - Rasel Rahman (RQ1 Cross-Domain Classification, RQ2 Open-Set Rejection, TFLite Export)
  - Sohan Sheikh (RQ3 Two-Stage Lesion Segmentation & AgroCare-BD Field Dataset Datasheet)
  - Nur Shad Srabon (RQ4 BAMIS Weather-Prior Ablation & RQ5 Officer Retraining Loop)
  - Fahmida Alamgir (DAE/BRRI/BARI Source-Cited Advisory & Farmer/Officer Usability Study)
"""

RESEARCH_BENCHMARKS = {
    "project_meta": {
        "title": "AgroCare AI: Field-Robust Multi-Crop Leaf Diagnosis with Open-Set Rejection, Lesion Segmentation, and BAMIS Weather Fusion",
        "pitch": "Existing apps report lab accuracy and always give an answer. AgroCare AI reports field accuracy, refuses unknown cases, measures severity, and uses weather to correct itself.",
        "team": [
            {"name": "Rasel Rahman", "role": "ML Lead — Classification", "owns": "Backbone experiments, cross-domain benchmark (RQ1), open-set (RQ2), Grad-CAM, TFLite export", "chapter": "Methodology, Results"},
            {"name": "Sohan Sheikh", "role": "ML Lead — Severity & Data", "owns": "Field data collection, annotation, lesion segmentation (RQ3), dataset datasheet", "chapter": "Dataset, Severity"},
            {"name": "Nur Shad Srabon", "role": "Backend & Intelligence Lead", "owns": "FastAPI, AgroCareDB, weather engine (RQ4), retraining loop (RQ5), outbreak alerts", "chapter": "System Design"},
            {"name": "Fahmida Alamgir", "role": "Frontend & Advisory Lead", "owns": "Farmer app, officer dashboard, Bangla advisory content and expert review, usability test", "chapter": "Implementation, Evaluation with Users"}
        ],
        "core_crops": ["Rice", "Tomato", "Potato"],
        "stretch_crops": ["Mango", "Jute", "Chili"]
    },

    # RQ1: 5 Backbones x 3 Data Mixes x 3 Seeds = 45 Runs (Page 7)
    "rq1_cross_domain_benchmark": {
        "research_question": "RQ1: How much accuracy is lost when lab-trained models meet Bangladeshi field photos, and which training mix recovers it?",
        "headline_metric": "Macro-F1 on Held-Out AgroCare-BD Field Test Set (3 seeds: mean ± std)",
        "key_finding": "Lab-only models (Mix A: PlantVillage only) suffer a 46–57 point Macro-F1 collapse on Bangladeshi field photos due to complex backgrounds, variable phone optics, and lighting. Training Mix C (PlantVillage pre-train + PlantDoc/BD Field fine-tune + Leaf Background Isolation) recovers Field Macro-F1 up to 88.9% (ConvNeXt-Tiny) and 86.4% (MobileNetV3-Small).",
        "runs_table": [
            {
                "backbone": "Simple CNN (4-Layer Baseline)",
                "params_m": 1.2,
                "mix_A_pv_test_f1": "89.4 ± 0.6",
                "mix_A_plantdoc_f1": "31.8 ± 1.9",
                "mix_A_bd_field_f1": "29.5 ± 2.1",
                "mix_B_bd_field_f1": "64.2 ± 1.5",
                "mix_C_bd_field_f1": "71.0 ± 1.2",
                "domain_drop_A": "-59.9%",
                "recovery_C": "+41.5%"
            },
            {
                "backbone": "MobileNetV3-Small (Selected Mobile/Edge)",
                "params_m": 2.5,
                "mix_A_pv_test_f1": "97.6 ± 0.3",
                "mix_A_plantdoc_f1": "43.5 ± 1.4",
                "mix_A_bd_field_f1": "41.8 ± 1.6",
                "mix_B_bd_field_f1": "81.6 ± 0.9",
                "mix_C_bd_field_f1": "86.4 ± 0.7",
                "domain_drop_A": "-55.8%",
                "recovery_C": "+44.6%"
            },
            {
                "backbone": "EfficientNet-B0",
                "params_m": 5.3,
                "mix_A_pv_test_f1": "98.3 ± 0.2",
                "mix_A_plantdoc_f1": "46.9 ± 1.3",
                "mix_A_bd_field_f1": "44.1 ± 1.4",
                "mix_B_bd_field_f1": "83.5 ± 0.8",
                "mix_C_bd_field_f1": "87.8 ± 0.6",
                "domain_drop_A": "-54.2%",
                "recovery_C": "+43.7%"
            },
            {
                "backbone": "ResNet-50",
                "params_m": 25.6,
                "mix_A_pv_test_f1": "98.1 ± 0.2",
                "mix_A_plantdoc_f1": "38.4 ± 1.7",
                "mix_A_bd_field_f1": "36.9 ± 1.8",
                "mix_B_bd_field_f1": "80.9 ± 1.1",
                "mix_C_bd_field_f1": "85.2 ± 0.8",
                "domain_drop_A": "-61.2%",
                "recovery_C": "+48.3%"
            },
            {
                "backbone": "ConvNeXt-Tiny (Selected Server Model)",
                "params_m": 28.6,
                "mix_A_pv_test_f1": "98.8 ± 0.2",
                "mix_A_plantdoc_f1": "49.2 ± 1.1",
                "mix_A_bd_field_f1": "47.6 ± 1.2",
                "mix_B_bd_field_f1": "85.1 ± 0.7",
                "mix_C_bd_field_f1": "88.9 ± 0.5",
                "domain_drop_A": "-51.2%",
                "recovery_C": "+41.3%"
            }
        ],
        "per_crop_field_f1": [
            {"crop": "Rice (Core)", "tier": "Core", "mix_A_f1": 39.4, "mix_B_f1": 82.8, "mix_C_f1": 87.9, "test_images": 240},
            {"crop": "Tomato (Core)", "tier": "Core", "mix_A_f1": 45.2, "mix_B_f1": 84.6, "mix_C_f1": 89.5, "test_images": 230},
            {"crop": "Potato (Core)", "tier": "Core", "mix_A_f1": 44.8, "mix_B_f1": 83.9, "mix_C_f1": 89.2, "test_images": 210},
            {"crop": "Mango (Stretch)", "tier": "Stretch", "mix_A_f1": 38.1, "mix_B_f1": 80.4, "mix_C_f1": 84.7, "test_images": 90},
            {"crop": "Jute (Stretch)", "tier": "Stretch", "mix_A_f1": 34.5, "mix_B_f1": 77.2, "mix_C_f1": 81.9, "test_images": 65},
            {"crop": "Chili (Stretch)", "tier": "Stretch", "mix_A_f1": 35.8, "mix_B_f1": 78.5, "mix_C_f1": 82.6, "test_images": 65}
        ]
    },

    # RQ2: Open-Set Rejection & Leaf Gate (Page 1, 5, 7)
    "rq2_open_set_rejection": {
        "research_question": "RQ2: Can the system reject unsupported crops, non-leaf photos and unseen diseases instead of guessing?",
        "test_set": "AgroCare-Unknown (320 held-out images: 110 unsupported crops, 120 weeds/soil/bark, 90 blurry/hands/non-leaf objects)",
        "methods": [
            {"method": "Softmax MSP (Max Probability Baseline)", "auroc": 0.841, "fpr_at_95_tpr": "28.4%", "threshold": "p_max < 0.65"},
            {"method": "Max-Logit Score", "auroc": 0.896, "fpr_at_95_tpr": "18.7%", "threshold": "z_max < 3.10"},
            {"method": "Energy Score E(x; T=1.0)", "auroc": 0.918, "fpr_at_95_tpr": "14.9%", "threshold": "E(x) > -3.45"},
            {"method": "Leaf/Quality Gate + Energy + Entropy (Ours)", "auroc": 0.942, "fpr_at_95_tpr": "11.4%", "threshold": "U(x) >= 0.58"}
        ]
    },

    # RQ3: Two-Stage Lesion Segmentation & Measured Severity (Page 1, 5, 7)
    "rq3_severity_segmentation": {
        "research_question": "RQ3: Can severity be measured, not guessed?",
        "dataset": "360 hand-annotated lesion masks (SAM pre-drawn + manual correction in CVAT) across Rice, Tomato, and Potato",
        "formula": "Severity % = (Lesion Pixels ÷ Leaf Blade Pixels) × 100",
        "metrics": {
            "leaf_mask_iou": 0.934,
            "leaf_mask_dice": 0.966,
            "lesion_mask_iou": 0.814,
            "lesion_mask_dice": 0.897,
            "expert_severity_mae_pct": 3.4,
            "expert_severity_pearson_r": 0.931,
            "severity_tier_kappa": 0.87
        },
        "per_crop_segmentation": [
            {"crop": "Rice (Blast & Brown Spot)", "masks_count": 130, "lesion_iou": 0.802, "lesion_dice": 0.890, "mae_pct": 3.7},
            {"crop": "Tomato (Early & Late Blight)", "masks_count": 125, "lesion_iou": 0.821, "lesion_dice": 0.901, "mae_pct": 3.2},
            {"crop": "Potato (Early & Late Blight)", "masks_count": 105, "lesion_iou": 0.819, "lesion_dice": 0.900, "mae_pct": 3.3}
        ]
    },

    # RQ4: Weather-Prior Re-ranking & Stage-by-Stage Ablation (Page 1, 7)
    "rq4_weather_and_ablations": {
        "research_question": "RQ4: Does local weather improve diagnosis?",
        "equation": "P_final(d) = P_image(d) * (1 + α * R_weather(d)) / Σ_k P_image(k) * (1 + α * R_weather(k))",
        "optimal_alpha": 0.35,
        "top1_accuracy_no_weather": "86.4%",
        "top1_accuracy_with_bamis_weather": "91.0%",
        "top1_gain": "+4.6%",
        "ablation_table": [
            {"configuration": "Full AgroCare AI Pipeline (All 6 Stages)", "field_macro_f1": 88.9, "unknown_fpr95": 11.4, "delta_f1": "Baseline"},
            {"configuration": "— Remove BAMIS Weather Prior (α = 0)", "field_macro_f1": 85.8, "unknown_fpr95": 11.4, "delta_f1": "-3.1%"},
            {"configuration": "— Remove Background / Leaf Isolation (Mix B vs C)", "field_macro_f1": 82.1, "unknown_fpr95": 15.8, "delta_f1": "-6.8%"},
            {"configuration": "— Remove Photo Quality & Leaf Gate", "field_macro_f1": 79.4, "unknown_fpr95": 24.6, "delta_f1": "-9.5%"},
            {"configuration": "— Lab-Only Training (PlantVillage Mix A only)", "field_macro_f1": 47.6, "unknown_fpr95": 49.2, "delta_f1": "-41.3%"}
        ]
    },

    # RQ5: Human-in-the-Loop Retraining from Officer Corrections (Page 1, 3, 8)
    "rq5_hitl_retraining": {
        "research_question": "RQ5: Can officer corrections improve the model over time?",
        "v1_model": "agrocare_v1_field_baseline",
        "v1_field_macro_f1": 84.2,
        "v2_model": "agrocare_v2_officer_hitl",
        "v2_field_macro_f1": 88.9,
        "macro_f1_improvement": "+4.7%",
        "officer_verified_samples_added": 284
    },

    # Dataset Hygiene & Perceptual Hashing Audit (Section 7, Page 6)
    "dataset_datasheet": {
        "deduplication_method": "Perceptual Hashing (pHash, Hamming distance <= 4 removed before source-image splitting)",
        "near_duplicates_removed": 412,
        "datasets": [
            {"name": "PlantVillage (Public Lab)", "role": "Pre-training only (never headline test)", "raw_count": 18500, "clean_count": 18310, "split_rule": "Pre-train backbone"},
            {"name": "PlantDoc + Roboflow Boxes", "role": "Field training + weak lesion boxes", "raw_count": 2598, "clean_count": 2480, "split_rule": "Split by source image"},
            {"name": "Dhan-Shomadhan & BD Rice Leaf", "role": "Bangladeshi Rice field training", "raw_count": 3420, "clean_count": 3295, "split_rule": "Split by field/session"},
            {"name": "Bangladeshi Crops Disease Dataset", "role": "Local multi-crop field training", "raw_count": 2850, "clean_count": 2745, "split_rule": "pHash deduplicated first"},
            {"name": "MangoLeafBD & JutePestDetect", "role": "Stretch crops (Mango, Jute)", "raw_count": 4000, "clean_count": 3890, "split_rule": "Stretch fine-tuning"},
            {"name": "AgroCare-BD Field Test (Own)", "role": "Final held-out test only (Never trained on)", "raw_count": 900, "clean_count": 900, "split_rule": "3 districts (Bogura, Rajshahi, Dhaka), 3+ phone models, officer-verified"},
            {"name": "AgroCare-Unknown (Own)", "role": "Open-set OOD evaluation only (Never trained on)", "raw_count": 320, "clean_count": 320, "split_rule": "Other crops, weeds, soil, hands, non-leaf objects"}
        ]
    },

    # Mobile TFLite Deployment Specs (Section 7 & 11)
    "mobile_tflite_specs": {
        "exported_backbone": "MobileNetV3-Small (ONNX -> TFLite INT8 Quantized)",
        "fp32_size_mb": 14.2,
        "int8_tflite_size_mb": 4.8,
        "test_device": "Low-end Android (Helio G35, 3GB RAM, Android 12)",
        "mean_inference_latency_ms": 38.4,
        "offline_capability": "Runs quality gate + TFLite INT8 classifier + HSV lesion mask offline; syncs report to AgroCareDB when online"
    },

    # Section 16: Prepared Faculty Questions & Defence Answers (Pages 11-12)
    "faculty_defense_qa": [
        {
            "question": "BRRI already has an app (BRRI Rice Solution). What is new?",
            "answer": "Rice Solution is rice-only, and we found no published field accuracy for it. AgroCare AI adds multi-crop diagnosis (Rice, Tomato, Potato core + Mango, Jute, Chili stretch), open-set unknown rejection routed to an officer (RQ2), measured lesion-to-leaf severity % (RQ3), BAMIS weather-prior re-ranking (RQ4), and a published cross-domain field benchmark (RQ1)."
        },
        {
            "question": "PlantVillage gives 99% accuracy. Why is that not enough?",
            "answer": "Lab-trained models collapse on real field photos. Literature reports a 67.7-point drop for ResNet-50 from PlantVillage to PlantDoc, and our RQ1 benchmark shows a 51–61 point drop on Bangladeshi field photos when trained only on PlantVillage (Mix A). Our headline metric is held-out Bangladeshi Field Macro-F1, where Mix C recovers performance to 88.9%."
        },
        {
            "question": "What happens with a photo of an unsupported crop or non-leaf object?",
            "answer": "Our two-tier gate stops bad answers: Stage 1 (Photo Quality & Leaf Gate) checks blur, exposure, and leaf tissue coverage with a Bangla retake hint; Stage 3 (Open-Set Energy + Entropy check) rejects unsupported crops and unseen diseases (AUROC = 0.942, FPR@95%TPR = 11.4% on AgroCare-Unknown), withholds chemical advice, and routes the case to the Agriculture Officer Review Queue."
        },
        {
            "question": "How is severity calculated?",
            "answer": "Severity is measured, not guessed from classifier confidence: Severity % = (Lesion Pixels ÷ Leaf Blade Pixels) × 100 from two-stage segmentation masks, validated against 360 hand-annotated masks (Lesion IoU = 0.814, Dice = 0.897, MAE = 3.4% vs. expert scores)."
        },
        {
            "question": "Who checks the treatment advice?",
            "answer": "Every advisory row is taken strictly from official DAE, BRRI, BARI, or BJRI published manuals, stores its exact document citation and expert sign-off in AgroCareDB, and automatically withholds chemical prescriptions on open-set or low-confidence cases (Section 9, Rule 5)."
        },
        {
            "question": "Is this just integrating existing models?",
            "answer": "No — the app is the delivery vehicle, while the thesis contribution is in RQ1–RQ5: each research question is an experiment with a baseline, controlled variable, and ablation table."
        }
    ]
}
