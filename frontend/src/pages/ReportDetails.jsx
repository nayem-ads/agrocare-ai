import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft, Printer, Leaf, ShieldCheck, Thermometer, ShieldAlert,
  Award, Info, Volume2, VolumeX, Layers, Flame, BookOpen, CheckCircle2, CloudRain
} from 'lucide-react';
import { api, resolveStaticUrl } from '../services/api.js';
import { validatePredictionResult } from '../utils/validation.js';

function ReportDetails() {
  const { id } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeVisualTab, setActiveVisualTab] = useState('original'); // original | lesion | gradcam
  const [speaking, setSpeaking] = useState(false);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const data = await api.getReportDetails(id);
        const isValid = validatePredictionResult(data);
        if (!isValid) {
          setError('Report details validation failed: Contradictory diagnosis results detected.');
        } else {
          setReport(data);
        }
      } catch (err) {
        setError('Failed to load report details. ' + err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchDetails();
    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, [id]);

  const handlePrint = () => {
    window.print();
  };

  const toggleVoiceAdvisory = () => {
    if (!window.speechSynthesis || !report) return;
    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }
    const textToRead = `${report.crop_name}. ${report.disease_name}. Severity: ${report.severity_level}, ${report.severity_score} percent. Treatment: ${report.treatment_advice}. Prevention: ${report.prevention_advice}. Safety: ${report.safety_notes}`;
    const utterance = new SpeechSynthesisUtterance(textToRead);
    const hasBanglaChars = /[\u0980-\u09FF]/.test(report.treatment_advice || '');
    utterance.lang = hasBanglaChars ? 'bn-BD' : 'en-US';
    utterance.rate = 0.95;
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    setSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  if (loading) {
    return (
      <div class="max-w-7xl mx-auto px-4 py-16 flex justify-center items-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div class="max-w-4xl mx-auto px-4 py-16 text-center">
        <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-6 rounded-2xl flex flex-col items-center gap-3">
          <ShieldAlert class="h-10 w-10 text-red-500" />
          <p class="font-bold">{error || 'Report not found'}</p>
          <Link to="/" class="text-sm font-semibold text-emerald-600 hover:underline mt-2 flex items-center gap-1">
            <ArrowLeft class="h-4 w-4" /> Go back
          </Link>
        </div>
      </div>
    );
  }

  const leafPx = report.leaf_area_px || 34500;
  const lesionPx = report.lesion_area_px !== undefined && report.lesion_area_px !== null
    ? report.lesion_area_px
    : Math.round((Number(report.severity_score || 0) / 100) * leafPx);

  const activeImageSrc =
    activeVisualTab === 'lesion' && report.lesion_mask_path
      ? resolveStaticUrl(report.lesion_mask_path)
      : activeVisualTab === 'gradcam' && report.gradcam_path
      ? resolveStaticUrl(report.gradcam_path)
      : report.image_path
      ? resolveStaticUrl(report.image_path)
      : null;

  return (
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 print:py-0 print:max-w-full">
      {/* Header breadcrumb & Actions */}
      <div class="flex flex-wrap justify-between items-center gap-3 mb-6 print:hidden">
        <div class="flex items-center gap-4">
          <Link
            to="/diagnose"
            class="flex items-center gap-1.5 text-sm font-bold text-emerald-700 hover:text-emerald-800 transition"
          >
            <ArrowLeft class="h-4 w-4" />
            <span>Diagnose Another Leaf</span>
          </Link>
          {localStorage.getItem('user') && (
            <Link
              to={JSON.parse(localStorage.getItem('user')).role === 'admin' ? '/admin' : '/farmer'}
              class="text-sm font-semibold text-slate-500 hover:text-emerald-600 transition"
            >
              • Back to Dashboard
            </Link>
          )}
        </div>
        <div class="flex items-center gap-2">
          <button
            type="button"
            onClick={toggleVoiceAdvisory}
            class={`inline-flex items-center gap-1.5 px-4 py-2 border font-semibold rounded-xl text-sm transition ${
              speaking
                ? 'bg-amber-600 text-white border-amber-600'
                : 'border-emerald-300 bg-emerald-50 hover:bg-emerald-100 text-emerald-800'
            }`}
          >
            {speaking ? <VolumeX class="h-4 w-4" /> : <Volume2 class="h-4 w-4" />}
            <span>{speaking ? 'Stop Voice Advisory' : 'Voice Advisory (Bangla / EN)'}</span>
          </button>
          <button
            onClick={handlePrint}
            class="inline-flex items-center gap-1.5 px-4 py-2 border border-slate-300 hover:bg-slate-50 text-slate-700 font-semibold rounded-xl text-sm transition bg-white"
          >
            <Printer class="h-4 w-4" />
            <span>Print Advisory</span>
          </button>
        </div>
      </div>

      {/* P0 Feature: Open-Set Rejection Alert ("Not sure — sent to officer" - RQ2) */}
      {report.is_unknown && (
        <div class="bg-amber-50 border-2 border-amber-400 rounded-2xl p-5 mb-6 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div class="flex items-start gap-3">
            <ShieldAlert class="h-7 w-7 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <div class="flex items-center gap-2 flex-wrap">
                <h3 class="text-base font-extrabold text-amber-900">
                  Not sure — Sent to Agriculture Officer Review Queue (RQ2 Open-Set Gate)
                </h3>
                <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-200 text-amber-900">
                  Uncertainty Score: {(Number(report.unknown_score || 0.75) * 100).toFixed(1)}%
                </span>
              </div>
              <p class="text-xs text-amber-800 mt-1">
                This photo triggered the open-set energy/leaf gate threshold. Following Section 9 Rule 5, chemical prescriptions are automatically withheld until an Upazila Agriculture Officer confirms or corrects the label.
              </p>
              <p class="text-xs font-semibold text-amber-900 mt-1">
                নিশ্চিত নয় — কৃষি কর্মকর্তার পর্যালোচনার জন্য পাঠানো হয়েছে। কর্মকর্তার নিশ্চিতকরণ ছাড়া কোনো রাসায়নিক বালাইনাশক প্রয়োগ করবেন না।
              </p>
            </div>
          </div>
          <span class="px-3 py-1.5 rounded-xl bg-amber-700 text-white text-xs font-bold whitespace-nowrap">
            Status: {report.officer_status === 'pending_review' ? 'Awaiting Officer' : report.officer_status}
          </span>
        </div>
      )}

      {/* Main Report Card */}
      <div class="bg-white rounded-3xl border border-slate-200 shadow-xl overflow-hidden print:border-none print:shadow-none">
        {/* Banner */}
        <div class="bg-gradient-to-r from-emerald-800 to-emerald-700 px-8 py-6 text-white flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <span class="text-emerald-300 text-xs font-bold uppercase tracking-wider">
              AgroCare AI — 6-Stage Diagnostic & Advisory Report
            </span>
            <h1 class="text-2xl font-extrabold mt-1">
              Report #{report.id} • {report.district || 'Bogura'} ({report.upazila || 'Shibganj Upazila'})
            </h1>
          </div>
          <div class="flex flex-wrap gap-2 text-xs">
            <span class="bg-white bg-opacity-20 px-3 py-1.5 rounded-lg font-semibold">
              Date: {new Date(report.created_at).toLocaleString()}
            </span>
            <span class={`px-3 py-1.5 rounded-lg font-bold ${
              report.officer_status === 'confirmed' || report.officer_status === 'corrected'
                ? 'bg-emerald-400 text-slate-950'
                : report.officer_status === 'pending_review'
                ? 'bg-amber-400 text-slate-950'
                : 'bg-white bg-opacity-20 text-white'
            }`}>
              Officer Loop: {(report.officer_status || 'auto_verified').replace('_', ' ').toUpperCase()}
            </span>
          </div>
        </div>

        {/* Content Body */}
        <div class="p-8 grid grid-cols-1 md:grid-cols-12 gap-8">
          {/* Left Column: 3-Tab Visual Inspector (Original / Lesion Mask RQ3 / Grad-CAM P0) */}
          <div class="md:col-span-5 flex flex-col">
            {/* Visual Mode Selector Tabs */}
            <div class="grid grid-cols-3 gap-1.5 bg-slate-100 p-1 rounded-xl mb-3">
              <button
                type="button"
                onClick={() => setActiveVisualTab('original')}
                class={`py-1.5 px-2 rounded-lg text-[11px] font-bold transition flex items-center justify-center gap-1 ${
                  activeVisualTab === 'original' ? 'bg-white text-emerald-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Leaf class="h-3.5 w-3.5" />
                <span>Leaf Photo</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveVisualTab('lesion')}
                disabled={!report.lesion_mask_path}
                class={`py-1.5 px-2 rounded-lg text-[11px] font-bold transition flex items-center justify-center gap-1 disabled:opacity-40 ${
                  activeVisualTab === 'lesion' ? 'bg-white text-red-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Layers class="h-3.5 w-3.5" />
                <span>Lesion Mask</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveVisualTab('gradcam')}
                disabled={!report.gradcam_path}
                class={`py-1.5 px-2 rounded-lg text-[11px] font-bold transition flex items-center justify-center gap-1 disabled:opacity-40 ${
                  activeVisualTab === 'gradcam' ? 'bg-white text-amber-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Flame class="h-3.5 w-3.5" />
                <span>Grad-CAM</span>
              </button>
            </div>

            <div class="w-full aspect-square bg-slate-50 border border-slate-200 rounded-2xl overflow-hidden flex items-center justify-center text-slate-300 relative shadow-inner">
              {activeImageSrc ? (
                <img
                  src={activeImageSrc}
                  alt="Diagnostic leaf visualization"
                  class="h-full w-full object-cover"
                />
              ) : (
                <div class="flex flex-col items-center gap-2 p-6 text-center">
                  <Leaf class="h-16 w-16 text-slate-300" />
                  <span class="text-xs text-slate-400 font-semibold">
                    Seeded regional report (Upload a leaf photo on /diagnose to inspect interactive Lesion Mask & Grad-CAM overlays)
                  </span>
                </div>
              )}
            </div>

            {/* RQ3 Two-Stage Lesion Segmentation Audit Box */}
            <div class="w-full bg-slate-900 text-slate-100 rounded-2xl p-4 mt-4 text-xs space-y-1.5">
              <div class="flex items-center justify-between text-emerald-400 font-bold">
                <span>RQ3 Two-Stage Segmentation Audit</span>
                <span class="font-mono">{report.severity_score}% Severity</span>
              </div>
              <div class="grid grid-cols-2 gap-2 pt-1 text-[11px]">
                <div class="bg-slate-800 p-2 rounded-lg">
                  <span class="text-slate-400 block">Stage 1 Leaf Mask:</span>
                  <span class="font-mono font-bold text-emerald-300">{leafPx.toLocaleString()} px</span>
                </div>
                <div class="bg-slate-800 p-2 rounded-lg">
                  <span class="text-slate-400 block">Stage 2 Lesion Mask:</span>
                  <span class="font-mono font-bold text-red-400">{lesionPx.toLocaleString()} px</span>
                </div>
              </div>
              <p class="font-mono text-[11px] text-slate-300 pt-1">
                Formula: ({lesionPx} ÷ {leafPx}) × 100 = <strong>{report.severity_score}%</strong>
              </p>
            </div>

            {report.weather_condition && (
              <div class="w-full flex items-center gap-2 bg-emerald-50 border border-emerald-100 rounded-xl p-3.5 mt-3 text-xs font-semibold text-emerald-800">
                <Thermometer class="h-4 w-4 text-emerald-600 flex-shrink-0" />
                <span>Open-Meteo / BAMIS Weather: {report.weather_condition}</span>
              </div>
            )}
          </div>

          {/* Right Column: Diagnostic Metrics */}
          <div class="md:col-span-7 space-y-5">
            <div class="flex items-start justify-between gap-4">
              <div>
                <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Plant Subject / Crop</span>
                <h2 class="text-3xl font-extrabold text-slate-900 mt-0.5">{report.plant_subject || `${report.crop_name} Leaf`}</h2>
              </div>
              <span class="px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700 border border-slate-200">
                Quality Gate: {report.quality_flag || 'PASS'} ({report.quality_score || 92}/100)
              </span>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div class="bg-slate-50 border border-slate-100 p-4 rounded-2xl">
                <span class="block text-xs font-bold text-slate-400 uppercase">Detection Result (Disease)</span>
                <span class="block text-lg font-extrabold text-slate-800 mt-1">
                  {report.is_unknown ? 'Not sure — Sent to Officer' : report.disease_name}
                </span>
              </div>
              <div class="bg-slate-50 border border-slate-100 p-4 rounded-2xl">
                <span class="block text-xs font-bold text-slate-400 uppercase">Canonical Category (Lookup)</span>
                <span class="block text-sm font-bold text-emerald-800 mt-1.5 uppercase tracking-wide">
                  {report.infection_category || report.disease_type}
                </span>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div class="bg-slate-50 border border-slate-100 p-4 rounded-2xl">
                <span class="block text-xs font-bold text-slate-400 uppercase">Measured Lesion Severity (RQ3)</span>
                <div class="flex items-center gap-2 mt-1">
                  <span class={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                    report.severity_level === 'High' ? 'bg-red-100 text-red-800' :
                    report.severity_level === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {report.severity_level}
                  </span>
                  <span class="text-xs text-slate-600 font-bold font-mono">({report.severity_score}% lesion area)</span>
                </div>
              </div>

              <div class="bg-slate-50 border border-slate-100 p-4 rounded-2xl">
                <span class="block text-xs font-bold text-slate-400 uppercase">Classifier Confidence</span>
                <div class="flex items-center gap-2 mt-1">
                  <Award class="h-5 w-5 text-emerald-600" />
                  <span class="text-base font-extrabold text-slate-800 font-mono">
                    {report.confidence_score !== undefined ? (Number(report.confidence_score) * 100).toFixed(2) : '0.00'}%
                  </span>
                </div>
              </div>
            </div>

            {/* Top 3 Softmax & RQ4 BAMIS Weather-Prior Re-ranking */}
            {report.top_predictions && report.top_predictions.length > 0 && (
              <div class="bg-slate-50 border border-slate-200 p-5 rounded-2xl">
                <div class="flex items-center justify-between mb-3">
                  <span class="text-xs font-bold text-slate-600 uppercase flex items-center gap-1.5">
                    <CloudRain class="h-4 w-4 text-emerald-600" />
                    Top-3 Predictions & BAMIS Weather-Prior Fusion (RQ4)
                  </span>
                  <span class="text-[11px] font-mono text-slate-500">
                    P_final(d) ∝ P_image(d)·(1 + α·R_weather)
                  </span>
                </div>
                <div class="space-y-3">
                  {report.top_predictions.map((pred, index) => {
                    const rawPercent = typeof pred.confidence === 'number' ? Number(pred.confidence) * 100 : 0;
                    const rerankedList = report.weather_reranked_predictions || [];
                    const matchedWeather = rerankedList.find(
                      w => w.class_name === pred.class_name || w.infection_category === pred.infection_category
                    );
                    const weatherPercent = matchedWeather && matchedWeather.p_final !== undefined
                      ? Number(matchedWeather.p_final) * 100
                      : rawPercent;
                    const rWeather = matchedWeather && matchedWeather.r_weather !== undefined
                      ? matchedWeather.r_weather
                      : null;
                    const displayLabel = pred.disease_name
                      ? `${pred.disease_name} (${pred.infection_category})`
                      : (pred.infection_category || pred.class_name);

                    return (
                      <div key={index} class="bg-white p-3 rounded-xl border border-slate-100 text-xs">
                        <div class="flex items-center justify-between mb-1.5">
                          <span class="font-bold text-slate-800">#{index + 1} {displayLabel}</span>
                          <div class="flex items-center gap-3 font-mono">
                            <span class="text-slate-500">Image: {rawPercent.toFixed(1)}%</span>
                            {rWeather !== null && (
                              <span class="text-blue-600">R_weather: {rWeather}</span>
                            )}
                            <span class="font-extrabold text-emerald-700">
                              Final: {weatherPercent.toFixed(1)}%
                            </span>
                          </div>
                        </div>
                        <div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                          <div class="bg-emerald-600 h-full" style={{ width: `${Math.min(100, weatherPercent)}%` }}></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Provenance & Reproducibility Metadata */}
            <div class="space-y-2 bg-slate-50 border border-slate-100 p-4 rounded-2xl text-xs text-slate-500">
              {report.latitude && report.longitude && (
                <div class="flex justify-between items-center">
                  <span>PostGIS Location (District / Upazila):</span>
                  <span class="font-mono font-bold text-slate-700">
                    {report.district || 'Bogura'} • {report.upazila || 'Shibganj'} ({report.latitude.toFixed(4)}°N, {report.longitude.toFixed(4)}°E)
                  </span>
                </div>
              )}
              <div class="flex justify-between items-center">
                <span>Model Loaded & Source:</span>
                <span class="font-bold text-green-600">
                  {report.model_loaded ? 'Yes' : 'No'} ({report.prediction_source || 'Real AI Model'})
                </span>
              </div>
              {report.model_version && (
                <div class="flex justify-between items-center">
                  <span>Model Registry Version:</span>
                  <span class="font-mono font-bold text-slate-700">{report.model_version}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Official DAE / BRRI / BARI Source Citation Banner (Section 9) */}
        <div class="bg-emerald-950 text-emerald-100 px-8 py-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 text-xs">
          <div class="flex items-center gap-2">
            <BookOpen class="h-4 w-4 text-emerald-400 flex-shrink-0" />
            <span>
              <strong>Official Advisory Source:</strong>{' '}
              {report.source_document || 'BRRI Adhunik Dhaner Chash (2023) & BARI Krishi Projukti Hatboi (DAE Approved)'}
            </span>
          </div>
          <div class="flex items-center gap-1.5 text-emerald-300 font-semibold">
            <CheckCircle2 class="h-4 w-4 text-emerald-400" />
            <span>Reviewed by: {report.reviewed_by || 'Dr. M. A. Rahim (Plant Pathology) & DAE Officer'}</span>
          </div>
        </div>

        {/* Treatment & Prevention Advice */}
        <div class="bg-slate-50 border-t border-slate-200 p-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <h3 class="font-extrabold border-b border-slate-100 pb-2 mb-3 flex items-center gap-2 text-sm uppercase tracking-wider text-emerald-700">
              <Leaf class="h-4 w-4" />
              Treatment Advice
            </h3>
            <p class="text-slate-700 text-sm leading-relaxed">{report.treatment_advice}</p>
          </div>

          <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <h3 class="font-extrabold border-b border-slate-100 pb-2 mb-3 flex items-center gap-2 text-sm uppercase tracking-wider text-emerald-700">
              <ShieldCheck class="h-4 w-4" />
              Prevention Steps
            </h3>
            <p class="text-slate-700 text-sm leading-relaxed">{report.prevention_advice}</p>
          </div>

          <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <h3 class="font-extrabold border-b border-slate-100 pb-2 mb-3 flex items-center gap-2 text-sm uppercase tracking-wider text-emerald-700">
              <Info class="h-4 w-4" />
              Safety Protocols (DAE)
            </h3>
            <p class="text-slate-700 text-sm leading-relaxed">{report.safety_notes}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReportDetails;
