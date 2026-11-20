import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertCircle,
  Clock,
  CheckCircle2,
  TrendingUp,
  MapPin,
  PlusCircle,
  Filter,
  Eye,
  Sparkles,
  Layers,
  ChevronRight,
  ShieldAlert,
} from 'lucide-react';
import { fetchComplaintStats, fetchMyComplaints, fetchComplaints, ComplaintData, ComplaintStats } from '../lib/api';
import { useAuthStore } from '../store/auth';

export default function DashboardPage() {
  const [stats, setStats] = useState<ComplaintStats | null>(null);
  const [myComplaints, setMyComplaints] = useState<ComplaintData[]>([]);
  const [cityComplaints, setCityComplaints] = useState<ComplaintData[]>([]);
  const [activeTab, setActiveTab] = useState<'my' | 'city'>('my');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { user } = useAuthStore();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, myData, cityData] = await Promise.all([
        fetchComplaintStats().catch(() => ({ total: 0, submitted: 0, in_progress: 0, resolved: 0 })),
        fetchMyComplaints().catch(() => []),
        fetchComplaints({ limit: 30 }).catch(() => []),
      ]);
      setStats(statsData);
      setMyComplaints(myData);
      setCityComplaints(cityData);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'critical':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-rose-100 text-rose-700 border border-rose-200">Critical</span>;
      case 'high':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-700 border border-amber-200">High</span>;
      case 'medium':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-blue-100 text-blue-700 border border-blue-200">Medium</span>;
      default:
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-700 border border-slate-200">Low</span>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'resolved':
        return (
          <span className="flex items-center gap-1 text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full text-xs font-semibold">
            <CheckCircle2 size={12} /> Resolved
          </span>
        );
      case 'in_progress':
        return (
          <span className="flex items-center gap-1 text-sky-700 bg-sky-50 border border-sky-200 px-2.5 py-0.5 rounded-full text-xs font-semibold">
            <Clock size={12} /> In Progress
          </span>
        );
      case 'under_review':
        return (
          <span className="flex items-center gap-1 text-amber-700 bg-amber-50 border border-amber-200 px-2.5 py-0.5 rounded-full text-xs font-semibold">
            <AlertCircle size={12} /> Under Review
          </span>
        );
      case 'rejected':
        return (
          <span className="flex items-center gap-1 text-rose-700 bg-rose-50 border border-rose-200 px-2.5 py-0.5 rounded-full text-xs font-semibold">
            <ShieldAlert size={12} /> Rejected
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 text-slate-700 bg-slate-100 border border-slate-200 px-2.5 py-0.5 rounded-full text-xs font-semibold">
            Submitted
          </span>
        );
    }
  };

  const currentList = activeTab === 'my' ? myComplaints : cityComplaints;
  const filteredList = currentList.filter((item) => {
    if (statusFilter === 'all') return true;
    return item.status.toLowerCase() === statusFilter.toLowerCase();
  });

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-teal-900 rounded-3xl p-6 md:p-8 text-white shadow-xl relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-teal-500/20 text-teal-300 text-xs font-semibold mb-3 border border-teal-500/30">
            <Sparkles size={13} />
            <span>AI Municipal Triage Active</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight">
            Hello, {user?.full_name || 'Citizen'}
          </h2>
          <p className="text-slate-300 text-sm mt-2 leading-relaxed">
            Report civic infrastructure issues in seconds. CivicPulse AI analyzes severity, estimates community impact, and automatically routes grievances to municipal crews.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link
              to="/submit"
              className="flex items-center gap-2 px-4 py-2.5 bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold rounded-xl text-sm transition-all shadow-md shadow-teal-500/30"
            >
              <PlusCircle size={16} />
              <span>Report New Incident</span>
            </Link>
            <Link
              to="/map"
              className="flex items-center gap-2 px-4 py-2.5 bg-slate-800/80 hover:bg-slate-700/80 text-white font-medium rounded-xl text-sm border border-slate-700 transition-all"
            >
              <MapPin size={16} className="text-teal-400" />
              <span>Explore Ward Map</span>
            </Link>
          </div>
        </div>
        <div className="hidden lg:block absolute -right-6 -bottom-6 w-64 h-64 bg-teal-500/10 rounded-full blur-3xl pointer-events-none"></div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>Total Logged</span>
            <Layers size={16} className="text-slate-400" />
          </div>
          <div className="text-2xl md:text-3xl font-extrabold text-slate-900">
            {stats?.total ?? 0}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Across all municipal wards</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between text-amber-700 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>Pending Review</span>
            <AlertCircle size={16} className="text-amber-500" />
          </div>
          <div className="text-2xl md:text-3xl font-extrabold text-amber-600">
            {(stats?.submitted ?? 0) + (stats?.under_review ?? 0)}
          </div>
          <div className="text-[11px] text-amber-600/80 mt-1">Under AI & officer triage</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between text-sky-700 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>In Progress</span>
            <Clock size={16} className="text-sky-500" />
          </div>
          <div className="text-2xl md:text-3xl font-extrabold text-sky-600">
            {stats?.in_progress ?? 0}
          </div>
          <div className="text-[11px] text-sky-600/80 mt-1">Active field work orders</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between text-emerald-700 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>Resolved</span>
            <CheckCircle2 size={16} className="text-emerald-500" />
          </div>
          <div className="text-2xl md:text-3xl font-extrabold text-emerald-600">
            {stats?.resolved ?? 0}
          </div>
          <div className="text-[11px] text-emerald-600/80 mt-1">Civic issues addressed</div>
        </div>
      </div>

      {/* Main Complaints Section */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        {/* Tab & Filter Header */}
        <div className="p-4 md:p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center bg-slate-100 p-1 rounded-xl">
            <button
              onClick={() => setActiveTab('my')}
              className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'my'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              My Submissions ({myComplaints.length})
            </button>
            <button
              onClick={() => setActiveTab('city')}
              className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'city'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Community Activity ({cityComplaints.length})
            </button>
          </div>

          {/* Status Filter */}
          <div className="flex items-center space-x-2">
            <Filter size={15} className="text-slate-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 font-medium text-slate-700 focus:outline-none focus:ring-1 focus:ring-teal-500"
            >
              <option value="all">All Statuses</option>
              <option value="submitted">Submitted</option>
              <option value="under_review">Under Review</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>

        {/* Complaints List / Table */}
        {loading ? (
          <div className="py-16 text-center text-slate-400 text-sm">
            <div className="w-8 h-8 border-3 border-teal-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
            Loading civic issues...
          </div>
        ) : filteredList.length === 0 ? (
          <div className="py-16 text-center text-slate-500">
            <AlertCircle size={36} className="mx-auto text-slate-300 mb-2" />
            <div className="font-semibold text-slate-700">No complaints found</div>
            <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
              {activeTab === 'my'
                ? "You haven't submitted any complaints yet. Report an issue to track its real-time resolution!"
                : 'No complaints match the selected filter criteria.'}
            </p>
            {activeTab === 'my' && (
              <Link
                to="/submit"
                className="inline-flex items-center gap-1.5 mt-4 px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-semibold shadow-xs"
              >
                <PlusCircle size={14} />
                <span>Submit Your First Report</span>
              </Link>
            )}
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {filteredList.map((item) => (
              <div
                key={item.id}
                className="p-4 md:p-5 hover:bg-slate-50/70 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-1.5 max-w-2xl">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs font-mono font-semibold text-slate-400">
                      #{item.id.slice(0, 8)}
                    </span>
                    <span className="px-2 py-0.5 rounded-md text-[11px] font-semibold bg-slate-100 text-slate-700 capitalize">
                      {item.category.replace('_', ' ')}
                    </span>
                    {getPriorityBadge(item.priority)}
                    {getStatusBadge(item.status)}
                  </div>
                  <h3 className="text-base font-bold text-slate-900">{item.title}</h3>
                  <p className="text-xs text-slate-500 line-clamp-1">{item.description}</p>
                  <div className="flex items-center gap-4 text-xs text-slate-400 pt-1">
                    <span className="flex items-center gap-1">
                      <MapPin size={12} className="text-slate-400" />
                      {item.location_address || item.ward || 'Geo-located'}
                    </span>
                    <span>•</span>
                    <span>{new Date(item.created_at).toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <Link
                    to={`/complaints/${item.id}`}
                    className="flex items-center gap-1 px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-colors"
                  >
                    <Eye size={14} />
                    <span>View Diagnostics</span>
                    <ChevronRight size={14} />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
