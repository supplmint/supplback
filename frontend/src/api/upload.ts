import { apiClient } from './client';

export interface NotifyUploadRequest {
  fileName: string;
  mime: string;
  size: number;
}

export interface NotifyUploadResponse {
  fileName: string;
  mime: string;
  size: number;
  analyses: Record<string, any>;
}

export async function notifyUpload(
  fileName: string,
  mime: string,
  size: number
): Promise<NotifyUploadResponse> {
  return apiClient.post<NotifyUploadResponse>('/api/notify-upload', {
    fileName,
    mime,
    size,
  });
}

