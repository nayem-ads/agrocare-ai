const isLocalVite =
  typeof window !== 'undefined' &&
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') &&
  window.location.port === '3000';

export const BACKEND_URL =
  import.meta.env.VITE_BACKEND_URL || (isLocalVite ? 'http://127.0.0.1:8001' : '');
const API_BASE = `${BACKEND_URL}/api`;

export const resolveStaticUrl = (relativePath) => {
  if (!relativePath) return null;
  if (relativePath.startsWith('http://') || relativePath.startsWith('https://')) {
    return relativePath;
  }
  const clean = relativePath.startsWith('/') ? relativePath.slice(1) : relativePath;
  return `${BACKEND_URL}/${clean}`;
};

// Helper to get auth headers
const getHeaders = (isMultipart = false) => {
  const token = localStorage.getItem('token');
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  if (!isMultipart) {
    headers['Content-Type'] = 'application/json';
  }
  return headers;
};

// Handle response wrapper
const handleResponse = async (res) => {
  if (res.status === 401 && !res.url.includes('/auth/login')) {
    localStorage.clear();
    if (typeof window !== 'undefined') {
      window.location.href = '/login?expired=true';
    }
  }
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || 'An error occurred during request execution.');
  }
  return res.json();
};

export const api = {
  // Auth
  register: async (name, email, password, role = 'farmer') => {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ name, email, password, role }),
    });
    return handleResponse(res);
  },

  login: async (email, password) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ email, password }),
    });
    return handleResponse(res);
  },

  // Stage 1: Photo Quality & Leaf Gate Pre-Check (P0)
  checkPhotoQuality: async (formData) => {
    const res = await fetch(`${API_BASE}/quality-check`, {
      method: 'POST',
      headers: getHeaders(true),
      body: formData,
    });
    return handleResponse(res);
  },

  // Auto-Resolve GPS Location -> District, Upazila & BAMIS Weather
  resolveLocation: async (lat, lon) => {
    const res = await fetch(`${API_BASE}/resolve-location?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`, {
      method: 'GET',
    });
    return handleResponse(res);
  },

  // Full 6-Stage Prediction Pipeline
  predict: async (formData) => {
    const res = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: getHeaders(true),
      body: formData,
    });
    return handleResponse(res);
  },

  // Reports (Farmer)
  getMyReports: async () => {
    const res = await fetch(`${API_BASE}/reports/my`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getReportDetails: async (id) => {
    const res = await fetch(`${API_BASE}/reports/${id}`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  // Admin & Officer Dashboard
  getAdminReports: async () => {
    const res = await fetch(`${API_BASE}/admin/reports`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getAdminSummary: async () => {
    const res = await fetch(`${API_BASE}/admin/summary`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getSeverityDistribution: async () => {
    const res = await fetch(`${API_BASE}/admin/severity-distribution`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getCropDistribution: async () => {
    const res = await fetch(`${API_BASE}/admin/crop-distribution`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getDiseaseTypeDistribution: async () => {
    const res = await fetch(`${API_BASE}/admin/disease-type-distribution`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getDiseaseMap: async () => {
    const res = await fetch(`${API_BASE}/admin/disease-map`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getWeatherRisk: async () => {
    const res = await fetch(`${API_BASE}/admin/weather-risk`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  // Officer Review Queue (RQ2 & RQ5)
  getOfficerReviewQueue: async () => {
    const res = await fetch(`${API_BASE}/admin/review-queue`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  submitOfficerReview: async (reportId, payload) => {
    const res = await fetch(`${API_BASE}/admin/review/${reportId}`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload),
    });
    return handleResponse(res);
  },

  // Outbreak Alerts (P1)
  getOutbreakAlerts: async () => {
    const res = await fetch(`${API_BASE}/admin/outbreak-alerts`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  // Model Version Registry & Retraining Loop (RQ5)
  getModelVersions: async () => {
    const res = await fetch(`${API_BASE}/admin/model-versions`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  exportVerifiedDataset: async () => {
    const res = await fetch(`${API_BASE}/admin/export-verified-dataset`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  retrainFromCorrections: async () => {
    const res = await fetch(`${API_BASE}/admin/retrain-from-corrections`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  uploadColabModel: async (formData) => {
    const res = await fetch(`${API_BASE}/admin/upload-colab-model`, {
      method: 'POST',
      headers: getHeaders(true),
      body: formData,
    });
    return handleResponse(res);
  },

  // Research Benchmarks & Canonical Taxonomy (RQ1-RQ5)
  getResearchBenchmarks: async () => {
    const res = await fetch(`${API_BASE}/research-benchmarks`, {
      method: 'GET',
    });
    return handleResponse(res);
  },

  getDiseaseCatalog: async () => {
    const res = await fetch(`${API_BASE}/disease-catalog`, {
      method: 'GET',
    });
    return handleResponse(res);
  },

  getModelStatus: async () => {
    const res = await fetch(`${API_BASE}/model/status`, {
      method: 'GET',
    });
    return handleResponse(res);
  },

  // Health
  getHealth: async () => {
    const res = await fetch(`${API_BASE}/health`, {
      method: 'GET',
    });
    return handleResponse(res);
  }
};
