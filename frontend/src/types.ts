export type CallJobStatus = 'pending' | 'in_progress' | 'done' | 'failed';

export interface Company {
  id: string;
  name: string;
  phone_number: string;
  created_at: string;
}

export interface CallJob {
  id: string;
  company_id: string;
  caller_number: string;
  status: CallJobStatus;
  created_at: string;
}

export interface CallResult {
  id: string;
  call_job_id: string;
  question_asked: string;
  answer_given: string;
  resolved: boolean;
  needs_human_followup: boolean;
  transcript_url?: string | null;
}
