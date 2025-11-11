import axios from 'axios';
import { API_BASE_URL } from '../config';

export interface HealthResponse {
  status: string;
}

export async function checkHealth(): Promise<HealthResponse> {
  // Health check doesn't need authentication, so we use axios directly
  // to avoid sending Telegram initData header
  try {
    const response = await axios.get<HealthResponse>(`${API_BASE_URL}/health`, {
      timeout: 5000, // 5 seconds timeout for health check
      validateStatus: (status) => status < 500, // Accept any status < 500
    });
    return response.data;
  } catch (error: any) {
    console.error('Health check error:', error.message, error.code);
    throw error;
  }
}

/**
 * Проверяет готовность бэкенда с повторными попытками
 * @param maxRetries Максимальное количество попыток
 * @param retryDelay Задержка между попытками в миллисекундах
 * @param maxWaitTime Максимальное время ожидания в миллисекундах
 * @returns Promise, который резолвится когда бэкенд готов
 */
export async function waitForBackendReady(
  maxRetries: number = 30,
  retryDelay: number = 2000,
  maxWaitTime: number = 60000
): Promise<HealthResponse> {
  const startTime = Date.now();
  let lastError: any = null;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    // Проверяем максимальное время ожидания
    if (Date.now() - startTime > maxWaitTime) {
      throw new Error(`Backend не готов после ${maxWaitTime}ms ожидания`);
    }

    try {
      const response = await checkHealth();
      // Проверяем, что статус успешный
      if (response.status === 'ok') {
        console.log(`Backend готов после ${attempt} попыток`);
        return response;
      }
    } catch (error: any) {
      lastError = error;
      console.log(`Попытка ${attempt}/${maxRetries}: бэкенд еще не готов...`);
      
      // Если это не последняя попытка, ждем перед следующей
      if (attempt < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, retryDelay));
      }
    }
  }

  // Если все попытки исчерпаны, выбрасываем последнюю ошибку
  throw lastError || new Error('Backend не готов после всех попыток');
}

