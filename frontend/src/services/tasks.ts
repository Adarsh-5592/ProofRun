import { apiClient } from './api';
import type { GenerateRequest, GenerateResponse } from '../types';

/** Submit a code-generation request. Returns the created task. */
export async function generateCode(data: GenerateRequest): Promise<GenerateResponse> {
  const response = await apiClient.post<GenerateResponse>('/generate', data);
  return response.data;
}

/** Fetch the authenticated user's task history with pagination. */
export async function getTaskHistory(skip = 0, limit = 20): Promise<GenerateResponse[]> {
  const response = await apiClient.get<GenerateResponse[]>('/tasks', {
    params: { skip, limit },
  });
  return response.data;
}
