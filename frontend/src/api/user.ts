import { apiClient } from './client';

export interface UserProfile {
  tgid: string;
  profile: Record<string, any>;
}

export interface UpdateProfileRequest {
  profile: Record<string, any>;
}

export async function getMe(): Promise<UserProfile> {
  return apiClient.get<UserProfile>('/api/me');
}

export async function updateProfile(profile: Record<string, any>): Promise<UserProfile> {
  return apiClient.post<UserProfile>('/api/me', { profile });
}

export interface AnalysisItem {
  text?: string;
  report?: string;
  fileName?: string;
  createdAt?: string;
  created_at?: string;
  [key: string]: any;
}

export interface AnalysesHistoryResponse {
  analyses: AnalysisItem[];
}

export async function getAnalysesHistory(): Promise<AnalysesHistoryResponse> {
  return apiClient.get<AnalysesHistoryResponse>('/api/analyses/history');
}

