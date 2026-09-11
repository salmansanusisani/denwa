export type CallJobStatus = 'pending' | 'in_progress' | 'completed' | 'failed';

export interface Company {
  id: number;
  name: string;
  phone_number: string;
}

export interface CallJob {
  id: number;
  company_id: number;
  caller_number: string;
  status: CallJobStatus;
  created_at: string | null;
  result: CallResult | null;
}

export interface CallResult {
  id: number;
  call_job_id: number;
  question_asked: string;
  answer_given: string;
  resolved: boolean;
  needs_human_followup: boolean;
  transcript_url?: string | null;
}

export interface ApiDocument {
  id: number;
  company_id: number;
  filename: string;
  uploaded_at: string | null;
  chunks_count: number;
  status: string;
}

export interface ConfigStatus {
  call_e_configured: boolean;
  call_e_base_url: string;
  telnyx_configured: boolean;
  signature_check_enabled: boolean;
  worker_enabled: boolean;
  groq_configured: boolean;
  business_phone_number: string;
  business_phone_registered: boolean;
}
