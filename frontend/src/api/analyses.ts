import { apiClient } from './client';

export interface AnalysesResponse {
  analyses: Record<string, any>;
}

export interface UpdateAnalysesRequest {
  analyses: Record<string, any>;
}

export async function updateAnalyses(analyses: Record<string, any>): Promise<AnalysesResponse> {
  return apiClient.post<AnalysesResponse>('/api/analyses/summary', { analyses });
}

