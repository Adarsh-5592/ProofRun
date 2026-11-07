import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://structures-various-informational-drives.trycloudflare.com/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach Bearer token to every authenticated request
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('proofrun_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 Unauthorized – clear session and redirect to login
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('proofrun_token');
      // Redirect to login only if not already there
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

/**
 * Extract a user-readable error message from an Axios error.
 * Supports status codes: 401, 403, 404, 422, 429, 500, 502, and network failures.
 */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    // If backend returned a specific error detail
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      return detail.map((d: { msg?: string; loc?: string[] }) => d.msg || JSON.stringify(d)).join(', ');
    }

    const status = error.response?.status;
    if (status === 401) return 'Authentication required or session expired. Please log in again.';
    if (status === 403) return 'Access denied. You do not have permission to perform this action.';
    if (status === 404) return 'Requested resource not found.';
    if (status === 422) return 'Validation error. Please verify your input and try again.';
    if (status === 429) return 'Rate limit exceeded. Too many requests. Please wait a moment and try again.';
    if (status === 502) return 'AI code generation service temporarily unavailable. Please try again.';
    if (status === 500) return 'Internal backend error. Please try again later.';

    // Network failures / tunnel offline
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK' || !error.response) {
      return 'Cannot connect to backend server. The Cloudflare tunnel may be offline or unreachable.';
    }

    return error.message || 'An unexpected error occurred.';
  }
  if (error instanceof Error) return error.message;
  return 'An unexpected error occurred.';
}
