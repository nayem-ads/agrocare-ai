# Datasheet for Datasets: AgroCare-BD Field Test & AgroCare-Unknown (Section 7 & 17)

**Authors:** Sohan Sheikh (ML Lead — Severity & Data), Rasel Rahman (ML Lead — Classification), Nur Shad Srabon (Backend Lead), Fahmida Alamgir (Advisory & Usability Lead)

---

## 1. Motivation
- **For what purpose was the dataset created?**
  To benchmark the lab-to-field domain gap (`RQ1`), evaluate open-set rejection of unsupported crops and non-leaf photos (`RQ2`), and evaluate two-stage lesion segmentation accuracy against pathology severity scores (`RQ3`) under real Bangladeshi smallholder field conditions.
- **Who created the dataset?**
  The AgroCare AI Final Year Project research team across agricultural fields in Bogura (Shibganj), Rajshahi (Godagari), and Dhaka/Savar, combined with deduplicated public field splits from PlantDoc, Dhan-Shomadhan, and PlantVillage.

## 2. Composition
| Dataset Split | Role in Thesis | Images (Clean) | Crops Covered | Split Rule |
| :--- | :--- | :--- | :--- | :--- |
| **PlantVillage (Lab)** | Backbone Pre-training Only | 18,310 | Tomato, Potato, Pepper | Never used as headline test |
| **PlantDoc (Field)** | Field Fine-Tuning + Validation | 2,480 | Tomato, Potato, Pepper, Multi-crop | Split by source image, not random |
| **BD Rice Field (Dhan-Shomadhan)** | Local Rice Field Training | 3,295 | Rice (Blast, Brown Spot, BLB, Tungro, Hispa) | Split by field session |
| **MangoLeafBD & JutePestDetect** | Stretch Tier Fine-Tuning | 3,890 | Mango, Jute, Chili | Stretch tier evaluation |
| **AgroCare-BD Field Test (Own)** | Final Held-Out Field Benchmark (`RQ1`) | 900 | Rice (240), Tomato (230), Potato (210), Stretch (220) | **Never trained on**; 3+ smartphone models, morning & afternoon natural light |
| **AgroCare-Unknown (Own)** | Open-Set OOD Evaluation (`RQ2`) | 320 | Unsupported crops (110), weeds/soil (120), hands/blurry non-leaf objects (90) | **Never trained on** |
| **AgroCare-Lesion-Masks (Own)** | Two-Stage Severity Benchmark (`RQ3`) | 360 | Rice (130), Tomato (125), Potato (105) | SAM pre-annotated + manual CVAT polygon refinement |

## 3. Data Hygiene & Perceptual Hashing Deduplication
- **Near-Duplicate Removal:** Before any train/validation/test splitting, all candidate images are hashed using 64-bit Perceptual Hashing (`pHash` / `dHash`). Image pairs with Hamming distance $\le 4$ are flagged as near-duplicates and removed (`412` near-duplicates removed across public sources) to prevent data leakage between training and evaluation splits.
- **Zero Augmentation Leakage:** Offline and online geometric/photometric augmentations (rotation $\pm 20^\circ$, horizontal flips, brightness $\pm 14\%$) are applied **strictly to the training split after source-image partitioning**. Validation and test splits contain only unaugmented original images.

## 4. Collection & Annotation Process
- **Devices & Lighting:** Captured across 4 smartphone cameras (Xiaomi Redmi 10C Helio G35, Samsung Galaxy A23, Realme C55, iPhone 12) during morning (07:30–10:30) and late afternoon (15:30–17:30) field visits.
- **Metadata Recorded per Sample:** Crop name, canonical disease code, infection category (resolved via deterministic taxonomy lookup), GPS coordinates (`SRID=4326;POINT(lon lat)`), Upazila, capture timestamp, and device identifier.
- **Lesion Mask Annotation:** Leaf blade boundaries (`leaf_area_px`) and necrotic/chlorotic lesion polygons (`lesion_area_px`) were pre-segmented with Segment Anything (SAM) and manually corrected in CVAT to verify $\text{Severity \%} = \frac{\text{lesion\_area\_px}}{\text{leaf\_area\_px}} \times 100$.
