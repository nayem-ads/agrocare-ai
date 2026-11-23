# AgroCare AI: Field-Robust Multi-Crop Leaf Diagnosis with Open-Set Rejection, Two-Stage Lesion Segmentation, and Agro-Meteorological Prior Fusion

**Authors:**  
**Rasel Rahman**, **Sohan Sheikh**, **Nur Shad Srabon**, **Fahmida Alamgir**  
*Department of Computer Science & Engineering, Dhaka, Bangladesh*

---

## Abstract
Plant disease diagnosis models trained on laboratory datasets such as PlantVillage routinely report $>98\%$ accuracy yet suffer severe performance degradation when deployed on smallholder smartphones in Bangladeshi field conditions. Furthermore, existing regional tools (e.g., BRRI Rice Solution) focus on single crops, always emit a closed-set prediction even on non-leaf or unknown inputs, and do not quantify physical lesion severity. In this paper, we present **AgroCare AI**, a six-stage diagnostic and extension system addressing five research questions (`RQ1–RQ5`). First (`RQ1`), a 45-run cross-domain benchmark across five backbones and three training mixes demonstrates that while lab-only training drops by 51.2–61.2 Macro-F1 points on held-out Bangladeshi field photos, combining field fine-tuning with leaf foreground isolation (`Mix C`) recovers Macro-F1 to **88.9%**. Second (`RQ2`), a dual-tier photo quality/leaf gate and Energy-based open-set detector rejects unsupported crops and non-leaf objects with **0.942 AUROC** (`11.4% FPR@95%TPR`), withholding chemical advice and routing uncertain cases to an Agriculture Officer Review Queue. Third (`RQ3`), a two-stage leaf and lesion segmentation pipeline measures $\text{Severity \%} = (\text{Lesion Area} \div \text{Leaf Area}) \times 100$, achieving **0.814 Lesion IoU** (`0.897 Dice`, `3.4% MAE` vs. expert scores). Fourth (`RQ4`), fusing 10-day Open-Meteo forecasts with Bangladesh Agro-Meteorological Information System (BAMIS) disease priors improves Top-1 field accuracy by **+4.6%**. Finally (`RQ5`), human-in-the-loop retraining from 284 officer-verified field corrections improves Macro-F1 from **84.2% (`v1`) to 88.9% (`v2`)**.

**Keywords:** Plant Pathology, Open-Set Recognition, Lesion Segmentation, BAMIS Weather Fusion, Human-in-the-Loop Retraining, Bangladesh Agriculture.

---

## I. Introduction & Differentiation from Prior Work
Smallholder farmers in Bangladesh lose 15–30% of seasonal rice, tomato, and potato yields to fungal blights, bacterial spots, and insect-vectored viral diseases. While the **BRRI Rice Solution App (2023)** provides rice-specific management advice and **IRRI/BRRI Rice Doctor** offers rule-based questionnaires for extension workers, existing tools lack:
1. Multi-crop cross-domain field validation across Rice, Tomato, and Potato (Core) and Mango, Jute, and Chili (Stretch);
2. Open-set rejection of non-leaf images and unseen diseases;
3. Physical lesion-area percentage measurement;
4. Quantitative agro-meteorological prior re-ranking; and
5. A closed human-in-the-loop retraining pipeline with Upazila Agriculture Officers.

---

## II. Six-Stage Diagnostic Methodology
1. **Stage 1 — Photo Quality & Leaf Gate:** Evaluates Laplacian focus variance, exposure, HSV foliage coverage, and 2D Structure Tensor directional anisotropy to auto-detect monocot parallel-veined Rice leaves vs. dicot reticulate leaves (Tomato/Potato) and emit Bangla retake hints when quality fails.
2. **Stage 2 — Classifier & Canonical Taxonomy Lookup:** Enforces $\text{Crop} \rightarrow \text{Disease} \rightarrow \text{Category}$ via `DISEASE_TAXONOMY` so category labels never contradict specific disease predictions.
3. **Stage 3 — Open-Set Energy Gate (`RQ2`):** Computes energy $E(x) = -T \log \sum_i \exp(z_i / T)$ and predictive entropy. Uncertain samples ($U(x) \ge 0.58$) withhold chemical prescriptions (Section 9 Rule 5) and enter the Officer Review Queue.
4. **Stage 4 — BAMIS Weather-Prior Re-ranking (`RQ4`):**
   $$P_{\text{final}}(d) = \frac{P_{\text{image}}(d) \cdot (1 + \alpha \cdot R_{\text{weather}}(d))}{\sum_k P_{\text{image}}(k) \cdot (1 + \alpha \cdot R_{\text{weather}}(k))}$$
   where $R_{\text{weather}}(d) \in [0, 1]$ evaluates 7-day history and 3-day Open-Meteo forecasts against BAMIS crop-weather thresholds ($\alpha = 0.35$).
5. **Stage 5 — Two-Stage Lesion Segmentation (`RQ3`):** Computes $\text{Severity \%} = (\text{lesion\_area\_px} \div \text{leaf\_area\_px}) \times 100$ and renders a visual contour overlay.
6. **Stage 6 — Grad-CAM & DAE/BRRI/BARI Bilingual Advisory:** Generates spatial activation heatmaps and retrieves expert-reviewed Bangla and English treatments citing official DAE, BRRI, BARI, and BJRI manuals.

---

## III. Experimental Results Summary (`RQ1–RQ5`)
- **RQ1 (Cross-Domain Benchmark):** Across 45 runs (`5 Backbones × 3 Data Mixes × 3 Seeds`), `ConvNeXt-Tiny` under `Mix C` achieves **88.9% ± 0.5% Macro-F1** on the held-out `AgroCare-BD Field Test`, while `MobileNetV3-Small` achieves **86.4% ± 0.7% Macro-F1** and exports to a **4.8 MB INT8 TFLite** model running in **38.4 ms** on a low-end Android device.
- **RQ2 (Open-Set Rejection):** Combining the Stage 1 Leaf Gate with Stage 3 Energy + Entropy achieves **0.942 AUROC** and **11.4% FPR@95%TPR** on `AgroCare-Unknown` ($N=320$).
- **RQ3 (Lesion Severity):** Evaluated on 360 annotated masks, two-stage segmentation achieves **0.814 Lesion IoU**, **0.897 Dice**, and **3.4% MAE** ($r = 0.931$).
- **RQ4 (Weather Ablation):** BAMIS weather-prior fusion ($\alpha = 0.35$ vs. $\alpha = 0$) improves Top-1 accuracy on ambiguous field samples from **86.4% to 91.0% (+4.6%)**.
- **RQ5 (Officer HITL Retraining):** Incorporating 284 pHash-deduplicated officer corrections improves Field Macro-F1 from **84.2% (`v1.5`) to 88.9% (`v2.0`)**.
