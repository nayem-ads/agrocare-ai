import React, { useState } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { LogIn, Mail, Lock, ShieldAlert } from 'lucide-react';
import { api } from '../services/api.js';

function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const isExpired = searchParams.get('expired') === 'true';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await api.login(email, password);
      onLogin(data.user, data.access_token);
      if (data.user.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/farmer');
      }
    } catch (err) {
      setError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div class="min-h-[80vh] flex items-center justify-center bg-slate-50 px-4">
      <div class="max-w-md w-full bg-white border border-slate-200 rounded-2xl shadow-lg p-8">
        <div class="text-center mb-6">
          <div class="inline-flex p-3 bg-emerald-50 text-emerald-600 rounded-xl mb-3">
            <LogIn class="h-6 w-6" />
          </div>
          <h2 class="text-2xl font-bold text-slate-900">Sign in to Portal</h2>
          <p class="text-sm text-slate-500 mt-1">Access diagnostics history and extension reports</p>
        </div>

        {isExpired && (
          <div class="bg-amber-50 border border-amber-200 text-amber-800 px-4 py-3 rounded-xl mb-4 text-sm flex items-start gap-2 animate-pulse">
            <ShieldAlert class="h-5 w-5 flex-shrink-0 mt-0.5 text-amber-600" />
            <span>Your session has expired. Please log in again.</span>
          </div>
        )}

        {error && (
          <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-4 text-sm flex items-start gap-2 animate-shake">
            <ShieldAlert class="h-5 w-5 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}


        <form onSubmit={handleSubmit} class="space-y-5">
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Email Address</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400">
                <Mail class="h-5 w-5" />
              </span>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="farmer@agrocare.ai"
                class="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-xl text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition text-sm"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Password</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400">
                <Lock class="h-5 w-5" />
              </span>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                class="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-xl text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition text-sm"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            class="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-xl text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div class="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              'Login'
            )}
          </button>
        </form>

        <div class="text-center mt-6">
          <p class="text-sm text-slate-500">
            Don't have an account?{' '}
            <Link to="/register" class="text-emerald-600 hover:text-emerald-700 font-semibold transition">
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;
