# Model Cards — AgroCare AI 6-Stage Diagnostic Pipeline (Section 17)

**Maintainers:** Rasel Rahman (Classification, Open-Set, TFLite), Sohan Sheikh (Two-Stage Lesion Segmentation), Nur Shad Srabon (BAMIS Weather Prior & HITL Registry)

---

## Model Card 1: Multi-Crop Disease & Infection Classifier (`agrocare_v2.0_officer_hitl`)

- **Architecture:** ConvNeXt-Tiny (Server Primary) & MobileNetV2 / MobileNetV3-Small (Edge & Fast CPU Inference)
- **Input Resolution & Preprocessing:** $224 \times 224 \times 3$ RGB, family-specific normalization (`[-1, 1]` for MobileNet, ImageNet mean/std for ConvNeXt/ResNet)
- **Training Data Mix (`Mix C + RQ5 HITL`):** PlantVillage pre-training $\rightarrow$ PlantDoc + Bangladeshi Rice/Vegetable field fine-tuning with leaf foreground isolation + 284 officer-verified `AgroCareDB` corrections
- **Canonical Taxonomy Enforcement (Section 3):** Outputs map deterministically via `DISEASE_TAXONOMY` ($\text{Crop} \rightarrow \text{Disease} \rightarrow \text{Category}$) so infection categories (*Fungal, Bacterial, Viral, Pest, Nutrient, Healthy*) never contradict the specific disease.
- **Evaluation Metrics (3 Seeds, Mean $\pm$ Std):**
  - **PlantVillage Test Macro-F1:** $98.8\% \pm 0.2\%$
  - **PlantDoc Test Macro-F1:** $84.9\% \pm 0.7\%$
  - **AgroCare-BD Held-Out Field Test Macro-F1 (`RQ1 Headline`):** $88.9\% \pm 0.5\%$ (Server) / $86.4\% \pm 0.7\%$ (MobileNet Edge)

---

## Model Card 2: Stage 1 Leaf Gate & Stage 3 Open-Set Rejection (`RQ2`)

- **Objective:** Prevent hallucinated diagnoses on blurry/dark photos, non-leaf objects, unsupported crops, and unseen diseases.
- **Formulation:**
  - **Stage 1 Photo Quality & Leaf Gate:** Laplacian focus variance ($\ge 12.0$), luminance exposure ($\in [22, 246]$), HSV foliage + necrotic tissue ratio ($\ge 8.0\%$), and 2D Structure Tensor eigenvalue anisotropy for monocot (Rice) vs. dicot (Tomato/Potato) leaf identification.
  - **Stage 3 Energy & Entropy Open-Set Score:** Combines Helmholtz free energy $E(x; T=1.0) = -T \log \sum_i \exp(z_i / T)$ and normalized Shannon entropy $H(p)$ into a calibrated uncertainty score $U(x) \in [0, 1]$ with threshold $\tau = 0.58$.
- **Benchmark on `AgroCare-Unknown` ($N = 320$):**
  - **AUROC:** `0.942`
  - **FPR@95%TPR:** `11.4%`
- **Safety Policy (Section 9 Rule 5):** Whenever $U(x) \ge 0.58$, the report is marked `"Not sure — sent to officer"`, chemical prescriptions are withheld, and the case enters the Agriculture Officer Review Queue.

---

## Model Card 3: Stage 5 Two-Stage Leaf & Lesion Segmentation (`RQ3`)

- **Objective:** Measure severity as a physical lesion-to-leaf pixel ratio rather than guessing severity from classifier softmax confidence.
- **Pipeline:**
  1. **Stage 5a (Leaf Blade Mask):** U-Net / HSV + morphological contour closure extracting total leaf area (`leaf_area_px`).
  2. **Stage 5b (Lesion Mask):** Chromatic necrotic/chlorotic segmentation inside the leaf blade (`lesion_area_px` via HSV + CIE-LAB $a^*$-channel thresholding).
  3. **Equation:**
     $$\text{Severity \%} = \frac{\text{lesion\_area\_px}}{\text{leaf\_area\_px}} \times 100$$
- **Benchmark on 360 Hand-Annotated Masks:**
  - **Leaf Mask IoU / Dice:** `0.934` / `0.966`
  - **Lesion Mask IoU / Dice:** `0.814` / `0.897`
  - **Agreement with Expert Pathology Scores:** $\text{MAE} = 3.4\%$, Pearson $r = 0.931$

---

## Model Card 4: On-Device TFLite INT8 Mobile Model (Section 11)

- **Format:** Post-training INT8 quantized TensorFlow Lite (`agrocare_mobile_int8.tflite`)
- **Model Size:** `4.8 MB` (reduced from `14.2 MB` FP32)
- **On-Device Latency:** `38.4 ms` mean inference time on low-end Android (MediaTek Helio G35, 3 GB RAM)
