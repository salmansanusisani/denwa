import type { CallJob, Company, ApiDocument, ConfigStatus } from '../types';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1').replace(/\/$/, '');

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
  });

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const body = await response.json();
      if (body?.detail) {
        detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
      }
    } catch {
      // non-JSON error body, keep status-only message
    }
    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string }>('/health'),

  createCompany: (name: string, phoneNumber: string) =>
    request<Company>('/companies/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, phone_number: phoneNumber }),
    }),

  getCompany: (companyId: number) => request<Company>(`/companies/${companyId}`),

  findCompanyByPhone: (phoneNumber: string) =>
    request<Company>(`/companies/lookup?phone_number=${encodeURIComponent(phoneNumber)}`),

  listCalls: (companyId: number) => request<CallJob[]>(`/calls/?company_id=${companyId}`),

  getCall: (jobId: number) => request<CallJob>(`/calls/${jobId}`),

  listDocuments: (companyId: number) =>
    request<ApiDocument[]>(`/documents/?company_id=${companyId}`),

  uploadDocument: (companyId: number, file: File) => {
    const form = new FormData();
    form.append('company_id', String(companyId));
    form.append('file', file);
    return request<ApiDocument>('/documents/upload', { method: 'POST', body: form });
  },

  getConfigStatus: () => request<ConfigStatus>('/internal/dev/config-status'),
};