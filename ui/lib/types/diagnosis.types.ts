export interface DiagnosisMessage {
  role: "user" | "assistant";
  message: string;
}

export interface DiagnosisResult {
  finding: string;
  recommendation: string;
}

export interface DiagnosisContext {
  initial_prompt: string;
  conversation_history: DiagnosisMessage[];
  state?: Record<string, unknown>;
  plant_vitals?: {
    name: string;
    care_schedule?: {
      care_instructions: string;
      watering_schedule: string;
    };
  };
  result?: DiagnosisResult;
}

export interface DiagnosisSession {
  id: string;
  plant_id: string;
  status: "PENDING_USER_INPUT" | "COMPLETED" | "CANCELLED";
  diagnosis_context: DiagnosisContext;
  created_at: string;
  updated_at: string;
}

export interface DiagnosisResponse {
  diagnosis_id: string;
  status: "PENDING_USER_INPUT" | "COMPLETED";
  ai_question?: string;
  result?: DiagnosisResult;
}

export interface IDiagnosisAdapter {
  getDiagnoses(plantId: string): Promise<DiagnosisSession[]>;
  getDiagnosis(diagnosisId: string): Promise<DiagnosisSession>;
  deleteDiagnosis(diagnosisId: string): Promise<void>;
  startDiagnosis(plantId: string, prompt: string): Promise<DiagnosisResponse>;
  continueDiagnosis(
    diagnosisId: string,
    message: string
  ): Promise<DiagnosisResponse>;
}
