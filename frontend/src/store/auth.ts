import { create } from 'zustand';

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  phone_number?: string;
  role: 'citizen' | 'admin' | 'field_inspector' | 'department_officer' | 'supervisor';
  ward_id?: string;
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserProfile | null;
  setTokens: (access: string, refresh: string, user?: UserProfile) => void;
  setUser: (user: UserProfile) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: localStorage.getItem('access_token'),
  refreshToken: localStorage.getItem('refresh_token'),
  user: localStorage.getItem('user_profile')
    ? JSON.parse(localStorage.getItem('user_profile')!)
    : null,
  setTokens: (access, refresh, user) => {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    if (user) {
      localStorage.setItem('user_profile', JSON.stringify(user));
    }
    set({ accessToken: access, refreshToken: refresh, ...(user ? { user } : {}) });
  },
  setUser: (user) => {
    localStorage.setItem('user_profile', JSON.stringify(user));
    set({ user });
  },
  clear: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_profile');
    set({ accessToken: null, refreshToken: null, user: null });
  },
}));
