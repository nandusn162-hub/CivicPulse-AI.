import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Sparkles,
  ShieldAlert,
  Clock,
  CheckCircle2,
  Building2,
  Calendar,
  MapPin,
  TrendingUp,
  AlertCircle,
  Activity,
  Layers,
  Send,
  User,
} from 'lucide-react';
import {
  fetchComplaintById,
  fetchAIAnalysis,
  fetchComplaintTimeline,
  updateComplaint,
  ComplaintData,
  AIAnalysisData,
  TimelineEvent,
} from '../lib/api';
import { useAuthStore } from '../store/auth';

export default function ComplaintDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [complaint, setComplaint] = useState<ComplaintData | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<AIAnalysisData | null>(null);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Status update state
  const [newStatus, setNewStatus] = useState<string>('');
  const [newPriority, setNewPriority] = useState<string>('');
  const [assignedTo, setAssignedTo] = useState<string>('');
  const [resolutionNotes, setResolutionNotes] = useState<string>('');
  const [updating, setUpdating] = useState(false);
  const [updateSuccess, setUpdateSuccess] = useState(false);

  const { user } = useAuthStore();

  useEffect(() => {
    if (id) {
      loadComplaintData(id);
    }
  }, [id]);

  const loadComplaintData = async (complaintId: string) => {
    setLoading(true);
    setError(null);
    try {
      const [compData, aiData, timelineData] = await Promise.all([
        fetchComplaintById(complaintId),
        fetchAIAnalysis(complaintId).catch(() => null),
        fetchComplaintTimeline(complaintId).catch(() => []),
      ]);
      setComplaint(compData);
      setAiAnalysis(aiData);
      setTimeline(timelineData);
      setNewStatus(compData.status);
      setNewPriority(compData.priority);
      setAssignedTo(compData.assigned_to || '');
      setResolutionNotes(compData.resolution_notes || '');
    } catch (err: any) {
      setError(err.message || 'Failed to load complaint details.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;
    setUpdating(true);
    setUpdateSuccess(false);

    try {
      const updated = await updateComplaint(id, {
        status: newStatus,
        priority: newPriority,
        assigned_to: assignedTo,
        resolution_notes: resolutionNotes,
      });
      setComplaint(updated);
      setUpdateSuccess(true);
      // Refresh timeline
      const updatedTimeline = await fetchComplaintTimeline(id);
      setTimeline(updatedTimeline);
      setTimeout(() => setUpdateSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to update complaint.');
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center text-slate-400">
        <div className="w-8 h-8 border-3 border-teal-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        Loading AI diagnostics & audit history...
      </div>
    );
  }

  if (error || !complaint) {
    return (
      <div className="max-w-xl mx-auto my-12 p-6 bg-white rounded-2xl border border-slate-200 text-center">
        <AlertCircle size={36} className="mx-auto text-rose-500 mb-2" />
        <h2 className="text-lg font-bold text-slate-900">Complaint Not Found</h2>
        <p className="text-xs text-slate-500 mt-1">{error || 'Unable to retrieve grievance.'}</p>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-1.5 mt-4 px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-semibold"
        >
          <ArrowLeft size={14} /> Back to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Top Bar Navigation */}
      <div className="flex items-center justify-between">
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 bg-white px-3 py-1.5 rounded-xl border border-slate-200 shadow-2xs"
        >
          <ArrowLeft size={14} />
          <span>Back to Dashboard</span>
        </Link>
        <div className="text-xs text-slate-400 font-mono">
          Ref ID: <span className="text-slate-700 font-bold">{complaint.id}</span>
        </div>
      </div>

      {/* Header Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-teal-50 text-teal-700 border border-teal-200 uppercase tracking-wider">
              {complaint.category.replace('_', ' ')}
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold capitalize bg-slate-100 text-slate-700">
              {complaint.priority} Priority
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold capitalize bg-sky-50 text-sky-700 border border-sky-200">
              {complaint.status.replace('_', ' ')}
            </span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">{complaint.title}</h1>
          <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <MapPin size={13} className="text-slate-400" />
              {complaint.location_address || complaint.ward || 'Bengaluru Municipal Area'}
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <Calendar size={13} className="text-slate-400" />
              Logged: {new Date(complaint.created_at).toLocaleString()}
            </span>
            {complaint.assigned_to && (
              <>
                <span>•</span>
                <span className="flex items-center gap-1 text-slate-700 font-medium">
                  <Building2 size={13} className="text-teal-600" />
                  Assigned: {complaint.assigned_to}
                </span>
              </>
            )}
          </div>
        </div>

        {/* Community Impact Score Badge */}
        {aiAnalysis && (
          <div className="bg-gradient-to-br from-slate-900 to-teal-950 text-white p-4 rounded-xl text-center shrink-0 border border-teal-500/20 shadow-md">
            <div className="text-[10px] text-teal-300 font-bold uppercase tracking-wider">
              Community Impact Score
            </div>
            <div className="text-3xl font-black text-white mt-1">
              {aiAnalysis.community_impact_score.score}
              <span className="text-sm font-normal text-slate-400">/100</span>
            </div>
            <div className="text-[11px] text-teal-400 font-semibold mt-0.5">
              {aiAnalysis.community_impact_score.level} Priority Impact
            </div>
          </div>
        )}
      </div>

      {/* Main Grid: AI Intelligence vs Audit Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: AI Diagnostics & Impact Factors (2 cols on large) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Issue Description Card */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Citizen Description</h3>
            <p className="text-sm text-slate-800 leading-relaxed">{complaint.description}</p>
          </div>

          {/* AI Analysis Panel */}
          {aiAnalysis && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-5">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-lg bg-teal-500/10 text-teal-600 flex items-center justify-center">
                    <Sparkles size={16} />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">AI Diagnostic Report</h3>
                    <div className="text-[11px] text-slate-400 font-mono">
                      Engine: {aiAnalysis.model_version}
                    </div>
                  </div>
                </div>
                <div className="text-xs font-bold text-teal-700 bg-teal-50 px-2.5 py-1 rounded-full border border-teal-200">
                  {(aiAnalysis.confidence_score * 100).toFixed(0)}% AI Confidence
                </div>
              </div>

              {/* Grid of AI metrics */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/70">
                  <div className="text-[11px] text-slate-500 font-medium">Classified Issue</div>
                  <div className="text-sm font-bold text-slate-900 capitalize mt-0.5">
                    {aiAnalysis.category_detected.replace('_', ' ')}
                  </div>
                </div>
                <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/70">
                  <div className="text-[11px] text-slate-500 font-medium">Recommended Dept.</div>
                  <div className="text-sm font-bold text-slate-900 mt-0.5">
                    {aiAnalysis.recommended_department}
                  </div>
                </div>
                <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/70">
                  <div className="text-[11px] text-slate-500 font-medium">Target Resolution SLA</div>
                  <div className="text-sm font-bold text-emerald-600 mt-0.5">
                    &lt; {aiAnalysis.estimated_resolution_hours} Hours
                  </div>
                </div>
              </div>

              {/* Action Directive */}
              <div className="p-4 rounded-xl bg-teal-50/70 border border-teal-200/80 space-y-1">
                <div className="text-xs font-bold text-teal-900 flex items-center gap-1.5">
                  <Activity size={14} className="text-teal-700" />
                  <span>Action Directive:</span>
                </div>
                <p className="text-xs text-teal-800 leading-relaxed font-medium">
                  {aiAnalysis.recommended_action}
                </p>
              </div>

              {/* Community Impact Score Breakdown (Explicit explanation of factors) */}
              <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                    Community Impact Factor Breakdown
                  </h4>
                  <span className="text-xs text-slate-400">Total: {aiAnalysis.community_impact_score.score}/100</span>
                </div>

                <div className="space-y-2.5">
                  {Object.entries(aiAnalysis.community_impact_score.weights).map(([factor, item]) => (
                    <div key={factor} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="font-semibold text-slate-700 capitalize">
                          {factor} <span className="text-slate-400 font-normal">({item.weight})</span>
                        </span>
                        <span className="font-bold text-slate-900">{item.score}%</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-teal-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${item.score}%` }}
                        ></div>
                      </div>
                      <div className="text-[11px] text-slate-500">{item.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Admin & Department Officer Status Update Form */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
              <Building2 size={16} className="text-teal-600" />
              <span>Municipal Actions & Status Management</span>
            </h3>

            {updateSuccess && (
              <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2">
                <CheckCircle2 size={15} />
                <span>Status & work order successfully updated!</span>
              </div>
            )}

            <form onSubmit={handleUpdate} className="space-y-3.5">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Status</label>
                  <select
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800"
                  >
                    <option value="submitted">Submitted</option>
                    <option value="under_review">Under Review</option>
                    <option value="in_progress">In Progress</option>
                    <option value="resolved">Resolved</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Priority</label>
                  <select
                    value={newPriority}
                    onChange={(e) => setNewPriority(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Assigned Unit</label>
                  <input
                    type="text"
                    value={assignedTo}
                    onChange={(e) => setAssignedTo(e.target.value)}
                    placeholder="e.g. Whitefield Crew #3"
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Resolution / Field Notes
                </label>
                <textarea
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                  rows={2}
                  placeholder="Details of materials used, crew dispatch, or inspection outcome..."
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800"
                />
              </div>

              <button
                type="submit"
                disabled={updating}
                className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-xl text-xs shadow-xs transition-colors disabled:opacity-50 flex items-center gap-1.5"
              >
                <Send size={13} />
                <span>{updating ? 'Updating...' : 'Save Status Update'}</span>
              </button>
            </form>
          </div>
        </div>

        {/* Right Column: Audit Timeline */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Audit & Redressal Timeline
            </h3>

            <div className="space-y-6 relative before:absolute before:inset-0 before:left-3.5 before:w-0.5 before:bg-slate-100">
              {timeline.map((event, idx) => (
                <div key={idx} className="relative flex items-start gap-3">
                  <div
                    className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 z-10 text-xs ${
                      event.status === 'completed'
                        ? 'bg-teal-600 text-white'
                        : event.status === 'active'
                        ? 'bg-sky-500 text-white animate-pulse'
                        : event.status === 'rejected'
                        ? 'bg-rose-500 text-white'
                        : 'bg-slate-200 text-slate-500'
                    }`}
                  >
                    {event.status === 'completed' ? (
                      <CheckCircle2 size={14} />
                    ) : event.status === 'active' ? (
                      <Clock size={14} />
                    ) : (
                      idx + 1
                    )}
                  </div>
                  <div className="space-y-0.5">
                    <div className="text-xs font-bold text-slate-900">{event.stage}</div>
                    <div className="text-xs text-slate-600 font-medium">{event.title}</div>
                    <div className="text-[11px] text-slate-400">{event.description}</div>
                    {event.timestamp && (
                      <div className="text-[10px] text-slate-400 font-mono pt-1">
                        {new Date(event.timestamp).toLocaleString()}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
