import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { Leaf, LogIn, UserPlus, LogOut, LayoutDashboard, History, UploadCloud, User } from 'lucide-react';

import Landing from './pages/Landing.jsx';
import Login from './pages/Login.jsx';
import Register from './pages/Register.jsx';
import FarmerDashboard from './pages/FarmerDashboard.jsx';
import UploadLeaf from './pages/UploadLeaf.jsx';
import ReportHistory from './pages/ReportHistory.jsx';
import ReportDetails from './pages/ReportDetails.jsx';
import AdminDashboard from './pages/AdminDashboard.jsx';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div class="max-w-md mx-auto my-12 p-6 bg-red-50 border border-red-200 rounded-2xl text-center shadow-sm">
          <h2 class="text-xl font-bold text-red-700 mb-2">Something went wrong</h2>
          <p class="text-slate-600 text-sm mb-4">
            Something went wrong on the Diagnose page.
          </p>
          <button
            onClick={() => window.location.reload()}
            class="bg-red-600 hover:bg-red-700 text-white font-bold px-4 py-2 rounded-xl text-xs transition"
          >
            Reload Page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

function App() {

  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load session user
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (e) {
        localStorage.clear();
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData, token) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.clear();
    setUser(null);
  };

  if (loading) {
    return (
      <div class="min-h-screen bg-slate-50 flex items-center justify-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      {/* Top Navbar */}
      <header class="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between h-16 items-center">
            {/* Logo */}
            <div class="flex items-center space-x-2">
              <Link to="/" class="flex items-center space-x-2">
                <div class="p-2 bg-emerald-500 rounded-lg text-white">
                  <Leaf class="h-6 w-6" />
                </div>
                <span class="text-xl font-bold tracking-tight text-slate-900 font-sans">
                  AgroCare <span class="text-emerald-600">AI</span>
                </span>
              </Link>
            </div>

            {/* Navigation links */}
            <nav class="hidden md:flex space-x-6 items-center">
              <Link to="/" class="text-slate-600 hover:text-emerald-600 font-medium text-sm transition">
                Home
              </Link>
              <Link to="/diagnose" class="flex items-center space-x-1 text-slate-600 hover:text-emerald-600 font-medium text-sm transition">
                <UploadCloud class="h-4 w-4" />
                <span>Diagnose Leaf</span>
              </Link>
              
              {user && user.role === 'farmer' && (
                <>
                  <Link to="/farmer" class="flex items-center space-x-1 text-slate-600 hover:text-emerald-600 font-medium text-sm transition">
                    <LayoutDashboard class="h-4 w-4" />
                    <span>Dashboard</span>
                  </Link>
                  <Link to="/history" class="flex items-center space-x-1 text-slate-600 hover:text-emerald-600 font-medium text-sm transition">
                    <History class="h-4 w-4" />
                    <span>Report History</span>
                  </Link>
                </>
              )}

              {user && user.role === 'admin' && (
                <Link to="/admin" class="flex items-center space-x-1 text-slate-600 hover:text-emerald-600 font-medium text-sm transition">
                  <LayoutDashboard class="h-4 w-4" />
                  <span>Admin Panel</span>
                </Link>
              )}
            </nav>

            {/* Profile / Auth Buttons */}
            <div class="flex items-center space-x-4">
              {user ? (
                <div class="flex items-center space-x-4">
                  <div class="flex items-center space-x-2 bg-slate-100 px-3 py-1.5 rounded-full">
                    <User class="h-4 w-4 text-slate-500" />
                    <span class="text-xs font-semibold text-slate-700">{user.name} ({user.role.toUpperCase()})</span>
                  </div>
                  <button
                    onClick={handleLogout}
                    class="flex items-center space-x-1 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 px-3 py-1.5 rounded-lg text-sm font-medium transition"
                  >
                    <LogOut class="h-4 w-4" />
                    <span class="hidden sm:inline">Logout</span>
                  </button>
                </div>
              ) : (
                <div class="flex items-center space-x-2">
                  <Link
                    to="/login"
                    class="flex items-center space-x-1 text-slate-700 hover:text-emerald-600 px-3 py-2 rounded-lg text-sm font-medium transition"
                  >
                    <LogIn class="h-4 w-4" />
                    <span>Login</span>
                  </Link>
                  <Link
                    to="/register"
                    class="flex items-center space-x-1 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition shadow-sm"
                  >
                    <UserPlus class="h-4 w-4" />
                    <span>Register</span>
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main class="flex-grow">
        <Routes>
          <Route path="/" element={<Landing />} />
          
          <Route
            path="/login"
            element={!user ? <Login onLogin={handleLogin} /> : <Navigate to={user.role === 'admin' ? '/admin' : '/farmer'} />}
          />
          <Route
            path="/register"
            element={!user ? <Register onLogin={handleLogin} /> : <Navigate to={user.role === 'admin' ? '/admin' : '/farmer'} />}
          />

          {/* Farmer Routes */}
          <Route
            path="/farmer"
            element={user && user.role === 'farmer' ? <FarmerDashboard /> : <Navigate to="/login" />}
          />
          <Route
            path="/diagnose"
            element={
              <ErrorBoundary>
                <UploadLeaf />
              </ErrorBoundary>
            }
          />

          <Route
            path="/history"
            element={user && user.role === 'farmer' ? <ReportHistory /> : <Navigate to="/login" />}
          />
          <Route
            path="/reports/:id"
            element={<ReportDetails />}
          />

          {/* Admin Routes */}
          <Route
            path="/admin"
            element={user && user.role === 'admin' ? <AdminDashboard /> : <Navigate to="/login" />}
          />

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer class="bg-white border-t border-slate-200 py-6">
        <div class="max-w-7xl mx-auto px-4 text-center text-slate-500 text-sm">
          <p>© {new Date().getFullYear()} AgroCare AI. All Rights Reserved. Built for Crop Leaf Diagnostic Precision & Smart Agriculture.</p>
        </div>
      </footer>
    </BrowserRouter>
  );
}

export default App;
