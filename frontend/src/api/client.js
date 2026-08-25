// Thin fetch wrapper around the backend API.
// TODO(frontend): fill in each call once the backend routes are live.

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function createCompany(payload) {
  // TODO(frontend): POST {name, phone_number} to `${BASE_URL}/companies/`
  throw new Error("not implemented");
}

export async function uploadDocument(companyId, file) {
  // TODO(frontend): multipart POST to `${BASE_URL}/documents/upload?company_id=${companyId}`
  throw new Error("not implemented");
}

export async function triggerIntake(companyId, callerNumber) {
  // TODO(frontend): POST to `${BASE_URL}/calls/intake` — used by the "Simulate missed call" button.
  throw new Error("not implemented");
}

export async function listCalls(companyId) {
  // TODO(frontend): GET `${BASE_URL}/calls/?company_id=${companyId}` — feeds the dashboard table.
  throw new Error("not implemented");
}

export async function getCallDetail(callJobId) {
  // TODO(frontend): GET `${BASE_URL}/calls/${callJobId}`
  throw new Error("not implemented");
}
