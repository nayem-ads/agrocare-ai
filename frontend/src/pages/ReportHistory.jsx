import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { History, Eye, Leaf, Calendar, ShieldAlert } from 'lucide-react';
import { api } from '../services/api.js';

function ReportHistory() {
  const [reports, setReports] = useState([]);
  const [filterCrop, setFilterCrop] = useState('All');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const myReports = await api.getMyReports();
        setReports(myReports);
      } catch (err) {
        setError('Failed to retrieve history logs. ' + err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchReports();
  }, []);

  const filteredReports = filterCrop === 'All' 
    ? reports 
    : reports.filter(r => r.crop_name.toLowerCase() === filterCrop.toLowerCase());

  if (loading) {
    return (
      <div class="max-w-7xl mx-auto px-4 py-16 flex justify-center items-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  return (
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Title */}
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-slate-200 pb-5 mb-6 gap-4">
        <div>
          <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900 flex items-center gap-2">
            <History class="h-8 w-8 text-emerald-600" />
            Diagnosis Report History
          </h1>
          <p class="text-sm text-slate-500 mt-1">Review previously submitted crops and historical treatment advices.</p>
        </div>

        {/* Filter controls */}
        <div class="flex items-center gap-2">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Filter Crop:</span>
          <select
            value={filterCrop}
            onChange={(e) => setFilterCrop(e.target.value)}
            class="px-3 py-1.5 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white"
          >
            <option value="All">All Crops</option>
            <option value="Rice">Rice</option>
            <option value="Tomato">Tomato</option>
            <option value="Potato">Potato</option>
            <option value="Mango">Mango</option>
            <option value="Chili">Chili</option>
            <option value="Jute">Jute</option>
            <option value="General">General / Other</option>
          </select>
        </div>
      </div>

      {error && (
        <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-6 text-sm flex items-start gap-2">
          <ShieldAlert class="h-5 w-5 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Grid or Table display */}
      {filteredReports.length === 0 ? (
        <div class="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-500">
          <Leaf class="h-12 w-12 mx-auto text-slate-300 mb-3" />
          <p>No historical records found matching your filter criteria.</p>
          <Link to="/diagnose" class="text-sm text-emerald-600 hover:underline mt-1.5 inline-block">Perform leaf diagnosis now</Link>
        </div>
      ) : (
        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-slate-200 text-left text-sm">
              <thead class="bg-slate-50 text-slate-500 text-xs font-bold uppercase tracking-wider">
                <tr>
                  <th scope="col" class="px-6 py-4">Crop</th>
                  <th scope="col" class="px-6 py-4">Infection / Condition</th>
                  <th scope="col" class="px-6 py-4">Severity</th>
                  <th scope="col" class="px-6 py-4">Confidence</th>
                  <th scope="col" class="px-6 py-4">Date</th>
                  <th scope="col" class="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 text-slate-700">
                {filteredReports.map((report) => (
                  <tr key={report.id} class="hover:bg-slate-50 transition">
                    <td class="px-6 py-4 font-bold text-slate-900">{report.crop_name}</td>
                    <td class="px-6 py-4">
                      <div class="flex items-center gap-2">
                        <span class={`w-2 h-2 rounded-full ${
                          report.disease_type === 'healthy' ? 'bg-green-500' :
                          report.disease_type === 'pest' ? 'bg-purple-500' : 'bg-red-500'
                        }`}></span>
                        <span>{report.disease_name}</span>
                      </div>
                    </td>
                    <td class="px-6 py-4">
                      <span class={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                        report.severity_level === 'High' ? 'bg-red-50 text-red-700' :
                        report.severity_level === 'Medium' ? 'bg-yellow-50 text-yellow-700' :
                        'bg-green-50 text-green-700'
                      }`}>
                        {report.severity_level} ({report.severity_score}%)
                      </span>
                    </td>
                    <td class="px-6 py-4 font-mono text-xs">{Math.round(report.confidence_score * 100)}%</td>
                    <td class="px-6 py-4 text-xs text-slate-500">
                      <div class="flex items-center gap-1.5">
                        <Calendar class="h-3.5 w-3.5 text-slate-400" />
                        <span>{new Date(report.created_at).toLocaleDateString()}</span>
                      </div>
                    </td>
                    <td class="px-6 py-4 text-right">
                      <Link
                        to={`/reports/${report.id}`}
                        class="inline-flex items-center gap-1 text-emerald-600 hover:text-emerald-700 font-bold text-xs transition"
                      >
                        <Eye class="h-4 w-4" />
                        <span>View Report</span>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default ReportHistory;
