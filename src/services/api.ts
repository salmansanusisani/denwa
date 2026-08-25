import type { CallJob, CallResult, Company } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
  });

  if (!response.ok) {
    throw new Error(`Denwa API request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export const api = {
  getCompany: () => request<Company>('/companies/me'),
  getCallJobs: () => request<CallJob[]>('/calls'),
  getCallResult: (jobId: string) => request<CallResult>(`/calls/${jobId}/result`),
};
