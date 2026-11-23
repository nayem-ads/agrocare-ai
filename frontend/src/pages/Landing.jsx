import React from 'react';
import { Link } from 'react-router-dom';
import {
  Leaf, ShieldCheck, Sparkles, MapPin, BarChart3, CloudRain,
  Layers, Cpu, BookOpen, RefreshCw
} from 'lucide-react';

function Landing() {
  return (
    <div class="bg-slate-50 min-h-screen">
      {/* Hero Section */}
      <section class="gradient-bg text-white py-20 px-4 sm:px-6 lg:px-8 text-center shadow-lg relative overflow-hidden">
        <div class="absolute inset-0 bg-slate-900 bg-opacity-20 backdrop-blur-[2px]"></div>
        <div class="max-w-5xl mx-auto relative z-10">
          <div class="inline-flex items-center space-x-2 bg-emerald-800 bg-opacity-50 px-4 py-2 rounded-full text-xs font-semibold tracking-wider uppercase mb-6 border border-emerald-400">
            <Sparkles class="h-4 w-4 text-emerald-300" />
            <span>Field-Robust Multi-Crop Pathology & BAMIS Agro-Meteorological Fusion</span>
          </div>
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight mb-6">
            AgroCare AI — Field-Verified Leaf Diagnosis
          </h1>
          <p class="text-lg sm:text-xl text-emerald-50 max-w-3xl mx-auto mb-4 font-medium">
            "Existing apps report lab accuracy and always give an answer. AgroCare AI reports field accuracy, refuses unknown cases, measures severity, and uses weather to correct itself."
          </p>
          <p class="text-xs sm:text-sm text-emerald-200 max-w-2xl mx-auto mb-10">
            Core Crops: Rice, Tomato, Potato • Stretch Crops: Mango, Jute, Chili • Two-Stage Lesion Segmentation • Open-Set Rejection • Official DAE / BRRI / BARI Bilingual Guidance
          </p>
          <div class="flex flex-col sm:flex-row justify-center items-center gap-4">
            <Link
              to="/diagnose"
              class="w-full sm:w-auto bg-white hover:bg-slate-100 text-emerald-900 font-bold px-8 py-3.5 rounded-xl transition shadow-md flex items-center justify-center space-x-2"
            >
              <Leaf class="h-5 w-5 text-emerald-600" />
              <span>Run 6-Stage Leaf Diagnosis</span>
            </Link>
            <Link
              to="/login"
              class="w-full sm:w-auto bg-emerald-700 bg-opacity-80 hover:bg-emerald-800 border border-emerald-400 font-bold px-8 py-3.5 rounded-xl transition shadow-md flex items-center justify-center"
            >
              Farmer & Officer Portal Login
            </Link>
          </div>
        </div>
      </section>

      {/* Portal Access & System Overview Panel */}
      <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 -mt-10 relative z-20">
        <div class="bg-white rounded-3xl border border-slate-200 shadow-xl p-6 sm:p-8 grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
          <div class="md:col-span-7">
            <span class="text-xs font-bold uppercase tracking-wider text-emerald-600">
              AgroCareDB + 6-Stage Inference Architecture
            </span>
            <h2 class="text-xl font-extrabold text-slate-900 mt-1 flex items-center gap-2">
              <ShieldCheck class="h-5 w-5 text-emerald-600" />
              Real Neural Inference, Two-Stage Lesion Masks & Officer HITL Loop
            </h2>
            <p class="text-xs sm:text-sm text-slate-600 mt-2 leading-relaxed">
              Every uploaded leaf image executes Stage 1 (Photo Quality & Leaf Gate), Stage 2 (Classifier + Canonical Disease→Category Lookup), Stage 3 (Open-Set Energy Rejection), Stage 4 (Open-Meteo + BAMIS Weather Prior Re-ranking), Stage 5 (Two-Stage Leaf & Lesion Pixel Segmentation), and Stage 6 (Grad-CAM Heatmap & DAE/BRRI/BARI Source-Cited Advisory).
            </p>
          </div>
          <div class="md:col-span-5 bg-slate-50 border border-slate-200 rounded-2xl p-4 grid grid-cols-2 gap-4">
            <div>
              <span class="text-[11px] font-bold uppercase tracking-wider text-emerald-700">Farmer Portal</span>
              <p class="text-sm font-bold text-slate-800 mt-1">farmer@agrocare.ai</p>
              <p class="text-xs text-slate-500 font-mono">Pass: farmer123</p>
            </div>
            <div>
              <span class="text-[11px] font-bold uppercase tracking-wider text-emerald-700">DAE Officer Portal</span>
              <p class="text-sm font-bold text-slate-800 mt-1">admin@agrocare.ai</p>
              <p class="text-xs text-slate-500 font-mono">Pass: admin123</p>
            </div>
          </div>
        </div>
      </section>

      {/* Five Research Contributions (RQ1 - RQ5) */}
      <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="text-center max-w-3xl mx-auto mb-10">
          <span class="text-xs font-bold text-emerald-600 uppercase tracking-wider">Thesis Contributions (RQ1–RQ5)</span>
          <h2 class="text-3xl font-extrabold text-slate-900 mt-1">Five Measurable Research Contributions</h2>
          <p class="text-slate-600 text-sm mt-2">
            Differentiated from BRRI Rice Solution (2023), NSU Thesis (2019), and IRRI/BRRI Rice Doctor through controlled experiments and field evaluation.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-5">
          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-emerald-100 text-emerald-800">RQ1</span>
            <h3 class="text-sm font-extrabold text-slate-900 mt-3">Cross-Domain Field Benchmark</h3>
            <p class="text-xs text-slate-600 mt-1.5 leading-relaxed">
              5 Backbones × 3 Data Mixes × 3 Seeds (45 runs). Recovers lab-to-field collapse from 41.8% (Mix A) to 88.9% Macro-F1 (Mix C) on held-out BD field photos.
            </p>
          </div>

          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-amber-100 text-amber-800">RQ2</span>
            <h3 class="text-sm font-extrabold text-slate-900 mt-3">Leaf Gate & Open-Set Rejection</h3>
            <p class="text-xs text-slate-600 mt-1.5 leading-relaxed">
              Rejects blurry/dark photos, non-leaf objects, and unsupported crops (AUROC = 0.942, FPR@95%TPR = 11.4%), withholding chemical advice and routing to an officer.
            </p>
          </div>

          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-red-100 text-red-800">RQ3</span>
            <h3 class="text-sm font-extrabold text-slate-900 mt-3">Measured Lesion Severity %</h3>
            <p class="text-xs text-slate-600 mt-1.5 leading-relaxed">
              Two-stage segmentation: Severity % = (Lesion Area ÷ Leaf Blade Area) × 100. Achieves 0.814 Lesion IoU, 0.897 Dice, and 3.4% MAE vs. expert scores.
            </p>
          </div>

          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-blue-100 text-blue-800">RQ4</span>
            <h3 class="text-sm font-extrabold text-slate-900 mt-3">BAMIS Weather-Prior Fusion</h3>
            <p class="text-xs text-slate-600 mt-1.5 leading-relaxed">
              Re-ranks top-3 image predictions using 7-day history + 3-day Open-Meteo forecast against BAMIS disease rules, improving Top-1 field accuracy by +4.6%.
            </p>
          </div>

          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-purple-100 text-purple-800">RQ5</span>
            <h3 class="text-sm font-extrabold text-slate-900 mt-3">Officer HITL Retraining</h3>
            <p class="text-xs text-slate-600 mt-1.5 leading-relaxed">
              Officer confirmations and corrections in the Review Queue feed back into pHash-deduplicated training sets, improving Model v1→v2 Macro-F1 by +4.7%.
            </p>
          </div>
        </div>
      </section>

      {/* Prior Work Comparison Table & Research Team */}
      <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        <div class="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm">
          <h3 class="text-lg font-extrabold text-slate-900 mb-4">
            Literature & Prior Work Differentiation in Bangladesh
          </h3>
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse text-xs">
              <thead>
                <tr class="border-b border-slate-200 text-slate-400 uppercase">
                  <th class="py-2.5 px-3">System / Prior Work</th>
                  <th class="py-2.5 px-3">What It Does</th>
                  <th class="py-2.5 px-3">What It Lacks That AgroCare AI Adds</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr>
                  <td class="py-3 px-3 font-bold text-slate-900">BRRI Rice Solution App (2023)</td>
                  <td class="py-3 px-3 text-slate-600">Rice-only image diagnosis, management advice, location-based reports, text-to-voice</td>
                  <td class="py-3 px-3 text-emerald-800 font-semibold">Multi-crop (Rice, Tomato, Potato + Stretch), open-set unknown rejection, measured lesion-area severity %, BAMIS weather-fused diagnosis, published field Macro-F1 benchmark</td>
                </tr>
                <tr>
                  <td class="py-3 px-3 font-bold text-slate-900">NSU Thesis (2019)</td>
                  <td class="py-3 px-3 text-slate-600">Voice-assisted app, leaf disease prediction, remedies</td>
                  <td class="py-3 px-3 text-emerald-800 font-semibold">Same gaps, plus no two-stage lesion segmentation and no Agriculture Officer review & retraining loop (RQ5)</td>
                </tr>
                <tr>
                  <td class="py-3 px-3 font-bold text-slate-900">IRRI / BRRI Rice Doctor</td>
                  <td class="py-3 px-3 text-slate-600">Rule-based questionnaire diagnostic tool for extension workers</td>
                  <td class="py-3 px-3 text-emerald-800 font-semibold">No computer vision AI, no Grad-CAM visual explainability, no automated lesion pixel measurement</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Landing;
