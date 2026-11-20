import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldCheck,
  AlertTriangle,
  Clock,
  CheckCircle2,
  TrendingUp,
  BarChart3,
  Filter,
  Eye,
  RefreshCw,
  Search,
  Building2,
  ChevronRight,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { fetchComplaintStats, fetchComplaints, updateComplaint, ComplaintData, ComplaintStats } from '../lib/api';

const COLORS = ['#0d9488', '#0284c7', '#f59e0b', '#10b981', '#f43f5e', '#8b5cf6'];

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<ComplaintStats | null>(null);
  const [complaints, setComplaints] = useState<ComplaintData[]>([]);
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    setLoading(true);
    try {
      const [sData, cData] = await Promise.all([
        fetchComplaintStats().catch(() => ({ total: 0, submitted: 0, in_progress: 0, resolved: 0 })),
        fetchComplaints({ limit: 100 }).catch(() => []),
      ]);
      setStats(sData);
      setComplaints(cData);
    } catch (err) {
      console.error('Error fetching admin data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickStatusChange = async (id: string, newStatus: string) => {
    try {
      await updateComplaint(id, { status: newStatus });
      setComplaints((prev) =>
        prev.map((c) => (c.id === id ? { ...c, status: newStatus as any } : c))
      );
    } catch (err) {
      alert('Failed to update status');
    }
  };

  // Compute category chart data
  const categoryCounts: Record<string, number> = {};
  complaints.forEach((c) => {
    const cat = c.category.replace('_', ' ');
    categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
  });
  const categoryChartData = Object.entries(categoryCounts).map(([name, count]) => ({
    name,
    count,
  }));

  // Compute status chart data
  const statusChartData = [
    { name: 'Submitted', value: stats?.submitted || 0, color: '#94a3b8' },
    { name: 'In Progress', value: stats?.in_progress || 0, color: '#0284c7' },
    { name: 'Resolved', value: stats?.resolved || 0, color: '#10b981' },
    { name: 'Under Review', value: stats?.under_review || 0, color: '#f59e0b' },
  ].filter((d) => d.value > 0);

  // Filter complaints table
  const filtered = complaints.filter((c) => {
    if (priorityFilter !== 'all' && c.priority !== priorityFilter) return false;
    if (statusFilter !== 'all' && c.status !== statusFilter) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const match =
        c.title.toLowerCase().includes(q) ||
        c.description.toLowerCase().includes(q) ||
        c.category.toLowerCase().includes(q) ||
        (c.ward && c.ward.toLowerCase().includes(q));
      if (!match) return false;
    }
    return true;
  });

  // Priority queue: High or Critical that are not yet resolved
  const priorityQueue = complaints.filter(
    (c) =>
      (c.priority === 'critical' || c.priority === 'high') &&
      c.status !== 'resolved' &&
      c.status !== 'closed'
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <ShieldCheck size={24} className="text-teal-600" />
            <span>Municipal Admin Cockpit</span>
          </h1>
          <p className="text-xs text-slate-500">
            Real-time urban governance, SLA monitoring, and automated department triage dispatch.
          </p>
        </div>
        <button
          onClick={loadAdminData}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50 shadow-2xs"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          <span>Refresh Feed</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">
            Total Inflow
          </div>
          <div className="text-3xl font-black text-slate-900">{stats?.total ?? 0}</div>
          <div className="text-[11px] text-teal-600 font-semibold mt-1">Logged Incidents</div>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="text-xs font-bold uppercase tracking-wider text-rose-500 mb-1">
            Critical Priority Queue
          </div>
          <div className="text-3xl font-black text-rose-600">{priorityQueue.length}</div>
          <div className="text-[11px] text-rose-600/80 font-semibold mt-1">Immediate Dispatch Required</div>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="text-xs font-bold uppercase tracking-wider text-sky-500 mb-1">
            Active Work Orders
          </div>
          <div className="text-3xl font-black text-sky-600">{stats?.in_progress ?? 0}</div>
          <div className="text-[11px] text-sky-600/80 font-semibold mt-1">Field Crews Deployed</div>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="text-xs font-bold uppercase tracking-wider text-emerald-500 mb-1">
            Resolution Rate
          </div>
          <div className="text-3xl font-black text-emerald-600">
            {stats?.total ? Math.round(((stats.resolved || 0) / stats.total) * 100) : 0}%
          </div>
          <div className="text-[11px] text-emerald-600/80 font-semibold mt-1">
            {stats?.resolved ?? 0} Completed
          </div>
        </div>
      </div>

      {/* Analytics Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Issues by Category Bar Chart */}
        <div className="lg:col-span-2 bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Grievance Volume by Category
            </h3>
            <span className="text-[11px] text-slate-400">Live Municipal Aggregate</span>
          </div>
          <div className="h-60 w-full">
            {categoryChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryChartData}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#0d9488" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-xs">
                No categorical data available yet
              </div>
            )}
          </div>
        </div>

        {/* Status Distribution Pie Chart */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Resolution Pipeline
            </h3>
          </div>
          <div className="h-60 w-full flex items-center justify-center">
            {statusChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {statusChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-slate-400 text-xs">No active pipeline status</div>
            )}
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            {statusChartData.map((d) => (
              <div key={d.name} className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: d.color }}></span>
                <span className="text-slate-600">{d.name}:</span>
                <span className="font-bold text-slate-900">{d.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Critical Priority Queue */}
      {priorityQueue.length > 0 && (
        <div className="bg-rose-50/60 border border-rose-200/80 rounded-2xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-rose-800 flex items-center gap-1.5">
              <AlertTriangle size={15} className="text-rose-600" />
              <span>Priority Redressal Queue ({priorityQueue.length})</span>
            </h3>
            <span className="text-xs text-rose-700 font-semibold">SLA at Risk</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {priorityQueue.slice(0, 4).map((c) => (
              <div
                key={c.id}
                className="bg-white p-4 rounded-xl border border-rose-200/80 shadow-xs flex items-center justify-between gap-3"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-700">
                      {c.priority.toUpperCase()}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">#{c.id.slice(0, 8)}</span>
                  </div>
                  <div className="text-sm font-bold text-slate-900">{c.title}</div>
                  <div className="text-[11px] text-slate-500">
                    {c.location_address || c.ward || 'Bengaluru'}
                  </div>
                </div>
                <Link
                  to={`/complaints/${c.id}`}
                  className="px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white font-semibold rounded-lg text-xs shrink-0"
                >
                  Triage
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All Complaints Table with Filters */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        {/* Table Filter Controls */}
        <div className="p-5 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search size={16} className="absolute left-3.5 top-3 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by title, category, or ward..."
              className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-1 focus:ring-teal-500 text-slate-900 font-medium"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 focus:outline-none"
            >
              <option value="all">All Priorities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 focus:outline-none"
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

        {/* Table Content */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/80 text-slate-500 font-bold uppercase tracking-wider text-[10px] border-b border-slate-100">
              <tr>
                <th className="py-3 px-4">Ref ID</th>
                <th className="py-3 px-4">Incident Title</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Current Status</th>
                <th className="py-3 px-4">Quick Action</th>
                <th className="py-3 px-4 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3.5 px-4 font-mono font-semibold text-slate-400">
                    #{item.id.slice(0, 8)}
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-slate-900 max-w-xs truncate">{item.title}</div>
                    <div className="text-[11px] text-slate-400 truncate">
                      {item.location_address || item.ward || 'Bengaluru'}
                    </div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="capitalize text-slate-700 font-medium">
                      {item.category.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold capitalize ${
                        item.priority === 'critical'
                          ? 'bg-rose-100 text-rose-700'
                          : item.priority === 'high'
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {item.priority}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <select
                      value={item.status}
                      onChange={(e) => handleQuickStatusChange(item.id, e.target.value)}
                      className="px-2 py-1 rounded-lg text-xs font-semibold bg-slate-100 border border-slate-200 text-slate-800"
                    >
                      <option value="submitted">Submitted</option>
                      <option value="under_review">Under Review</option>
                      <option value="in_progress">In Progress</option>
                      <option value="resolved">Resolved</option>
                      <option value="rejected">Rejected</option>
                    </select>
                  </td>
                  <td className="py-3.5 px-4">
                    <button
                      onClick={() => handleQuickStatusChange(item.id, 'resolved')}
                      className="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 transition-colors"
                    >
                      Mark Resolved
                    </button>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <Link
                      to={`/complaints/${item.id}`}
                      className="inline-flex items-center gap-1 text-teal-600 hover:text-teal-700 font-bold"
                    >
                      <span>View</span>
                      <ChevronRight size={13} />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
