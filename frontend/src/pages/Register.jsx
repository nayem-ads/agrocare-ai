import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { UserPlus, User, Mail, Lock, ShieldAlert } from 'lucide-react';
import { api } from '../services/api.js';

function Register({ onLogin }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('farmer');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      // Register
      await api.register(name, email, password, role);
      // Automatically log in after registration
      const loginData = await api.login(email, password);
      onLogin(loginData.user, loginData.access_token);
      if (loginData.user.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/farmer');
      }
    } catch (err) {
      setError(err.message || 'Registration failed. Check details and retry.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div class="min-h-[80vh] flex items-center justify-center bg-slate-50 px-4 py-8">
      <div class="max-w-md w-full bg-white border border-slate-200 rounded-2xl shadow-lg p-8">
        <div class="text-center mb-6">
          <div class="inline-flex p-3 bg-emerald-50 text-emerald-600 rounded-xl mb-3">
            <UserPlus class="h-6 w-6" />
          </div>
          <h2 class="text-2xl font-bold text-slate-900">Create an Account</h2>
          <p class="text-sm text-slate-500 mt-1">Register as a Farmer or Extension Officer</p>
        </div>

        {error && (
          <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-4 text-sm flex items-start gap-2">
            <ShieldAlert class="h-5 w-5 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} class="space-y-5">
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Full Name</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400">
                <User class="h-5 w-5" />
              </span>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="John Doe"
                class="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-xl text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition text-sm"
              />
            </div>
          </div>

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

          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Register As</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              class="block w-full px-3 py-2.5 border border-slate-300 rounded-xl text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition text-sm bg-white"
            >
              <option value="farmer">Farmer (Access Leaf Diagnostics & History)</option>
              <option value="admin">Agriculture Officer (Dashboard & Regional Analytics)</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            class="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-xl text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div class="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        <div class="text-center mt-6">
          <p class="text-sm text-slate-500">
            Already have an account?{' '}
            <Link to="/login" class="text-emerald-600 hover:text-emerald-700 font-semibold transition">
              Login here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Register;
