import { apiClient } from './client';

export interface RecommendationsResponse {
  recommendations: Record<string, any>;
}

export interface UpdateRecommendationsRequest {
  recommendations: Record<string, any>;
}

export async function updateRecommendations(
  recommendations: Record<string, any>
): Promise<RecommendationsResponse> {
  return apiClient.post<RecommendationsResponse>('/api/reco/basic', { recommendations });
}

