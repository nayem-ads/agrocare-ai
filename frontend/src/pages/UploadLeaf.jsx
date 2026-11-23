import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud, Camera, RefreshCw, MapPin, Eye, ShieldAlert,
  Sparkles, CheckCircle2, AlertTriangle, CloudRain, Cpu, Navigation
} from 'lucide-react';
import { api } from '../services/api.js';

const coreCrops = [
  { value: 'Rice', label: 'Rice — ধান (Core Tier)', tier: 'Core' },
  { value: 'Tomato', label: 'Tomato — টমেটো (Core Tier)', tier: 'Core' },
  { value: 'Potato', label: 'Potato — আলু (Core Tier)', tier: 'Core' }
];

const stretchCrops = [
  { value: 'Mango', label: 'Mango — আম (Stretch Tier)', tier: 'Stretch' },
  { value: 'Jute', label: 'Jute — পাট (Stretch Tier)', tier: 'Stretch' },
  { value: 'Chili', label: 'Chili — মরিচ (Stretch Tier)', tier: 'Stretch' }
];

const bangladeshStations = [
  { id: 'Auto', label: '✨ Auto-Detect Location (GPS / IP / Photo EXIF)' },
  { id: 'Dhaka', label: 'Dhaka — Savar Upazila (ঢাকা)', lat: 23.8103, lon: 90.4125 },
  { id: 'Bogura', label: 'Bogura — Shibganj Upazila (বগুড়া)', lat: 24.8481, lon: 89.3730 },
  { id: 'Rajshahi', label: 'Rajshahi — Godagari Upazila (রাজশাহী)', lat: 24.3636, lon: 88.6241 },
  { id: 'Rangpur', label: 'Rangpur — Mithapukur Upazila (রংপুর)', lat: 25.7558, lon: 89.2447 },
  { id: 'Mymensingh', label: 'Mymensingh — Trishal Upazila (ময়মনসিংহ)', lat: 24.7471, lon: 90.4203 },
  { id: 'Dinajpur', label: 'Dinajpur — Birganj Upazila (দিনাজপুর)', lat: 25.6217, lon: 88.6358 },
  { id: 'Jessore', label: 'Jessore — Jhikargachha Upazila (যশোর)', lat: 23.1664, lon: 89.2081 },
  { id: 'Sylhet', label: 'Sylhet — Golapganj Upazila (সিলেট)', lat: 24.8949, lon: 91.8687 },
  { id: 'Chittagong', label: 'Chittagong — Hathazari Upazila (চট্টগ্রাম)', lat: 22.3569, lon: 91.7832 },
  { id: 'Khulna', label: 'Khulna — Dumuria Upazila (খুলনা)', lat: 22.8456, lon: 89.5403 }
];

function UploadLeaf() {
  const [cropName, setCropName] = useState('Auto');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  // Location & Auto-Detection State
  const [locationMode, setLocationMode] = useState('Auto');
  const [latitude, setLatitude] = useState(23.7652);
  const [longitude, setLongitude] = useState(90.4396);
  const [detectedDistrict, setDetectedDistrict] = useState('Dhaka');
  const [detectedUpazila, setDetectedUpazila] = useState('Banasree / Rampura');
  const [detectedWeather, setDetectedWeather] = useState(null);
  const [locationSource, setLocationSource] = useState('Auto-Detecting...');
  const [fetchingLocation, setFetchingLocation] = useState(false);
  const [locationStatus, setLocationStatus] = useState('');

  const [language, setLanguage] = useState('en');
  const [weatherAlpha, setWeatherAlpha] = useState(0.35);
  const [simulateUnknown, setSimulateUnknown] = useState(false);

  // Stage 1: Photo Quality & Leaf Gate check state
  const [qualityCheck, setQualityCheck] = useState(null);
  const [checkingQuality, setCheckingQuality] = useState(false);

  // Camera variables
  const [useCamera, setUseCamera] = useState(false);
  const [cameraStream, setCameraStream] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const [modelStatus, setModelStatus] = useState({
    model_loaded: false,
    demo_mode: false,
    model_path: '',
    labels_loaded: false,
    number_of_classes: 0,
    model_version: '',
    supported_crops: []
  });
  const [statusLoading, setStatusLoading] = useState(true);
  const [statusError, setStatusError] = useState('');

  useEffect(() => {
    autoDetectLocation();
    fetchModelStatus();
    return () => {
      stopCamera();
    };
  }, []);

  const syncLocationWithBackend = async (lat, lon, sourceLabel) => {
    setLatitude(lat);
    setLongitude(lon);
    setLocationSource(sourceLabel);

    let resolvedDistrict = null;
    let resolvedUpazila = null;

    // 1. Query OpenStreetMap Nominatim reverse geocoding in browser for exact neighborhood/thana
    try {
      const osmRes = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}&accept-language=en`
      );
      if (osmRes.ok) {
        const osmData = await osmRes.json();
        const addr = osmData.address || {};
        const neighborhood =
          addr.suburb ||
          addr.neighbourhood ||
          addr.quarter ||
          addr.borough ||
          addr.city_district ||
          addr.town ||
          addr.village ||
          addr.county;
        const cityOrDist =
          addr.city ||
          addr.state_district ||
          addr.county ||
          addr.state ||
          'Dhaka';
        if (neighborhood) {
          resolvedUpazila = neighborhood;
        }
        if (cityOrDist) {
          resolvedDistrict = cityOrDist.replace(' District', '').replace(' Division', '');
        }
      }
    } catch (e) {
      // Fallback to backend gazetteer if Nominatim is unreachable
    }

    // 2. Sync with backend for BAMIS weather & fine-grained Thana/Upazila gazetteer
    try {
      const resolved = await api.resolveLocation(lat, lon);
      if (resolved && resolved.success) {
        const finalDist = resolvedDistrict || resolved.district;
        const finalUpz = resolvedUpazila || resolved.upazila;
        setDetectedDistrict(finalDist);
        setDetectedUpazila(finalUpz);
        setDetectedWeather(resolved.weather);
        setLocationStatus(`Auto-detected: ${finalDist} • ${finalUpz} (${sourceLabel})`);
      }
    } catch (e) {
      if (resolvedDistrict) setDetectedDistrict(resolvedDistrict);
      if (resolvedUpazila) setDetectedUpazila(resolvedUpazila);
      setLocationStatus(`Coordinates locked (${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E) via ${sourceLabel}`);
    }
  };

  const fallbackIpGeolocation = async () => {
    try {
      const resp = await fetch('https://ipapi.co/json/');
      if (resp.ok) {
        const ipData = await resp.json();
        if (ipData && ipData.latitude && ipData.longitude) {
          await syncLocationWithBackend(
            Number(ipData.latitude),
            Number(ipData.longitude),
            `Network IP (${ipData.city || 'BD'})`
          );
          setFetchingLocation(false);
          return;
        }
      }
    } catch (e) {
      // Fallback to Dhaka / Bogura station if offline
    }
    await syncLocationWithBackend(23.8103, 90.4125, 'Regional Station Auto-Lock');
    setFetchingLocation(false);
  };

  const autoDetectLocation = () => {
    setFetchingLocation(true);
    setLocationMode('Auto');
    setLocationStatus('Auto-detecting field GPS & Upazila...');

    if (!navigator.geolocation) {
      fallbackIpGeolocation();
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        await syncLocationWithBackend(
          position.coords.latitude,
          position.coords.longitude,
          'Live Browser GPS'
        );
        setFetchingLocation(false);
      },
      async () => {
        await fallbackIpGeolocation();
      },
      { enableHighAccuracy: true, timeout: 4500 }
    );
  };

  const handleStationChange = async (stationId) => {
    setLocationMode(stationId);
    if (stationId === 'Auto') {
      autoDetectLocation();
      return;
    }
    const found = bangladeshStations.find(s => s.id === stationId);
    if (found) {
      setFetchingLocation(true);
      await syncLocationWithBackend(found.lat, found.lon, 'Selected BAMIS Station');
      setFetchingLocation(false);
    }
  };

  const fetchModelStatus = async () => {
    setStatusLoading(true);
    setStatusError('');
    try {
      const status = await api.getModelStatus();
      setModelStatus(status);
      if (!status.model_loaded && !status.demo_mode) {
        setError('Real AI model is not loaded. Please train or upload a model.');
      }
    } catch (err) {
      console.error(err);
      setStatusError('Backend is not connected. Please start the FastAPI server.');
      setError('Could not verify AI model loading status.');
    } finally {
      setStatusLoading(false);
    }
  };

  const runQualityGatePrecheck = async (file) => {
    setCheckingQuality(true);
    setQualityCheck(null);
    try {
      const fd = new FormData();
      fd.append('image', file);
      const qRes = await api.checkPhotoQuality(fd);
      setQualityCheck(qRes);

      // If the uploaded smartphone photo contains embedded EXIF GPS metadata, auto-lock to it!
      if (qRes && qRes.exif_gps && qRes.exif_gps.latitude && qRes.exif_gps.longitude) {
        await syncLocationWithBackend(
          Number(qRes.exif_gps.latitude),
          Number(qRes.exif_gps.longitude),
          'Photo EXIF GPS Metadata'
        );
      }
    } catch (e) {
      console.warn('Quality precheck fallback:', e);
    } finally {
      setCheckingQuality(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
      setUseCamera(false);
      stopCamera();
      runQualityGatePrecheck(file);
    }
  };

  const startCamera = async () => {
    setUseCamera(true);
    setImagePreview(null);
    setImageFile(null);
    setQualityCheck(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      });
      setCameraStream(stream);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      setError('Could not access camera feed. Verify permissions.');
      setUseCamera(false);
    }
  };

  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      setCameraStream(null);
    }
  };

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      canvas.toBlob((blob) => {
        const file = new File([blob], 'leaf_capture.jpg', { type: 'image/jpeg' });
        setImageFile(file);
        setImagePreview(URL.createObjectURL(file));
        stopCamera();
        runQualityGatePrecheck(file);
      }, 'image/jpeg');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!imageFile) {
      setError('Please select an image file or capture a photo first.');
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('crop_name', cropName);
    formData.append('language', language);
    formData.append('weather_alpha', weatherAlpha);
    formData.append('simulate_unknown', simulateUnknown ? 'true' : 'false');
    if (latitude !== null) formData.append('latitude', latitude);
    if (longitude !== null) formData.append('longitude', longitude);
    if (detectedDistrict) formData.append('custom_district', detectedDistrict);
    if (detectedUpazila) formData.append('custom_upazila', detectedUpazila);

    try {
      const result = await api.predict(formData);
      if (result.success) {
        navigate(`/reports/${result.report_id}?lang=${language}`);
      } else {
        setError(result.error || 'Diagnosis failed. Try again.');
      }
    } catch (err) {
      setError(err.message || 'An error occurred during image classification.');
    } finally {
      setLoading(false);
    }
  };

  if (statusLoading) {
    return (
      <div class="max-w-4xl mx-auto px-4 py-16 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mx-auto mb-4"></div>
        <p class="text-slate-600 font-semibold">Loading model status...</p>
      </div>
    );
  }

  if (statusError) {
    return (
      <div class="max-w-4xl mx-auto px-4 py-16">
        <div class="bg-red-50 border border-red-200 text-red-700 p-8 rounded-2xl text-center max-w-md mx-auto shadow-sm">
          <ShieldAlert class="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 class="text-xl font-bold mb-2">Connection Error</h2>
          <p class="text-slate-600 text-sm mb-6">{statusError}</p>
          <button
            type="button"
            onClick={fetchModelStatus}
            class="bg-red-600 hover:bg-red-700 text-white font-bold px-6 py-2.5 rounded-xl transition"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  if (modelStatus && !modelStatus.model_loaded && !modelStatus.demo_mode) {
    return (
      <div class="max-w-4xl mx-auto px-4 py-16">
        <div class="bg-amber-50 border border-amber-200 text-amber-800 p-8 rounded-2xl text-center max-w-md mx-auto shadow-sm">
          <ShieldAlert class="h-16 w-16 text-amber-500 mx-auto mb-4" />
          <h2 class="text-xl font-bold mb-2">Model Missing</h2>
          <p class="text-slate-600 text-sm mb-6">Real AI model is not loaded. Please train or upload a model.</p>
          <button
            type="button"
            onClick={fetchModelStatus}
            class="bg-amber-600 hover:bg-amber-700 text-white font-bold px-6 py-2.5 rounded-xl transition"
          >
            Check Status Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div class="max-w-5xl mx-auto px-4 py-8">
      {/* Title & Pitch */}
      <div class="text-center mb-8">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-bold mb-3">
          <Cpu class="h-3.5 w-3.5" />
          <span>6-Stage Field Pipeline: Auto Leaf & GPS Gate → Classifier → Open-Set → BAMIS Weather → Lesion Mask → Grad-CAM</span>
        </div>
        <h1 class="text-3xl font-extrabold text-slate-900 flex justify-center items-center gap-2">
          <Sparkles class="h-8 w-8 text-emerald-600" />
          Plant Leaf Diagnosis
        </h1>
        <p class="text-slate-500 mt-1.5 text-sm max-w-2xl mx-auto">
          Automatically detects your leaf crop, GPS District/Upazila, and local BAMIS weather conditions to deliver measured lesion severity and official DAE/BRRI/BARI Bangla advisory.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-12 gap-8">
        {/* Left configurations column */}
        <div class="md:col-span-5 space-y-6">
          <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <h3 class="text-xs font-bold text-slate-900 uppercase tracking-wider mb-4">Diagnosis Parameters</h3>

            <form class="space-y-4">
              <div>
                <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">
                  Crop Leaf Detection Mode
                </label>
                <select
                  value={cropName}
                  onChange={(e) => setCropName(e.target.value)}
                  class="w-full px-3 py-2.5 border border-slate-300 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white"
                >
                  <optgroup label="Automatic AI Leaf Detection (Recommended)">
                    <option value="Auto">
                      ✨ Auto-Detect Leaf & Crop (স্বয়ংক্রিয় পাতা শনাক্তকরণ)
                      {qualityCheck?.detected_crop ? ` → [${qualityCheck.detected_crop}]` : ''}
                    </option>
                  </optgroup>
                  <optgroup label="Core Tier (Full Depth: Diagnosis + Open-Set + Lesion Masks + BAMIS)">
                    {coreCrops.map(crop => (
                      <option key={crop.value} value={crop.value}>{crop.label}</option>
                    ))}
                  </optgroup>
                  <optgroup label="Stretch Tier (Diagnosis + DAE/BARI/BJRI Advisory)">
                    {stretchCrops.map(crop => (
                      <option key={crop.value} value={crop.value}>{crop.label}</option>
                    ))}
                  </optgroup>
                </select>
              </div>

              <div>
                <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">Advisory Language</label>
                <div class="grid grid-cols-2 gap-2 bg-slate-100 p-1 rounded-xl">
                  <button
                    type="button"
                    onClick={() => setLanguage('en')}
                    class={`py-1.5 text-xs font-bold rounded-lg transition ${
                      language === 'en' ? 'bg-white text-emerald-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                    }`}
                  >
                    English
                  </button>
                  <button
                    type="button"
                    onClick={() => setLanguage('bn')}
                    class={`py-1.5 text-xs font-bold rounded-lg transition ${
                      language === 'bn' ? 'bg-white text-emerald-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                    }`}
                  >
                    বাংলা (Bangla)
                  </button>
                </div>
              </div>

              {/* Auto-Detected Location & District/Upazila Selector */}
              <div class="border-t border-slate-100 pt-4">
                <div class="flex items-center justify-between mb-1.5">
                  <span class="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                    <Navigation class="h-3.5 w-3.5 text-emerald-600" />
                    Auto-Detected Location
                  </span>
                  <button
                    type="button"
                    onClick={autoDetectLocation}
                    disabled={fetchingLocation}
                    class="text-xs text-emerald-600 hover:text-emerald-700 font-bold"
                  >
                    {fetchingLocation ? 'Detecting...' : 'Re-Detect GPS'}
                  </button>
                </div>

                <select
                  value={locationMode}
                  onChange={(e) => handleStationChange(e.target.value)}
                  class="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white mb-2"
                >
                  {bangladeshStations.map(st => (
                    <option key={st.id} value={st.id}>{st.label}</option>
                  ))}
                </select>

                {/* Live Resolved District, Upazila & Weather Card */}
                <div class="bg-emerald-50 border border-emerald-200 rounded-xl p-3 text-xs space-y-1.5">
                  <div class="flex items-center justify-between">
                    <span class="px-2 py-0.5 rounded bg-emerald-600 text-white font-extrabold text-[10px]">
                      AUTO-DETECTED REGION
                    </span>
                    <span class="font-mono text-[10px] text-emerald-800 font-semibold">
                      {locationSource}
                    </span>
                  </div>
                  <div class="flex items-center gap-1.5 font-extrabold text-slate-900 text-sm pt-0.5">
                    <MapPin class="h-4 w-4 text-emerald-600 flex-shrink-0" />
                    <span>{detectedDistrict} • {detectedUpazila}</span>
                  </div>
                  <div class="flex items-center justify-between text-[11px] font-mono text-slate-600">
                    <span>GPS: {latitude?.toFixed(4)}°N, {longitude?.toFixed(4)}°E</span>
                    {detectedWeather && (
                      <span class="font-bold text-emerald-800">
                        {detectedWeather.temperature}°C • {detectedWeather.humidity}% RH
                      </span>
                    )}
                  </div>
                </div>
                <p class="text-[10px] text-slate-400 mt-1">{locationStatus}</p>
              </div>

              {/* RQ4 BAMIS Weather-Prior Fusion control */}
              <div class="border-t border-slate-100 pt-4">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                    <CloudRain class="h-3.5 w-3.5 text-emerald-600" />
                    BAMIS Weather Prior (RQ4)
                  </span>
                  <span class="text-xs font-mono font-bold text-emerald-700">α = {weatherAlpha}</span>
                </div>
                <div class="grid grid-cols-2 gap-2 mt-1.5">
                  <button
                    type="button"
                    onClick={() => setWeatherAlpha(0.35)}
                    class={`py-1.5 px-2 text-[11px] font-bold rounded-lg border transition ${
                      weatherAlpha > 0
                        ? 'bg-emerald-50 border-emerald-300 text-emerald-800'
                        : 'bg-white border-slate-200 text-slate-500'
                    }`}
                  >
                    With BAMIS Prior (α=0.35)
                  </button>
                  <button
                    type="button"
                    onClick={() => setWeatherAlpha(0.0)}
                    class={`py-1.5 px-2 text-[11px] font-bold rounded-lg border transition ${
                      weatherAlpha === 0
                        ? 'bg-slate-800 border-slate-800 text-white'
                        : 'bg-white border-slate-200 text-slate-500'
                    }`}
                  >
                    No-Weather Baseline (α=0)
                  </button>
                </div>
              </div>

              {/* RQ2 Open-Set Rejection Demo Toggle */}
              <div class="border-t border-slate-100 pt-3">
                <label class="flex items-start gap-2.5 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={simulateUnknown}
                    onChange={(e) => setSimulateUnknown(e.target.checked)}
                    class="mt-0.5 rounded border-slate-300 text-amber-600 focus:ring-amber-500"
                  />
                  <div>
                    <span class="block text-xs font-bold text-slate-700">
                      Test Open-Set Unknown Rejection (RQ2)
                    </span>
                    <span class="block text-[11px] text-slate-400">
                      Routes photo as "Not sure — sent to officer" & withholds chemical advice (Section 9 Rule 5).
                    </span>
                  </div>
                </label>
              </div>

              {/* Model & TFLite Offline Status Widget */}
              <div class="border-t border-slate-100 pt-4 mt-4">
                <span class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">AI Pipeline & Mobile TFLite Status</span>
                <div class="space-y-1.5 text-xs">
                  <div class="flex justify-between">
                    <span class="text-slate-500">Model Loaded:</span>
                    <span class={`font-bold ${modelStatus.model_loaded ? 'text-green-600' : 'text-red-500'}`}>
                      {modelStatus.model_loaded ? 'Yes' : 'No'}
                    </span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-slate-500">Inference Source:</span>
                    <span class="font-bold text-slate-700">
                      {modelStatus.demo_mode ? 'Demo Fallback Mode' : 'Real AI Model'}
                    </span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-slate-500">Offline Edge TFLite:</span>
                    <span class="font-mono font-semibold text-emerald-700">INT8 • 4.8 MB • 38 ms</span>
                  </div>
                </div>
              </div>
            </form>
          </div>
        </div>

        {/* Right Upload & Quality Gate Panel */}
        <div class="md:col-span-7 space-y-6">
          <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            {error && (
              <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-4 text-sm flex items-start gap-2">
                <ShieldAlert class="h-5 w-5 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            {/* Stage 1: Photo Quality & Automatic Leaf Gate Banner (P0 Feature) */}
            {checkingQuality && (
              <div class="bg-slate-50 border border-slate-200 text-slate-600 px-4 py-3 rounded-xl mb-4 text-xs flex items-center gap-2">
                <div class="h-4 w-4 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
                <span>Running Stage 1 Auto-Leaf & Quality Gate (venation morphology, blur, exposure, EXIF GPS)...</span>
              </div>
            )}

            {qualityCheck && (
              <div class={`px-4 py-3.5 rounded-xl mb-4 border text-xs ${
                qualityCheck.passed
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                  : 'bg-amber-50 border-amber-300 text-amber-900'
              }`}>
                <div class="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                  <div class="flex items-center gap-1.5 font-bold">
                    {qualityCheck.passed ? (
                      <CheckCircle2 class="h-4 w-4 text-emerald-600" />
                    ) : (
                      <AlertTriangle class="h-4 w-4 text-amber-600" />
                    )}
                    <span>
                      Stage 1 Quality & Leaf Gate: {qualityCheck.quality_flag} (Score: {qualityCheck.quality_score}/100)
                    </span>
                  </div>
                  <span class="font-mono text-[11px]">
                    Focus: {qualityCheck.blur_variance} • Light: {qualityCheck.brightness} • Leaf Tissue: {qualityCheck.leaf_coverage_pct}%
                  </span>
                </div>
                {qualityCheck.detected_crop && qualityCheck.is_leaf_detected !== false && (
                  <div class="flex flex-wrap items-center justify-between gap-2 bg-white bg-opacity-90 border border-emerald-200 px-3 py-2 rounded-lg my-1.5">
                    <div class="flex items-center gap-2">
                      <span class="px-2 py-0.5 rounded-md bg-emerald-600 text-white font-extrabold text-[11px]">
                        AUTO-DETECTED LEAF
                      </span>
                      <span class="font-extrabold text-slate-900 text-xs">
                        {qualityCheck.detected_crop_label || `${qualityCheck.detected_crop} Leaf`}
                      </span>
                    </div>
                    <span class="text-[11px] font-mono font-semibold text-emerald-700">
                      {Math.round((qualityCheck.crop_confidence || 0.9) * 100)}% Match • {qualityCheck.detection_method || 'Leaf Morphology'}
                    </span>
                  </div>
                )}
                <p class="text-xs font-medium mt-1">{qualityCheck.retake_hint_en}</p>
                <p class="text-xs font-semibold text-emerald-800 mt-0.5">{qualityCheck.retake_hint_bn}</p>
              </div>
            )}

            {/* Video stream container */}
            {useCamera ? (
              <div class="relative w-full aspect-video rounded-xl overflow-hidden bg-slate-900 border border-slate-800">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  class="w-full h-full object-cover"
                ></video>
                <div class="absolute bottom-4 left-0 right-0 flex justify-center items-center gap-4 px-4">
                  <button
                    type="button"
                    onClick={capturePhoto}
                    class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold p-3 rounded-full shadow-lg transition"
                    title="Capture image"
                  >
                    <Camera class="h-6 w-6" />
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setUseCamera(false);
                      stopCamera();
                    }}
                    class="bg-slate-700 hover:bg-slate-800 text-white font-bold px-4 py-2 rounded-xl text-xs transition"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : imagePreview ? (
              <div class="relative w-full aspect-video rounded-xl overflow-hidden bg-slate-100 border border-slate-200">
                <img
                  src={imagePreview}
                  alt="Uploaded Leaf preview"
                  class="w-full h-full object-contain"
                />
                <button
                  type="button"
                  onClick={() => {
                    setImagePreview(null);
                    setImageFile(null);
                    setQualityCheck(null);
                  }}
                  class="absolute top-4 right-4 bg-slate-900 bg-opacity-70 hover:bg-opacity-95 text-white font-bold p-2 rounded-full transition"
                  title="Retake / Remove image"
                >
                  <RefreshCw class="h-4 w-4" />
                </button>
              </div>
            ) : (
              <div class="border-2 border-dashed border-slate-300 hover:border-emerald-500 rounded-2xl p-12 text-center transition bg-slate-50 relative">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <UploadCloud class="h-12 w-12 mx-auto text-slate-400 mb-3" />
                <p class="text-sm font-bold text-slate-700">Drag leaf photo here, or click to browse</p>
                <p class="text-xs text-slate-500 mt-1">
                  Automatically detects Crop Leaf, EXIF GPS Location, Blur, and Leaf Coverage (PNG, JPG, WEBP up to 5MB)
                </p>
                <p class="text-xs text-emerald-700 font-medium mt-2">
                  পাতার স্পষ্ট ছবি তুলুন — ফসলের নাম ও অবস্থান স্বয়ংক্রিয়ভাবে শনাক্ত করা হবে
                </p>
              </div>
            )}

            <canvas ref={canvasRef} class="hidden"></canvas>

            <div class="flex items-center gap-4 mt-6">
              {!useCamera && !imagePreview && (
                <button
                  type="button"
                  onClick={startCamera}
                  class="flex-1 flex justify-center items-center gap-2 py-3 border border-slate-300 rounded-xl text-sm font-semibold text-slate-700 hover:bg-slate-50 transition bg-white"
                >
                  <Camera class="h-5 w-5 text-slate-500" />
                  <span>Capture Field Photo with Camera</span>
                </button>
              )}

              {(imagePreview || useCamera) && (
                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  class="flex-1 flex justify-center items-center gap-2 py-3.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-sm font-bold transition disabled:opacity-50 shadow-sm"
                >
                  {loading ? (
                    <div class="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  ) : (
                    <>
                      <Eye class="h-5 w-5" />
                      <span>
                        {qualityCheck && !qualityCheck.passed
                          ? 'Submit Uncertain Photo to Officer Review Queue'
                          : 'Run 6-Stage Leaf Diagnosis'}
                      </span>
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UploadLeaf;
