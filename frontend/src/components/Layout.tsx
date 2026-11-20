import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  PenSquare,
  ClipboardList,
  MapPin,
  Map,
  BarChart3,
  Bell,
  User,
  LogOut,
  Menu,
  X,
  Sparkles,
} from 'lucide-react';
import { useAuthStore } from '../store/auth';
import { fetchComplaintStats } from '../lib/api';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [impactScore, setImpactScore] = useState<number | null>(null);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, clear } = useAuthStore();

  const handleLogout = () => {
    clear();
    navigate('/login');
  };

  useEffect(() => {
    // Compute a simple community impact score from stats
    fetchComplaintStats()
      .then((stats) => {
        const total = stats.total || 1;
        const resolved = stats.resolved || 0;
        const score = Math.round((resolved / total) * 100);
        setImpactScore(Math.min(Math.max(score, 5), 99));
      })
      .catch(() => setImpactScore(null));
  }, [location.pathname]);

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Submit Complaint', path: '/submit', icon: PenSquare },
    { name: 'Track Complaints', path: '/complaints', icon: ClipboardList },
    { name: 'Civic Map', path: '/map', icon: MapPin },
    { name: 'Ward Explorer', path: '/ward-map', icon: Map },
    { name: 'Impact Score', path: '/admin', icon: BarChart3 },
    { name: 'Notifications', path: '/departments', icon: Bell, badge: 2 },
  ];

  const userInitials = user?.full_name
    ? user.full_name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : 'U';

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row">
      {/* Mobile Topbar */}
      <div className="md:hidden bg-[#1a2744] text-white flex items-center justify-between px-4 py-3 sticky top-0 z-50 shadow-lg">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 rounded-lg hover:bg-white/10 transition-colors"
        >
          {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Bell size={18} className="text-gray-300" />
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-[10px] font-bold flex items-center justify-center">
              2
            </span>
          </div>
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-xs font-bold">
            {userInitials}
          </div>
        </div>
      </div>

      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0 transition-transform duration-200 fixed md:static inset-y-0 left-0 z-40 w-56 bg-[#1a2744] text-white flex flex-col justify-between shadow-xl md:shadow-none`}
      >
        <div>
          {/* Logo / Brand */}
          <div className="px-5 pt-5 pb-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-lg bg-blue-500 flex items-center justify-center">
                <MapPin size={16} className="text-white" />
              </div>
              <div>
                <div className="font-bold text-sm text-white leading-none">CivicPulse AI</div>
                <div className="text-[10px] text-blue-300 mt-0.5">
                  Smarter Cities. Stronger Communities.
                </div>
              </div>
            </div>
          </div>

          {/* Nav Items */}
          <nav className="px-3 space-y-0.5 mt-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path || 
                (item.path === '/complaints' && location.pathname.startsWith('/complaints'));
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'text-gray-300 hover:bg-white/8 hover:text-white'
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon size={16} className={isActive ? 'text-white' : 'text-gray-400'} />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <span className="w-5 h-5 bg-red-500 rounded-full text-[10px] font-bold flex items-center justify-center">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Separator */}
          <div className="mx-5 my-4 border-t border-white/10" />

          {/* Profile & Logout */}
          <div className="px-3 space-y-0.5">
            <Link
              to="/dashboard"
              onClick={() => setSidebarOpen(false)}
              className="flex items-center space-x-2.5 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-300 hover:bg-white/8 hover:text-white transition-all"
            >
              <User size={16} className="text-gray-400" />
              <span>Profile</span>
            </Link>
            <button
              onClick={handleLogout}
              className="w-full flex items-center space-x-2.5 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-300 hover:bg-white/8 hover:text-white transition-all text-left"
            >
              <LogOut size={16} className="text-gray-400" />
              <span>Logout</span>
            </button>
          </div>
        </div>

        {/* Community Impact Score Widget */}
        <div className="p-4">
          <div className="bg-gradient-to-br from-blue-600/30 to-blue-900/40 rounded-xl p-4 border border-blue-500/20">
            <div className="text-xs font-semibold text-blue-200 mb-3">Community Impact Score</div>
            <div className="flex items-center justify-center">
              <div className="relative w-20 h-20">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                  <circle
                    cx="18"
                    cy="18"
                    r="15.5"
                    fill="none"
                    stroke="rgba(255,255,255,0.1)"
                    strokeWidth="3"
                  />
                  <circle
                    cx="18"
                    cy="18"
                    r="15.5"
                    fill="none"
                    stroke="#3b82f6"
                    strokeWidth="3"
                    strokeDasharray={`${((impactScore ?? 50) / 100) * 97.4} 97.4`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-xl font-extrabold text-white">{impactScore ?? '—'}%</span>
                </div>
              </div>
            </div>
            <div className="text-center mt-2">
              <div className="text-[10px] text-green-300 flex items-center justify-center gap-1">
                <Sparkles size={10} />
                {(impactScore ?? 50) >= 50 ? 'A cleaner, greener city!' : 'Help improve your area!'}
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-30 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Bar (desktop) */}
        <header className="hidden md:flex items-center justify-between px-6 py-3 bg-white border-b border-gray-200 sticky top-0 z-30">
          <div className="flex items-center space-x-3">
            <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
              <Menu size={18} className="text-gray-500" />
            </button>
          </div>
          <div className="flex items-center space-x-4">
            <div className="relative cursor-pointer">
              <Bell size={18} className="text-gray-500" />
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-[9px] font-bold flex items-center justify-center text-white">
                2
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold border border-blue-200">
                {userInitials}
              </div>
              <span className="text-sm font-medium text-gray-700">{user?.full_name || 'User'}</span>
            </div>
          </div>
        </header>

        <main className="flex-1 p-4 md:p-6 max-w-7xl w-full mx-auto">{children}</main>
      </div>
    </div>
  );
}
