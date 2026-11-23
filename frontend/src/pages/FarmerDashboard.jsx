import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { UploadCloud, History, CloudSun, AlertTriangle, ChevronRight, Leaf, ShieldAlert } from 'lucide-react';
import { api } from '../services/api.js';

function FarmerDashboard() {
  const [reports, setReports] = useState([]);
  const [weatherAlerts, setWeatherAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const myReports = await api.getMyReports();
        setReports(myReports);
        
        // Fetch weather alerts (using admin weather risk to show local district warning)
        const risks = await api.getWeatherRisk();
        // Just take the first few risks matching Dhaka / Rajshahi
        setWeatherAlerts(risks.filter(r => r.risk_level === 'High' || r.risk_level === 'Medium').slice(0, 3));
      } catch (err) {
        setError('Failed to fetch dashboard summaries. ' + err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div class="max-w-7xl mx-auto px-4 py-16 flex justify-center items-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  return (
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome Banner */}
      <div class="bg-gradient-to-r from-emerald-600 to-green-500 rounded-2xl p-6 sm:p-8 text-white shadow-md mb-8">
        <h1 class="text-2xl sm:text-3xl font-extrabold">Welcome back, Farmer!</h1>
        <p class="text-emerald-50 mt-1">Check weather risk alerts or capture a leaf photo to diagnose plant health problems immediately.</p>
        <div class="mt-6 flex flex-wrap gap-4">
          <Link
            to="/diagnose"
            class="bg-white hover:bg-emerald-50 text-emerald-800 font-bold px-6 py-2.5 rounded-xl transition shadow flex items-center gap-2 text-sm"
          >
            <UploadCloud class="h-4 w-4 text-emerald-600" />
            <span>Diagnose New Leaf</span>
          </Link>
          <Link
            to="/history"
            class="bg-emerald-700 bg-opacity-40 hover:bg-opacity-65 text-white border border-emerald-400 font-bold px-6 py-2.5 rounded-xl transition text-sm"
          >
            History Log
          </Link>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Columns - Quick Action / Info Cards */}
        <div class="lg:col-span-2 space-y-8">
          {/* Summary Metric Cards */}
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
              <div class="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
                <Leaf class="h-6 w-6" />
              </div>
              <div>
                <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Diagnostic Runs</span>
                <p class="text-2xl font-bold text-slate-800 mt-0.5">{reports.length}</p>
              </div>
            </div>
            
            <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
              <div class="p-3 bg-yellow-50 text-yellow-600 rounded-xl">
                <AlertTriangle class="h-6 w-6" />
              </div>
              <div>
                <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Active Infection Alerts</span>
                <p class="text-2xl font-bold text-slate-800 mt-0.5">
                  {reports.filter(r => r.severity_level === 'High').length} High Cases
                </p>
              </div>
            </div>
          </div>

          {/* Recent Diagnosis History */}
          <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
            <div class="p-6 border-b border-slate-200 flex justify-between items-center">
              <h2 class="text-lg font-bold text-slate-900">Recent Leaf Diagnoses</h2>
              <Link to="/history" class="text-sm font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-1 transition">
                <span>View all</span>
                <ChevronRight class="h-4 w-4" />
              </Link>
            </div>
            
            {reports.length === 0 ? (
              <div class="p-12 text-center text-slate-500">
                <UploadCloud class="h-12 w-12 mx-auto text-slate-300 mb-3" />
                <p>No leaf diagnostics performed yet.</p>
                <Link to="/diagnose" class="text-sm text-emerald-600 hover:underline mt-1 inline-block">Diagnose your first leaf image now</Link>
              </div>
            ) : (
              <ul class="divide-y divide-slate-100">
                {reports.slice(0, 3).map((report) => (
                  <li key={report.id}>
                    <Link to={`/reports/${report.id}`} class="p-6 hover:bg-slate-50 flex items-center justify-between transition group">
                      <div class="flex items-center gap-4">
                        <div class="h-12 w-12 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600 font-bold overflow-hidden">
                          {report.image_path ? (
                            <img src={`/${report.image_path}`} alt="leaf" class="h-full w-full object-cover" />
                          ) : (
                            <Leaf class="h-6 w-6" />
                          )}
                        </div>
                        <div>
                          <p class="text-sm font-bold text-slate-900 group-hover:text-emerald-600 transition">
                            {report.crop_name} - {report.disease_name}
                          </p>
                          <p class="text-xs text-slate-400 mt-1">
                            Diagnosed on {new Date(report.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div class="flex items-center gap-3">
                        <span class={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                          report.severity_level === 'High' ? 'bg-red-50 text-red-700' :
                          report.severity_level === 'Medium' ? 'bg-yellow-50 text-yellow-700' :
                          'bg-green-50 text-green-700'
                        }`}>
                          {report.severity_level}
                        </span>
                        <ChevronRight class="h-5 w-5 text-slate-300 group-hover:text-slate-400 transition" />
                      </div>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Right Column - Weather & Regional Crop Risk */}
        <div class="space-y-8">
          <div class="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
            <h2 class="text-lg font-bold text-slate-900 flex items-center gap-2 mb-4">
              <CloudSun class="h-5 w-5 text-emerald-600" />
              Regional Weather Risks
            </h2>
            <p class="text-xs text-slate-500 mb-6">
              Agricultural disease vectors calculated dynamically based on current weather (humidity & rainfall) across Bangladesh districts.
            </p>
            
            {weatherAlerts.length === 0 ? (
              <p class="text-sm text-slate-500">No active disease outbreaks predicted for local regions.</p>
            ) : (
              <div class="space-y-4">
                {weatherAlerts.map((alert, idx) => (
                  <div key={idx} class="p-4 rounded-xl border border-slate-100 bg-slate-50 hover:border-emerald-500 transition">
                    <div class="flex justify-between items-start">
                      <div>
                        <span class="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                          {alert.district}
                        </span>
                        <h4 class="text-sm font-bold text-slate-800 mt-1">{alert.crop} Crops</h4>
                      </div>
                      <span class={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        alert.risk_level === 'High' ? 'bg-red-50 text-red-600' : 'bg-yellow-50 text-yellow-600'
                      }`}>
                        {alert.risk_level} Risk
                      </span>
                    </div>
                    <p class="text-xs text-slate-600 mt-2 font-sans leading-relaxed">{alert.reason}</p>
                    <div class="flex items-center gap-3 mt-3 text-[10px] text-slate-400 font-semibold">
                      <span>Temp: {alert.temperature}°C</span>
                      <span>•</span>
                      <span>Humidity: {alert.humidity}%</span>
                      <span>•</span>
                      <span>{alert.condition}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default FarmerDashboard;
