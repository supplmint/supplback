import { Request } from "express";

export interface AuthenticatedRequest extends Request {
  tgid?: string;
}

export interface HealthAppRecord {
  id: number;
  tgid: string;
  profile: Record<string, any>;
  analyses: Record<string, any>;
  recommendations: Record<string, any>;
  created_at: Date;
  updated_at: Date;
}

export interface UpdateProfileRequest {
  profile: Record<string, any>;
}

export interface AnalysesSummaryRequest {
  analyses: Record<string, any>;
}

export interface RecommendationsRequest {
  recommendations: Record<string, any>;
}

export interface NotifyUploadRequest {
  fileName: string;
  mime: string;
  size: number;
}

