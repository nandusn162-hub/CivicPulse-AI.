import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Clock, CheckCircle2, AlertTriangle, Search, Filter, ChevronRight } from 'lucide-react';
import { fetchMyComplaints, fetchComplaints, type ComplaintData } from '../lib/api';
import { useAuthStore } from '../store/auth';

const statusColors: Record<string, { bg: string; text: string; label: string }> = {
  submitted: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Submitted' },
  under_review: { bg: 'bg-yellow-100', text: 'text-yellow-700', label: 'Under Review' },
  in_progress: { bg: 'bg-orange-100', text: 'text-orange-700', label: 'In Progress' },
  resolved: { bg: 'bg-green-100', text: 'text-green-700', label: 'Resolved' },
  closed: { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Closed' },
  rejected: { bg: 'bg-red-100', text: 'text-red-700', label: 'Rejected' },
};

const priorityColors: Record<string, string> = {
  critical: 'bg-red-500',
  high: 'bg-orange-500',
  medium: 'bg-yellow-500',
  low: 'bg-green-500',
};

export default function TrackComplaintsPage() {
  const [complaints, setComplaints] = useState<ComplaintData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [viewMode, setViewMode] = useState<'my' | 'all'>('my');
  const user = useAuthStore((s) => s.user);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const data = viewMode === 'my' ? await fetchMyComplaints() : await fetchComplaints({ limit: 100 });
        setComplaints(data);
      } catch (e: any) {
        setError(e.message ?? 'Failed to load complaints');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [viewMode]);

  const filtered = complaints.filter((c) => {
    if (filter !== 'all' && c.status !== filter) return false;
    if (search && !c.title.toLowerCase().includes(search.toLowerCase()) && !c.description.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const statusCounts = {
    all: complaints.length,
    submitted: complaints.filter((c) => c.status === 'submitted').length,
    in_progress: complaints.filter((c) => c.status === 'in_progress' || c.status === 'under_review').length,
    resolved: complaints.filter((c) => c.status === 'resolved').length,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-3 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Track Complaints</h1>
          <p className="text-sm text-gray-500">Monitor the status of your civic complaints</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('my')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              viewMode === 'my' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            My Complaints
          </button>
          <button
            onClick={() => setViewMode('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              viewMode === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            All Complaints
          </button>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: 'Total', count: statusCounts.all, icon: Filter, color: 'blue' },
          { label: 'Pending', count: statusCounts.submitted, icon: Clock, color: 'yellow' },
          { label: 'In Progress', count: statusCounts.in_progress, icon: AlertTriangle, color: 'orange' },
          { label: 'Resolved', count: statusCounts.resolved, icon: CheckCircle2, color: 'green' },
        ].map((s) => (
          <div key={s.label} className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">{s.count}</div>
                <div className="text-xs text-gray-500">{s.label}</div>
              </div>
              <s.icon size={20} className={`text-${s.color}-500`} />
            </div>
          </div>
        ))}
      </div>

      {/* Search & Filter */}
      <div className="flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search complaints..."
            className="w-full pl-9 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
        >
          <option value="all">All Status</option>
          <option value="submitted">Submitted</option>
          <option value="under_review">Under Review</option>
          <option value="in_progress">In Progress</option>
          <option value="resolved">Resolved</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      {/* Complaint List */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">{error}</div>
      )}

      {filtered.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <div className="text-gray-400 text-4xl mb-3">📋</div>
          <div className="text-gray-600 font-medium">No complaints found</div>
          <div className="text-gray-400 text-sm mt-1">
            {viewMode === 'my'
              ? 'You have not submitted any complaints yet.'
              : 'No complaints match your filter.'}
          </div>
          <Link
            to="/submit"
            className="inline-block mt-4 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
          >
            Report an Issue
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((c) => {
            const st = statusColors[c.status] ?? statusColors.submitted;
            return (
              <Link
                key={c.id}
                to={`/complaints/${c.id}`}
                className="block bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md hover:border-blue-200 transition-all group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`w-2 h-2 rounded-full ${priorityColors[c.priority] ?? 'bg-gray-400'}`} />
                      <h3 className="text-sm font-semibold text-gray-900 truncate">{c.title}</h3>
                    </div>
                    <p className="text-xs text-gray-500 line-clamp-1 mb-2">{c.description}</p>
                    <div className="flex items-center gap-3 text-xs">
                      <span className={`px-2 py-0.5 rounded-full font-medium ${st.bg} ${st.text}`}>
                        {st.label}
                      </span>
                      <span className="text-gray-400 capitalize">{c.category.replace('_', ' ')}</span>
                      {c.ward && <span className="text-gray-400">📍 {c.ward}</span>}
                      <span className="text-gray-400">
                        {new Date(c.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <ChevronRight size={16} className="text-gray-300 group-hover:text-blue-500 mt-1 transition-colors" />
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
