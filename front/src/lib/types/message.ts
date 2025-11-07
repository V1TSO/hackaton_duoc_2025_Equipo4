import { AssessmentData, Driver } from "./assessment";

export interface ConversationMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export interface MessageRequest {
  message: string;
  conversation_history: Array<{ role: string; content: string }>;
  session_data?: Partial<AssessmentData>;
}

export interface PredictionResult {
  score: number;
  risk_level: string;
  drivers: Driver[];
  model_used: string;
}

export interface MessageResponse {
  reply: string;
  extracted_data?: Partial<AssessmentData>;
  is_ready: boolean;
  prediction?: PredictionResult;
  action: "continue" | "redirect_results" | "redirect_coach";
  redirect_url?: string;
  assessment_id?: string;
  session_id?: string;
  prediction_made?: boolean;
  model_used?: string;
}

export interface ConversationState {
  messages: ConversationMessage[];
  extractedData: Partial<AssessmentData>;
  isComplete: boolean;
}

