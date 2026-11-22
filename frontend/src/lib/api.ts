import { useAuthStore } from '../store/auth';

const API_BASE = (import.meta as any).env?.VITE_API_URL ?? 'http://127.0.0.1:8000';

export async function refresh(refreshToken: string): Promise<TokenPair> {
  const resp = await fetch(`${API_BASE}/api/v1/auth/refresh`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${refreshToken}` },
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'Token refresh failed' }));
    throw new Error(err.detail ?? 'Token refresh failed');
  }
  return await resp.json();
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  phone?: string;
  password: string;
  ward_id?: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface ComplaintData {
  id: string;
  title: string;
  description: string;
  category: string;
  status: 'submitted' | 'under_review' | 'in_progress' | 'resolved' | 'closed' | 'rejected';
  priority: 'low' | 'medium' | 'high' | 'critical';
  reporter_id: string;
  location_address?: string;
  latitude?: number;
  longitude?: number;
  ward?: string;
  assigned_to?: string;
  resolution_notes?: string;
  resolved_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ComplaintStats {
  total: number;
  submitted: number;
  under_review?: number;
  in_progress: number;
  resolved: number;
  rejected?: number;
  high_priority?: number;
}

export interface AIAnalysisData {
  complaint_id: string;
  category_detected: string;
  confidence_score: number;
  severity_score: number;
  priority: string;
  recommended_department: string;
  estimated_resolution_hours: number;
  recommended_action: string;
  community_impact_score: {
    score: number;
    level: string;
    weights: {
      severity: { weight: string; score: number; description: string };
      reach: { weight: string; score: number; description: string };
      proximity: { weight: string; score: number; description: string };
      duration: { weight: string; score: number; description: string };
      corroboration: { weight: string; score: number; description: string };
    };
  };
  model_version: string;
  analyzed_at: string;
}

export interface TimelineEvent {
  stage: string;
  title: string;
  description: string;
  status: 'completed' | 'active' | 'pending' | 'rejected';
  timestamp?: string;
}

export interface DepartmentInfo {
  id: string;
  name: string;
  code: string;
  categories: string[];
  head: string;
  email: string;
  phone: string;
}

export async function login(data: { email: string; password: string }): Promise<TokenPair> {
  const form = new URLSearchParams();
  form.append('username', data.email);
  form.append('password', data.password);
  const resp = await fetch(`${API_BASE}/api/v1/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form,
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'Authentication failed' }));
    throw new Error(err.detail ?? 'Login failed');
  }
  return await resp.json();
}

export async function register(data: RegisterRequest): Promise<any> {
  const resp = await fetch(`${API_BASE}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'Registration failed' }));
    throw new Error(err.detail ?? 'Registration failed');
  }
  return await resp.json();
}

export async function fetchCurrentUser(): Promise<any> {
  return authorizedFetch('/api/v1/auth/me');
}

export async function authorizedFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const token = useAuthStore.getState().accessToken;
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(init?.headers ?? {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
  const resp = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });
  if (resp.status === 401) {
    useAuthStore.getState().clear();
    window.location.href = '/login';
    throw new Error('Session expired, please login again.');
  }
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: `Request error ${resp.status}` }));
    throw new Error(err.detail ?? `Request failed with status ${resp.status}`);
  }
  return (await resp.json()) as T;
}

export async function fetchComplaintStats(): Promise<ComplaintStats> {
  return authorizedFetch<ComplaintStats>('/api/v1/complaints/stats');
}

export async function fetchComplaints(params?: {
  skip?: number;
  limit?: number;
  status?: string;
  priority?: string;
  category?: string;
}): Promise<ComplaintData[]> {
  const query = new URLSearchParams();
  if (params?.skip) query.append('skip', String(params.skip));
  if (params?.limit) query.append('limit', String(params.limit));
  if (params?.status) query.append('status', params.status);
  if (params?.priority) query.append('priority', params.priority);
  if (params?.category) query.append('category', params.category);
  const qStr = query.toString() ? `?${query.toString()}` : '';
  return authorizedFetch<ComplaintData[]>(`/api/v1/complaints/${qStr}`);
}

export async function fetchMyComplaints(): Promise<ComplaintData[]> {
  return authorizedFetch<ComplaintData[]>('/api/v1/complaints/my');
}

export async function fetchComplaintById(id: string): Promise<ComplaintData> {
  return authorizedFetch<ComplaintData>(`/api/v1/complaints/${id}`);
}

export async function createComplaint(data: {
  title: string;
  description: string;
  category: string;
  location_address?: string;
  latitude?: number;
  longitude?: number;
  ward?: string;
}): Promise<ComplaintData> {
  return authorizedFetch<ComplaintData>('/api/v1/complaints/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateComplaint(
  id: string,
  data: {
    status?: string;
    priority?: string;
    assigned_to?: string;
    resolution_notes?: string;
  }
): Promise<ComplaintData> {
  return authorizedFetch<ComplaintData>(`/api/v1/complaints/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function fetchDepartments(): Promise<DepartmentInfo[]> {
  return authorizedFetch<DepartmentInfo[]>('/api/v1/complaints/departments');
}

export async function fetchAIAnalysis(complaintId: string): Promise<AIAnalysisData> {
  return authorizedFetch<AIAnalysisData>(`/api/v1/complaints/${complaintId}/ai-analysis`);
}

export async function fetchComplaintTimeline(complaintId: string): Promise<TimelineEvent[]> {
  return authorizedFetch<TimelineEvent[]>(`/api/v1/complaints/${complaintId}/timeline`);
}

export async function uploadEvidenceFile(file: File): Promise<{
  file_name: string;
  mime_type: string;
  file_size_bytes: number;
  file_url: string;
}> {
  const token = useAuthStore.getState().accessToken;
  const formData = new FormData();
  formData.append('file', file);
  const resp = await fetch(`${API_BASE}/api/v1/complaints/upload`, {
    method: 'POST',
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: formData,
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail ?? 'Failed to upload evidence');
  }
  return await resp.json();
}
