import { apiClient } from './api';
import type { ExecuteRequest, ExecuteResponse, HealthResponse } from '../types';

/** Execute the code for a given task. */
export async function executeCode(data: ExecuteRequest): Promise<ExecuteResponse> {
  const response = await apiClient.post<ExecuteResponse>('/execute', data);
  return response.data;
}

/** Fetch the authenticated user's execution history with pagination. */
export async function getExecutionHistory(skip = 0, limit = 20): Promise<ExecuteResponse[]> {
  const response = await apiClient.get<ExecuteResponse[]>('/executions', {
    params: { skip, limit },
  });
  return response.data;
}

/** Health check – useful to test backend connectivity. */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>('/health');
  return response.data;
}
