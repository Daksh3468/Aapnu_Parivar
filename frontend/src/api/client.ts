const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export interface HealthCheckResponse {
  status: string;
  project: string;
  version: string;
  environment: string;
  demo_mode: boolean;
  database: string;
  timestamp: number;
}

export async function fetchHealthCheck(): Promise<HealthCheckResponse> {
  const response = await fetch(`${API_BASE_URL}/health`, {
    headers: {
      'Accept': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Health check failed with status: ${response.status}`);
  }

  return response.json();
}
