// Auth types
export interface UserResponse {
  id: number;
  full_name: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserRegister {
  full_name: string;
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

// Task types
export interface GenerateRequest {
  prompt: string;
}

export interface GenerateResponse {
  id: string;
  prompt: string;
  generated_code: string;
  model_name: string;
  generation_status: 'generating' | 'completed' | 'failed';
  created_at: string;
}

// Execution types
export interface ExecuteRequest {
  task_id: string;
  timeout_seconds: number;
}

export type ExecutionStatus =
  | 'success'
  | 'error'
  | 'timeout'
  | 'output_limit'
  | 'memory_limit'
  | 'sandbox_error'
  | 'sandbox_busy'
  | 'cleanup_error';

export interface ExecuteResponse {
  id: string;
  task_id: string;
  status: ExecutionStatus;
  stdout: string;
  stderr: string;
  exit_code: number | null;
  timed_out: boolean;
  output_limited: boolean;
  oom_killed: boolean;
  cleanup_ok: boolean;
  duration_ms: number | null;
  error: string | null;
  created_at: string;
}

// Health check
export interface HealthResponse {
  status: string;
  application: string;
  version: string;
}

// API error
export interface ApiError {
  detail: string;
}

// Pagination
export interface PaginationParams {
  skip: number;
  limit: number;
}
