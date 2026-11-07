import { apiClient } from './api';
import type { UserRegister, UserLogin, TokenResponse, UserResponse } from '../types';

/** Register a new user. Returns the created user profile. */
export async function register(data: UserRegister): Promise<UserResponse> {
  const response = await apiClient.post<UserResponse>('/auth/register', data);
  return response.data;
}

/** Login. Stores the access token in localStorage and returns the token response. */
export async function login(data: UserLogin): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('/auth/login', data);
  const { access_token } = response.data;
  localStorage.setItem('proofrun_token', access_token);
  return response.data;
}

/** Fetch the currently authenticated user's profile. */
export async function getCurrentUser(): Promise<UserResponse> {
  const response = await apiClient.get<UserResponse>('/auth/me');
  return response.data;
}

/** Remove the stored token (logout). */
export function logout(): void {
  localStorage.removeItem('proofrun_token');
}

/** Returns true if a token is stored (may still be expired). */
export function isAuthenticated(): boolean {
  return !!localStorage.getItem('proofrun_token');
}
