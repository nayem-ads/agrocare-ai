# -*- coding: utf-8 -*-
"""
AgroCare AI — Canonical Crop -> Disease -> Category Taxonomy Registry
Owner: Rasel Rahman (ML Lead - Classification) & Fahmida Alamgir (Advisory Lead)

Section 3 Requirement:
Label structure: crop -> disease or problem -> category.
The category (fungal, bacterial, viral, pest, nutrient, healthy) is looked up
from the disease label, never predicted separately, so it cannot contradict the disease.
"""

CORE_CROPS = ["Rice", "Tomato", "Potato"]
STRETCH_CROPS = ["Mango", "Jute", "Chili"]
SUPPORTED_CROPS = CORE_CROPS + STRETCH_CROPS

# Canonical Disease Registry: disease_code -> full metadata
# Severity thresholds (low_max, med_max) are calibrated per disease with pathology guidance.
DISEASE_TAXONOMY = {
    # --- RICE (Core Tier) ---
    "Rice_Blast": {
        "disease_code": "Rice_Blast",
        "crop_name": "Rice",
        "tier": "Core",
        "disease_name_en": "Rice Blast",
        "disease_name_bn": "ধানের ব্লাস্ট রোগ (Rice Blast)",
        "infection_category": "Fungal Infection",
        "category_key": "fungal",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 15.0, "med_max": 40.0},
        "bamis_Rule": {
            "temp_min": 16.0, "temp_max": 26.0,
            "humidity_min": 88.0, "rain_min_mm": 5.0,
            "description": "Night temperature 16–22°C with relative humidity >88% and dew/rain (BAMIS, Bogura)"
        }
    },
    "Rice_Brown_Spot": {
        "disease_code": "Rice_Brown_Spot",
        "crop_name": "Rice",
        "tier": "Core",
        "disease_name_en": "Brown Spot",
        "disease_name_bn": "ধানের বাদামী দাগ রোগ (Brown Spot)",
        "infection_category": "Fungal Infection",
        "category_key": "fungal",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 20.0, "med_max": 45.0},
        "bamis_Rule": {
            "temp_min": 24.0, "temp_max": 32.0,
            "humidity_min": 80.0, "rain_min_mm": 2.0,
            "description": "Temperature 25–30°C with high humidity >80% and potash-deficient wet soil (BRRI)"
        }
    },
    "Rice_Bacterial_Leaf_Blight": {
        "disease_code": "Rice_Bacterial_Leaf_Blight",
        "crop_name": "Rice",
        "tier": "Core",
        "disease_name_en": "Bacterial Leaf Blight (BLB)",
        "disease_name_bn": "ধানের পাতা পোড়া বা বিএলবি রোগ (BLB)",
        "infection_category": "Bacterial Infection",
        "category_key": "bacterial",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 15.0, "med_max": 38.0},
        "bamis_Rule": {
            "temp_min": 27.0, "temp_max": 34.0,
            "humidity_min": 80.0, "rain_min_mm": 15.0,
            "description": "Warm temperature 28–32°C, humidity 80–90%, cloudy weather and heavy rain >30mm (BAMIS, Bogura)"
        }
    },
    "Rice_Tungro": {
        "disease_code": "Rice_Tungro",
        "crop_name": "Rice",
        "tier": "Core",
        "disease_name_en": "Rice Tungro Virus",
        "disease_name_bn": "ধানের টুংরো ভাইরাস রোগ (Rice Tungro)",
        "infection_category": "Viral Disease",
        "category_key": "viral",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 15.0, "med_max": 35.0},
        "bamis_Rule": {
            "temp_min": 28.0, "temp_max": 36.0,
            "humidity_min": 65.0, "rain_min_mm": 0.0,
            "description": "Warm humid spells (28–34°C) favouring Green Leafhopper (GLH) vector migration (BRRI)"
        }
    },
    "Rice_Hispa_Pest": {
        "disease_code": "Rice_Hispa_Pest",
        "crop_name": "Rice",
        "tier": "Core",
        "disease_name_en": "Rice Hispa / Leaf Folder Damage",
        "disease_name_bn": "ধানের মাজরা ও পামরি পোকার আক্রমণ",
        "infection_category": "Pest Damage",
        "category_key": "pest",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 20.0, "med_max": 45.0},
        "bamis_Rule": {
            "temp_min": 29.0, "temp_max": 37.0,
            "humidity_min": 60.0, "rain_min_mm": 0.0,
            "description": "Hot, sunny spells after rain encouraging Hispa beetle and Leaf Folderfeeding (DAE)"
        }
    },
    "Rice_Nitrogen_Deficiency": {
        "disease_code": "Rice_Nitrogen_Deficiency",
        "crop_name": "Rice",
        "tier": "Core",
        "disease_name_en": "Nitrogen / Zinc Chlorosis",
        "disease_name_bn": "ধানের নাইট্রোজেন ও জিংকের অভাবজনিত হলদে পাতা",
        "infection_category": "Nutrient Deficiency",
        "category_key": "nutrient deficiency",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 20.0, "med_max": 50.0},
        "bamis_Rule": {
            "temp_min": 20.0, "temp_max": 35.0,
            "humidity_min": 50.0, "rain_min_mm": 20.0,
            "description": "Heavy rainfall leaching soil nitrogen or waterlogged zinc-deficient paddies (BRRI)"
        }
    },
    "Rice_Healthy": {
        "disease_code": "Rice_Healthy",
        "crop_name": "Rice",
        "tier": "Core",
        "disease_name_en": "Healthy Rice Leaf",
        "disease_name_bn": "সুস্থ ধানের পাতা (Healthy Rice Leaf)",
        "infection_category": "Healthy Leaf",
        "category_key": "healthy",
        "is_healthy": True,
        "severity_cutoffs": {"low_max": 5.0, "med_max": 15.0},
        "bamis_Rule": {
            "temp_min": 22.0, "temp_max": 31.0,
            "humidity_min": 55.0, "rain_min_mm": 0.0,
            "description": "Balanced sunshine and moderate humidity unfavourable for spore germination"
        }
    },

    # --- TOMATO (Core Tier) ---
    "Tomato_Late_Blight": {
        "disease_code": "Tomato_Late_Blight",
        "crop_name": "Tomato",
        "tier": "Core",
        "disease_name_en": "Late Blight",
        "disease_name_bn": "টমেটোর নাবী ধ্বসা রোগ (Late Blight)",
        "infection_category": "Fungal Infection",
        "category_key": "fungal",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 15.0, "med_max": 35.0},
        "bamis_Rule": {
            "temp_min": 14.0, "temp_max": 24.0,
            "humidity_min": 85.0, "rain_min_mm": 3.0,
            "description": "Cool, foggy or rainy weather (15–23°C) with relative humidity >85% (BARI)"
        }
    },
    "Tomato_Early_Blight": {
        "disease_code": "Tomato_Early_Blight",
        "crop_name": "Tomato",
        "tier": "Core",
        "disease_name_en": "Early Blight",
        "disease_name_bn": "টমেটোর আগাম ধ্বসা রোগ (Early Blight)",
        "infection_category": "Fungal Infection",
        "category_key": "fungal",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 18.0, "med_max": 42.0},
        "bamis_Rule": {
            "temp_min": 24.0, "temp_max": 31.0,
            "humidity_min": 78.0, "rain_min_mm": 2.0,
            "description": "Warm humid days (24–29°C) alternating with heavy morning dew (BARI)"
        }
    },
    "Tomato_Bacterial_Spot": {
        "disease_code": "Tomato_Bacterial_Spot",
        "crop_name": "Tomato",
        "tier": "Core",
        "disease_name_en": "Bacterial Spot",
        "disease_name_bn": "টমেটোর ব্যাকটেরিয়াজনিত পাতার দাগ (Bacterial Spot)",
        "infection_category": "Bacterial Infection",
        "category_key": "bacterial",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 18.0, "med_max": 40.0},
        "bamis_Rule": {
            "temp_min": 25.0, "temp_max": 33.0,
            "humidity_min": 80.0, "rain_min_mm": 8.0,
            "description": "Warm temperatures (25–30°C) with wind-driven rain splashing bacteria across foliage (BARI)"
        }
    },
    "Tomato_Yellow_Leaf_Curl_Virus": {
        "disease_code": "Tomato_Yellow_Leaf_Curl_Virus",
        "crop_name": "Tomato",
        "tier": "Core",
        "disease_name_en": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "disease_name_bn": "টমেটোর পাতা কোঁকড়ানো ভাইরাস রোগ (TYLCV)",
        "infection_category": "Viral Disease",
        "category_key": "viral",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 15.0, "med_max": 38.0},
        "bamis_Rule": {
            "temp_min": 27.0, "temp_max": 36.0,
            "humidity_min": 55.0, "rain_min_mm": 0.0,
            "description": "Warm, dry-to-moderate weather (27–35°C) accelerating Bemisia tabaci whitefly transmission (BARI)"
        }
    },
    "Tomato_Spider_Mite_Pest": {
        "disease_code": "Tomato_Spider_Mite_Pest",
        "crop_name": "Tomato",
        "tier": "Core",
        "disease_name_en": "Two-Spotted Spider Mite / Leaf Miner",
        "disease_name_bn": "টমেটোর লাল মাকড় ও পাতা ছিদ্রকারী পোকা",
        "infection_category": "Pest Damage",
        "category_key": "pest",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 20.0, "med_max": 45.0},
        "bamis_Rule": {
            "temp_min": 29.0, "temp_max": 38.0,
            "humidity_min": 45.0, "rain_min_mm": 0.0,
            "description": "Hot and dry conditions (>29°C) causing rapid spider mite reproduction (DAE)"
        }
    },
    "Tomato_Magnesium_Deficiency": {
        "disease_code": "Tomato_Magnesium_Deficiency",
        "crop_name": "Tomato",
        "tier": "Core",
        "disease_name_en": "Interveinal Magnesium / Potassium Deficiency",
        "disease_name_bn": "টমেটোর ম্যাগনেসিয়াম ও পটাশিয়ামের ঘাটতি",
        "infection_category": "Nutrient Deficiency",
        "category_key": "nutrient deficiency",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 20.0, "med_max": 50.0},
        "bamis_Rule": {
            "temp_min": 20.0, "temp_max": 34.0,
            "humidity_min": 50.0, "rain_min_mm": 10.0,
            "description": "Acidic or leached sandy loam soil after heavy irrigation or rainfall (BARI)"
        }
    },
    "Tomato_Healthy": {
        "disease_code": "Tomato_Healthy",
        "crop_name": "Tomato",
        "tier": "Core",
        "disease_name_en": "Healthy Tomato Leaf",
        "disease_name_bn": "সুস্থ টমেটোর পাতা (Healthy Tomato Leaf)",
        "infection_category": "Healthy Leaf",
        "category_key": "healthy",
        "is_healthy": True,
        "severity_cutoffs": {"low_max": 5.0, "med_max": 15.0},
        "bamis_Rule": {
            "temp_min": 20.0, "temp_max": 28.0,
            "humidity_min": 50.0, "rain_min_mm": 0.0,
            "description": "Optimal growing temperature (21–27°C) with low foliar wetness"
        }
    },

    # --- POTATO (Core Tier) ---
    "Potato_Late_Blight": {
        "disease_code": "Potato_Late_Blight",
        "crop_name": "Potato",
        "tier": "Core",
        "disease_name_en": "Potato Late Blight",
        "disease_name_bn": "আলুর নাবী ধ্বসা বা মড়ক রোগ (Late Blight)",
        "infection_category": "Fungal Infection",
        "category_key": "fungal",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 12.0, "med_max": 32.0},
        "bamis_Rule": {
            "temp_min": 12.0, "temp_max": 22.0,
            "humidity_min": 88.0, "rain_min_mm": 2.0,
            "description": "Winter fog, cloudy sky, temperature 12–21°C and humidity >88% (BAMIS Bogura Potato Alert)"
        }
    },
    "Potato_Early_Blight": {
        "disease_code": "Potato_Early_Blight",
        "crop_name": "Potato",
        "tier": "Core",
        "disease_name_en": "Potato Early Blight",
        "disease_name_bn": "আলুর আগাম ধ্বসা রোগ (Early Blight)",
        "infection_category": "Fungal Infection",
        "category_key": "fungal",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 18.0, "med_max": 40.0},
        "bamis_Rule": {
            "temp_min": 22.0, "temp_max": 30.0,
            "humidity_min": 75.0, "rain_min_mm": 1.0,
            "description": "Alternating wet and dry warm periods (24–28°C) during tuber bulking (BARI)"
        }
    },
    "Potato_Bacterial_Wilt": {
        "disease_code": "Potato_Bacterial_Wilt",
        "crop_name": "Potato",
        "tier": "Core",
        "disease_name_en": "Bacterial Wilt / Brown Rot Foliage",
        "disease_name_bn": "আলুর ব্যাকটেরিয়াজনিত ঢলে পড়া রোগ",
        "infection_category": "Bacterial Infection",
        "category_key": "bacterial",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 15.0, "med_max": 38.0},
        "bamis_Rule": {
            "temp_min": 25.0, "temp_max": 34.0,
            "humidity_min": 78.0, "rain_min_mm": 10.0,
            "description": "High soil moisture and warm temperatures (>26°C) favouring Ralstonia solanacearum (BARI)"
        }
    },
    "Potato_Leaf_Roll_Virus": {
        "disease_code": "Potato_Leaf_Roll_Virus",
        "crop_name": "Potato",
        "tier": "Core",
        "disease_name_en": "Potato Leaf Roll Virus (PLRV)",
        "disease_name_bn": "আলুর পাতা মোড়ানো ভাইরাস রোগ (PLRV)",
        "infection_category": "Viral Disease",
        "category_key": "viral",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 15.0, "med_max": 38.0},
        "bamis_Rule": {
            "temp_min": 22.0, "temp_max": 31.0,
            "humidity_min": 60.0, "rain_min_mm": 0.0,
            "description": "Mild dry winter temperatures favouring Myzus persicae aphid flights (BARI Tuber Crops)"
        }
    },
    "Potato_Aphid_Cutworm_Pest": {
        "disease_code": "Potato_Aphid_Cutworm_Pest",
        "crop_name": "Potato",
        "tier": "Core",
        "disease_name_en": "Potato Aphid & Foliage Chewing Pest",
        "disease_name_bn": "আলুর জাব পোকা ও পাতা খেকো পোকার আক্রমণ",
        "infection_category": "Pest Damage",
        "category_key": "pest",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 20.0, "med_max": 45.0},
        "bamis_Rule": {
            "temp_min": 23.0, "temp_max": 33.0,
            "humidity_min": 55.0, "rain_min_mm": 0.0,
            "description": "Warm spell in late winter accelerating aphid colonies on potato shoots (DAE)"
        }
    },
    "Potato_Potassium_Deficiency": {
        "disease_code": "Potato_Potassium_Deficiency",
        "crop_name": "Potato",
        "tier": "Core",
        "disease_name_en": "Potassium Scorch / Boron Deficiency",
        "disease_name_bn": "আলুর পটাশ ও বোরনের অভাবজনিত পাতা কিনারা পোড়া",
        "infection_category": "Nutrient Deficiency",
        "category_key": "nutrient deficiency",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 20.0, "med_max": 50.0},
        "bamis_Rule": {
            "temp_min": 15.0, "temp_max": 30.0,
            "humidity_min": 50.0, "rain_min_mm": 5.0,
            "description": "Light flood-plain soils in Rangpur/Bogura lacking balanced MoP and boron (BARI)"
        }
    },
    "Potato_Healthy": {
        "disease_code": "Potato_Healthy",
        "crop_name": "Potato",
        "tier": "Core",
        "disease_name_en": "Healthy Potato Leaf",
        "disease_name_bn": "সুস্থ আলুর পাতা (Healthy Potato Leaf)",
        "infection_category": "Healthy Leaf",
        "category_key": "healthy",
        "is_healthy": True,
        "severity_cutoffs": {"low_max": 5.0, "med_max": 15.0},
        "bamis_Rule": {
            "temp_min": 16.0, "temp_max": 25.0,
            "humidity_min": 50.0, "rain_min_mm": 0.0,
            "description": "Clear sunny winter weather with low relative humidity"
        }
    },

    # --- STRETCH CROPS (Mango, Jute, Chili) ---
    "Mango_Anthracnose": {
        "disease_code": "Mango_Anthracnose",
        "crop_name": "Mango",
        "tier": "Stretch",
        "disease_name_en": "Mango Anthracnose",
        "disease_name_bn": "আমের অ্যানথ্রাকনোজ বা পাতার কালো দাগ রোগ",
        "infection_category": "Fungal Infection",
        "category_key": "fungal",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 20.0, "med_max": 45.0},
        "bamis_Rule": {"temp_min": 25.0, "temp_max": 34.0, "humidity_min": 80.0, "rain_min_mm": 5.0, "description": "Humid monsoon or pre-monsoon showers (>80% RH) in Rajshahi/Chapainawabganj (BARI)"}
    },
    "Mango_Bacterial_Canker": {
        "disease_code": "Mango_Bacterial_Canker",
        "crop_name": "Mango",
        "tier": "Stretch",
        "disease_name_en": "Bacterial Black Spot / Canker",
        "disease_name_bn": "আমের ব্যাকটেরিয়াজনিত কালো দাগ রোগ",
        "infection_category": "Bacterial Infection",
        "category_key": "bacterial",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 20.0, "med_max": 45.0},
        "bamis_Rule": {"temp_min": 27.0, "temp_max": 36.0, "humidity_min": 78.0, "rain_min_mm": 10.0, "description": "Spring storm rain and warm temperatures >28°C (MangoLeafBD / BARI)"}
    },
    "Mango_Hopper_Gall_Midge": {
        "disease_code": "Mango_Hopper_Gall_Midge",
        "crop_name": "Mango",
        "tier": "Stretch",
        "disease_name_en": "Mango Hopper & Gall Midge Damage",
        "disease_name_bn": "আমের হপার ও গল মাছি পোকার আক্রমণ",
        "infection_category": "Pest Damage",
        "category_key": "pest",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 20.0, "med_max": 45.0},
        "bamis_Rule": {"temp_min": 26.0, "temp_max": 36.0, "humidity_min": 65.0, "rain_min_mm": 0.0, "description": "Warm cloudy spring weather during flushing and flowering (DAE)"}
    },
    "Mango_Healthy": {
        "disease_code": "Mango_Healthy",
        "crop_name": "Mango",
        "tier": "Stretch",
        "disease_name_en": "Healthy Mango Leaf",
        "disease_name_bn": "সুস্থ আমের পাতা (Healthy Mango Leaf)",
        "infection_category": "Healthy Leaf",
        "category_key": "healthy",
        "is_healthy": True,
        "severity_cutoffs": {"low_max": 5.0, "med_max": 15.0},
        "bamis_Rule": {"temp_min": 24.0, "temp_max": 33.0, "humidity_min": 50.0, "rain_min_mm": 0.0, "description": "Dry sunny conditions"}
    },
    "Jute_Stem_Rot_Leaf_Blight": {
        "disease_code": "Jute_Stem_Rot_Leaf_Blight",
        "crop_name": "Jute",
        "tier": "Stretch",
        "disease_name_en": "Jute Macrophomina Leaf & Stem Blight",
        "disease_name_bn": "পাটের কান্ড পচা ও পাতা ঝলসানো রোগ",
        "infection_category": "Fungal Infection",
        "category_key": "fungal",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 20.0, "med_max": 45.0},
        "bamis_Rule": {"temp_min": 28.0, "temp_max": 36.0, "humidity_min": 82.0, "rain_min_mm": 10.0, "description": "Hot monsoon humidity (>82% RH) and acidic wet soil (BJRI)"}
    },
    "Jute_Yellow_Mosaic": {
        "disease_code": "Jute_Yellow_Mosaic",
        "crop_name": "Jute",
        "tier": "Stretch",
        "disease_name_en": "Jute Yellow Mosaic Virus",
        "disease_name_bn": "পাটের হলুদ মোজাইক ভাইরাস রোগ",
        "infection_category": "Viral Disease",
        "category_key": "viral",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 20.0, "med_max": 45.0},
        "bamis_Rule": {"temp_min": 28.0, "temp_max": 36.0, "humidity_min": 65.0, "rain_min_mm": 0.0, "description": "Warm weather increasing whitefly transmission on jute foliage (BJRI)"}
    },
    "Jute_Hairy_Caterpillar_Pest": {
        "disease_code": "Jute_Hairy_Caterpillar_Pest",
        "crop_name": "Jute",
        "tier": "Stretch",
        "disease_name_en": "Jute Hairy Caterpillar / Semilooper Damage",
        "disease_name_bn": "পাটের বিছা পোকা ও ঘোড়া পোকার আক্রমণ",
        "infection_category": "Pest Damage",
        "category_key": "pest",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 20.0, "med_max": 45.0},
        "bamis_Rule": {"temp_min": 28.0, "temp_max": 37.0, "humidity_min": 70.0, "rain_min_mm": 0.0, "description": "Warm monsoon breaks favouring Spilosoma obliqua outbreaks (JutePestDetect / BJRI)"}
    },
    "Jute_Healthy": {
        "disease_code": "Jute_Healthy",
        "crop_name": "Jute",
        "tier": "Stretch",
        "disease_name_en": "Healthy Jute Leaf",
        "disease_name_bn": "সুস্থ পাটের পাতা (Healthy Jute Leaf)",
        "infection_category": "Healthy Leaf",
        "category_key": "healthy",
        "is_healthy": True,
        "severity_cutoffs": {"low_max": 5.0, "med_max": 15.0},
        "bamis_Rule": {"temp_min": 26.0, "temp_max": 34.0, "humidity_min": 60.0, "rain_min_mm": 0.0, "description": "Normal monsoon growing conditions"}
    },
    "Chili_Anthracnose_Dieback": {
        "disease_code": "Chili_Anthracnose_Dieback",
        "crop_name": "Chili",
        "tier": "Stretch",
        "disease_name_en": "Chili Anthracnose & Cercospora Leaf Spot",
        "disease_name_bn": "মরিচের অ্যানথ্রাকনোজ ও পাতার দাগ রোগ",
        "infection_category": "Fungal Infection",
        "category_key": "fungal",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 20.0, "med_max": 45.0},
        "bamis_Rule": {"temp_min": 25.0, "temp_max": 33.0, "humidity_min": 80.0, "rain_min_mm": 5.0, "description": "High humidity (>80%) and rain splash on chili foliage (BARI)"}
    },
    "Chili_Leaf_Curl_Virus": {
        "disease_code": "Chili_Leaf_Curl_Virus",
        "crop_name": "Chili",
        "tier": "Stretch",
        "disease_name_en": "Chili Leaf Curl Virus (ChiLCV)",
        "disease_name_bn": "মরিচের পাতা কোঁকড়ানো ভাইরাস রোগ",
        "infection_category": "Viral Disease",
        "category_key": "viral",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 18.0, "med_max": 42.0},
        "bamis_Rule": {"temp_min": 27.0, "temp_max": 37.0, "humidity_min": 55.0, "rain_min_mm": 0.0, "description": "Hot dry weather favouring whitefly and thrips vector activity (BARI)"}
    },
    "Chili_Thrips_Mite_Pest": {
        "disease_code": "Chili_Thrips_Mite_Pest",
        "crop_name": "Chili",
        "tier": "Stretch",
        "disease_name_en": "Chili Thrips & Yellow Mite Damage",
        "disease_name_bn": "মরিচের থ্রিপস ও হলুদ মাকড়ের আক্রমণ",
        "infection_category": "Pest Damage",
        "category_key": "pest",
        "is_healthy": False,
        "severity_cutoffs": {"low_max": 20.0, "med_max": 45.0},
        "bamis_Rule": {"temp_min": 28.0, "temp_max": 38.0, "humidity_min": 50.0, "rain_min_mm": 0.0, "description": "Dry warm spells accelerating thrips and mite curling (DAE)"}
    },
    "Chili_Healthy": {
        "disease_code": "Chili_Healthy",
        "crop_name": "Chili",
        "tier": "Stretch",
        "disease_name_en": "Healthy Chili Leaf",
        "disease_name_bn": "সুস্থ মরিচের পাতা (Healthy Chili Leaf)",
        "infection_category": "Healthy Leaf",
        "category_key": "healthy",
        "is_healthy": True,
        "severity_cutoffs": {"low_max": 5.0, "med_max": 15.0},
        "bamis_Rule": {"temp_min": 22.0, "temp_max": 30.0, "humidity_min": 55.0, "rain_min_mm": 0.0, "description": "Optimal dry weather"}
    }
}

# Maps (crop_name, infection_category) -> canonical disease_code
# This guarantees that even when an infection-category model outputs a category probability distribution,
# or when a crop-specific disease model outputs a disease code, the lookup strictly resolves
# Crop -> Specific Disease -> Category without ever contradicting.
CROP_CATEGORY_TO_DISEASE = {
    ("Rice", "Fungal Infection"): "Rice_Blast",
    ("Rice", "Bacterial Infection"): "Rice_Bacterial_Leaf_Blight",
    ("Rice", "Viral Disease"): "Rice_Tungro",
    ("Rice", "Pest Damage"): "Rice_Hispa_Pest",
    ("Rice", "Nutrient Deficiency"): "Rice_Nitrogen_Deficiency",
    ("Rice", "Healthy Leaf"): "Rice_Healthy",

    ("Tomato", "Fungal Infection"): "Tomato_Late_Blight",
    ("Tomato", "Bacterial Infection"): "Tomato_Bacterial_Spot",
    ("Tomato", "Viral Disease"): "Tomato_Yellow_Leaf_Curl_Virus",
    ("Tomato", "Pest Damage"): "Tomato_Spider_Mite_Pest",
    ("Tomato", "Nutrient Deficiency"): "Tomato_Magnesium_Deficiency",
    ("Tomato", "Healthy Leaf"): "Tomato_Healthy",

    ("Potato", "Fungal Infection"): "Potato_Late_Blight",
    ("Potato", "Bacterial Infection"): "Potato_Bacterial_Wilt",
    ("Potato", "Viral Disease"): "Potato_Leaf_Roll_Virus",
    ("Potato", "Pest Damage"): "Potato_Aphid_Cutworm_Pest",
    ("Potato", "Nutrient Deficiency"): "Potato_Potassium_Deficiency",
    ("Potato", "Healthy Leaf"): "Potato_Healthy",

    ("Mango", "Fungal Infection"): "Mango_Anthracnose",
    ("Mango", "Bacterial Infection"): "Mango_Bacterial_Canker",
    ("Mango", "Viral Disease"): "Mango_Anthracnose",
    ("Mango", "Pest Damage"): "Mango_Hopper_Gall_Midge",
    ("Mango", "Nutrient Deficiency"): "Mango_Anthracnose",
    ("Mango", "Healthy Leaf"): "Mango_Healthy",

    ("Jute", "Fungal Infection"): "Jute_Stem_Rot_Leaf_Blight",
    ("Jute", "Bacterial Infection"): "Jute_Stem_Rot_Leaf_Blight",
    ("Jute", "Viral Disease"): "Jute_Yellow_Mosaic",
    ("Jute", "Pest Damage"): "Jute_Hairy_Caterpillar_Pest",
    ("Jute", "Nutrient Deficiency"): "Jute_Stem_Rot_Leaf_Blight",
    ("Jute", "Healthy Leaf"): "Jute_Healthy",

    ("Chili", "Fungal Infection"): "Chili_Anthracnose_Dieback",
    ("Chili", "Bacterial Infection"): "Chili_Anthracnose_Dieback",
    ("Chili", "Viral Disease"): "Chili_Leaf_Curl_Virus",
    ("Chili", "Pest Damage"): "Chili_Thrips_Mite_Pest",
    ("Chili", "Nutrient Deficiency"): "Chili_Anthracnose_Dieback",
    ("Chili", "Healthy Leaf"): "Chili_Healthy",
}


def resolve_disease_taxonomy(crop_name: str, predicted_class: str, infection_category: str = None) -> dict:
    """
    Strictly resolves (crop_name, predicted_class/category) -> canonical taxonomy entry.
    Ensures the category is ALWAYS looked up from the disease entry so they can never contradict.
    """
    clean_crop = (crop_name or "Tomato").strip().capitalize()
    if clean_crop == "Pepper":
        clean_crop = "Chili"

    # 1. Direct lookup if predicted_class is already a canonical disease_code
    if predicted_class in DISEASE_TAXONOMY:
        return DISEASE_TAXONOMY[predicted_class].copy()

    # 2. Normalize category string
    cat_map = {
        "fungal_infection": "Fungal Infection",
        "fungal infection": "Fungal Infection",
        "fungal": "Fungal Infection",
        "bacterial_infection": "Bacterial Infection",
        "bacterial infection": "Bacterial Infection",
        "bacterial": "Bacterial Infection",
        "viral_disease": "Viral Disease",
        "viral disease": "Viral Disease",
        "viral": "Viral Disease",
        "pest_damage": "Pest Damage",
        "pest damage": "Pest Damage",
        "pest": "Pest Damage",
        "nutrient_deficiency": "Nutrient Deficiency",
        "nutrient deficiency": "Nutrient Deficiency",
        "nutrient": "Nutrient Deficiency",
        "healthy_leaf": "Healthy Leaf",
        "healthy leaf": "Healthy Leaf",
        "healthy": "Healthy Leaf",
    }

    norm_cat = None
    if infection_category:
        norm_cat = cat_map.get(infection_category.strip().lower(), infection_category)
    if not norm_cat and predicted_class:
        norm_cat = cat_map.get(predicted_class.strip().lower(), "Fungal Infection")

    disease_code = CROP_CATEGORY_TO_DISEASE.get((clean_crop, norm_cat))
    if disease_code and disease_code in DISEASE_TAXONOMY:
        entry = DISEASE_TAXONOMY[disease_code].copy()
        # Preserve exact infection_category from the canonical disease entry
        return entry

    # Fallback canonical structure
    is_healthy = norm_cat == "Healthy Leaf"
    return {
        "disease_code": f"{clean_crop}_{norm_cat.replace(' ', '_')}",
        "crop_name": clean_crop,
        "tier": "Core" if clean_crop in CORE_CROPS else "Stretch",
        "disease_name_en": norm_cat,
        "disease_name_bn": norm_cat,
        "infection_category": norm_cat,
        "category_key": "healthy" if is_healthy else norm_cat.split()[0].lower(),
        "is_healthy": is_healthy,
        "severity_cutoffs": {"low_max": 20.0, "med_max": 45.0},
        "bamis_Rule": {
            "temp_min": 22.0, "temp_max": 32.0,
            "humidity_min": 75.0, "rain_min_mm": 2.0,
            "description": "BAMIS regional crop-weather threshold"
        }
    }
