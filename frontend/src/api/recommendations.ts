import { apiClient } from './client';

export interface RecommendationsResponse {
  recommendations: Record<string, any>;
}

export interface UpdateRecommendationsRequest {
  recommendations: Record<string, any>;
}

export interface RecommendationResponse {
  analysis_id: string;
  recommendation: string;
}

export async function updateRecommendations(
  recommendations: Record<string, any>
): Promise<RecommendationsResponse> {
  return apiClient.post<RecommendationsResponse>('/api/reco/basic', { recommendations });
}

export async function getRecommendation(analysisId: string): Promise<RecommendationResponse> {
  return apiClient.get<RecommendationResponse>(`/api/recommendations/${analysisId}`);
}

