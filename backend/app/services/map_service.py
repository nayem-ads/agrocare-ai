# -*- coding: utf-8 -*-
"""
AgroCare AI — High-Precision Bangladesh District, Thana & Upazila Geospatial Resolver
Owner: Nur Shad Srabon (Backend & Intelligence Lead)
"""

import math
import random

# Primary District index (used by Admin Weather Risk & Seeding)
DISTRICT_COORDINATES = {
    "Dhaka": {"lat": 23.7652, "lon": 90.4396, "upazila": "Banasree / Rampura Thana"},
    "Bogura": {"lat": 24.8481, "lon": 89.3730, "upazila": "Shibganj Upazila"},
    "Rajshahi": {"lat": 24.3636, "lon": 88.6241, "upazila": "Godagari Upazila"},
    "Rangpur": {"lat": 25.7558, "lon": 89.2447, "upazila": "Mithapukur Upazila"},
    "Mymensingh": {"lat": 24.7471, "lon": 90.4203, "upazila": "Trishal Upazila"},
    "Dinajpur": {"lat": 25.6217, "lon": 88.6358, "upazila": "Birganj Upazila"},
    "Jessore": {"lat": 23.1664, "lon": 89.2081, "upazila": "Jhikargachha Upazila"},
    "Chittagong": {"lat": 22.3569, "lon": 91.7832, "upazila": "Hathazari Upazila"},
    "Khulna": {"lat": 22.8456, "lon": 89.5403, "upazila": "Dumuria Upazila"},
    "Sylhet": {"lat": 24.8949, "lon": 91.8687, "upazila": "Golapganj Upazila"},
    "Barisal": {"lat": 22.7010, "lon": 90.3535, "upazila": "Babuganj Upazila"},
    "Comilla": {"lat": 23.4682, "lon": 91.1782, "upazila": "Burichang Upazila"},
    "Chapainawabganj": {"lat": 24.5965, "lon": 88.2775, "upazila": "Shibganj (Chapai) Upazila"},
    "Faridpur": {"lat": 23.6070, "lon": 89.8429, "upazila": "Bhanga Upazila"},
    "Gazipur": {"lat": 23.9999, "lon": 90.4203, "upazila": "Gazipur Sadar Upazila"},
    "Narayanganj": {"lat": 23.6238, "lon": 90.5000, "upazila": "Sonargaon Upazila"},
    "Tangail": {"lat": 24.2513, "lon": 89.9167, "upazila": "Madhupur Upazila"},
    "Bogra": {"lat": 24.8481, "lon": 89.3730, "upazila": "Shibganj Upazila"},
    "Coxs Bazar": {"lat": 21.4272, "lon": 92.0058, "upazila": "Chakaria Upazila"}
}

# Fine-grained Sub-District / Thana / Upazila Gazetteer for exact GPS reverse-geocoding
SUBDISTRICT_GAZETTEER = [
    # Dhaka Metropolitan Thanas & Suburbs
    {"district": "Dhaka", "upazila": "Banasree / Rampura", "lat": 23.7652, "lon": 90.4396},
    {"district": "Dhaka", "upazila": "Aftabnagar / Badda", "lat": 23.7735, "lon": 90.4360},
    {"district": "Dhaka", "upazila": "Khilgaon / Goran", "lat": 23.7515, "lon": 90.4290},
    {"district": "Dhaka", "upazila": "Gulshan / Banani", "lat": 23.7925, "lon": 90.4078},
    {"district": "Dhaka", "upazila": "Bashundhara / Vatara", "lat": 23.8191, "lon": 90.4350},
    {"district": "Dhaka", "upazila": "Uttara", "lat": 23.8759, "lon": 90.3795},
    {"district": "Dhaka", "upazila": "Mirpur", "lat": 23.8067, "lon": 90.3686},
    {"district": "Dhaka", "upazila": "Mohammadpur", "lat": 23.7658, "lon": 90.3584},
    {"district": "Dhaka", "upazila": "Dhanmondi", "lat": 23.7461, "lon": 90.3742},
    {"district": "Dhaka", "upazila": "Tejgaon / Farmgate", "lat": 23.7580, "lon": 90.3910},
    {"district": "Dhaka", "upazila": "Motijheel / Paltan", "lat": 23.7330, "lon": 90.4172},
    {"district": "Dhaka", "upazila": "Shahbagh / Ramna", "lat": 23.7389, "lon": 90.3956},
    {"district": "Dhaka", "upazila": "Jatrabari / Demra", "lat": 23.7104, "lon": 90.4348},
    {"district": "Dhaka", "upazila": "Savar Upazila", "lat": 23.8583, "lon": 90.2667},
    {"district": "Dhaka", "upazila": "Dhamrai Upazila", "lat": 23.9140, "lon": 90.2170},
    {"district": "Dhaka", "upazila": "Keraniganj Upazila", "lat": 23.6942, "lon": 90.3456},
    # Surrounding & Regional Agricultural Hubs
    {"district": "Gazipur", "upazila": "Gazipur Sadar / Joydebpur", "lat": 23.9999, "lon": 90.4203},
    {"district": "Gazipur", "upazila": "Kaliakair Upazila", "lat": 24.0750, "lon": 90.2180},
    {"district": "Narayanganj", "upazila": "Narayanganj Sadar / Rupganj", "lat": 23.6238, "lon": 90.5000},
    {"district": "Bogura", "upazila": "Shibganj Upazila", "lat": 24.8481, "lon": 89.3730},
    {"district": "Bogura", "upazila": "Sherpur Upazila", "lat": 24.6710, "lon": 89.4160},
    {"district": "Rajshahi", "upazila": "Godagari Upazila", "lat": 24.3636, "lon": 88.6241},
    {"district": "Rajshahi", "upazila": "Paba Upazila", "lat": 24.4210, "lon": 88.6100},
    {"district": "Rangpur", "upazila": "Mithapukur Upazila", "lat": 25.7558, "lon": 89.2447},
    {"district": "Mymensingh", "upazila": "Trishal Upazila", "lat": 24.7471, "lon": 90.4203},
    {"district": "Dinajpur", "upazila": "Birganj Upazila", "lat": 25.6217, "lon": 88.6358},
    {"district": "Jessore", "upazila": "Jhikargachha Upazila", "lat": 23.1664, "lon": 89.2081},
    {"district": "Chittagong", "upazila": "Hathazari Upazila", "lat": 22.3569, "lon": 91.7832},
    {"district": "Khulna", "upazila": "Dumuria Upazila", "lat": 22.8456, "lon": 89.5403},
    {"district": "Sylhet", "upazila": "Golapganj Upazila", "lat": 24.8949, "lon": 91.8687},
    {"district": "Barisal", "upazila": "Babuganj Upazila", "lat": 22.7010, "lon": 90.3535},
    {"district": "Comilla", "upazila": "Burichang Upazila", "lat": 23.4682, "lon": 91.1782},
    {"district": "Chapainawabganj", "upazila": "Shibganj (Chapai) Upazila", "lat": 24.5965, "lon": 88.2775},
    {"district": "Faridpur", "upazila": "Bhanga Upazila", "lat": 23.6070, "lon": 89.8429},
    {"district": "Tangail", "upazila": "Madhupur Upazila", "lat": 24.2513, "lon": 89.9167},
    {"district": "Coxs Bazar", "upazila": "Chakaria Upazila", "lat": 21.4272, "lon": 92.0058},
]


def get_district_coordinates(name: str) -> dict:
    """
    Returns the latitude, longitude, and primary agricultural upazila of a Bangladesh district.
    """
    if name in DISTRICT_COORDINATES:
        return DISTRICT_COORDINATES[name]

    return {
        "lat": 23.7652 + random.uniform(-0.3, 0.3),
        "lon": 90.4396 + random.uniform(-0.3, 0.3),
        "upazila": "Banasree / Rampura"
    }


def resolve_district_upazila(lat: float = None, lon: float = None) -> tuple[str, str, str]:
    """
    Finds the nearest Bangladesh district and Thana/Upazila for a (lat, lon) pair
    using the fine-grained SUBDISTRICT_GAZETTEER and returns (district, upazila, postgis_wkt).
    """
    c_lat = float(lat) if lat is not None else 23.7652
    c_lon = float(lon) if lon is not None else 90.4396

    best_dist = "Dhaka"
    best_upazila = "Banasree / Rampura"
    min_d = 999999.0

    for entry in SUBDISTRICT_GAZETTEER:
        dist = math.hypot(c_lat - entry["lat"], c_lon - entry["lon"])
        if dist < min_d:
            min_d = dist
            best_dist = entry["district"]
            best_upazila = entry["upazila"]

    wkt = f"SRID=4326;POINT({c_lon:.5f} {c_lat:.5f})"
    return best_dist, best_upazila, wkt


def get_random_district() -> str:
    return random.choice(list(DISTRICT_COORDINATES.keys()))
