import { apiClient } from './client';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { getTelegramInitData } from '../utils/telegram';

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

export interface UploadFileResponse {
  success: boolean;
  fileName: string;
  mime: string;
  size: number;
  webhookStatus: number;
  webhookResponse?: string;
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

export async function uploadFileToWebhook(
  file: File
): Promise<UploadFileResponse> {
  const uploadUrl = `${API_BASE_URL}/api/upload-file`;
  console.log('=== Upload File to Webhook ===');
  console.log('API_BASE_URL:', API_BASE_URL);
  console.log('Upload URL:', uploadUrl);
  console.log('File name:', file.name);
  console.log('File size:', file.size);
  console.log('File type:', file.type);
  
  const formData = new FormData();
  formData.append('file', file);
  formData.append('fileName', file.name);
  formData.append('mimeType', file.type || 'application/octet-stream');
  formData.append('size', String(file.size));

  const initData = getTelegramInitData();
  console.log('Telegram initData available:', !!initData);
  console.log('InitData length:', initData?.length || 0);
  
  const headers: Record<string, string> = {};
  if (initData) {
    headers['x-telegram-initdata'] = initData;
    console.log('Added x-telegram-initdata header');
  } else {
    console.warn('WARNING: No Telegram initData available!');
  }

  console.log('Sending request to:', uploadUrl);
  console.log('Request headers:', headers);
  
  try {
    const response = await axios.post<UploadFileResponse>(
      uploadUrl,
      formData,
      {
        headers,
        timeout: 50000,
        maxContentLength: Infinity,
        maxBodyLength: Infinity,
      }
    );
    
    console.log('Request successful!');
    console.log('Response status:', response.status);
    console.log('Response data:', response.data);
    
    return response.data;
  } catch (error: any) {
    console.error('=== Upload Error ===');
    console.error('Error type:', error.constructor.name);
    console.error('Error message:', error.message);
    console.error('Error code:', error.code);
    console.error('Request URL:', error.config?.url);
    console.error('Request method:', error.config?.method);
    console.error('Response status:', error.response?.status);
    console.error('Response statusText:', error.response?.statusText);
    console.error('Response data:', error.response?.data);
    console.error('Response headers:', error.response?.headers);
    throw error;
  }
}

