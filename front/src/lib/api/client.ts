import { createClient } from "@/lib/supabase/client";
import type { MessageResponse } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_AVAILABLE = process.env.NEXT_PUBLIC_API_AVAILABLE !== "false";

export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: unknown
  ) {
    super(message);
    this.name = "APIError";
  }
}

async function getAuthToken(): Promise<string | null> {
  try {
    const supabase = createClient();
    const {
      data: { session },
    } = await supabase.auth.getSession();
    return session?.access_token || null;
  } catch (error) {
    console.error("Error getting auth token:", error);
    return null;
  }
}

async function fetchWithAuth(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = await getAuthToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorData: { message?: string; detail?: string };
      try {
        errorData = await response.json();
      } catch {
        errorData = { message: response.statusText };
      }

      throw new APIError(
        errorData.message || errorData.detail || "API request failed",
        response.status,
        errorData
      );
    }

    return response;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError("Network error: Unable to connect to the server");
  }
}

export const healthAPI = {
  async message(
    content: string,
    sessionId?: string
  ): Promise<MessageResponse> {
    if (!API_AVAILABLE) {
      return {
        reply:
          "El servicio de mensajería inteligente no está disponible porque el backend no está conectado. Conéctalo y vuelve a intentarlo.",
        extracted_data: {},
        is_ready: false,
        action: "continue",
        session_id: sessionId,
        prediction_made: false,
        model_used: undefined,
        assessment_id: undefined,
      };
    }

    const requestBody = {
      content,
      session_id: sessionId || null,
    };

    const response = await fetchWithAuth("/api/chat/message", {
      method: "POST",
      body: JSON.stringify(requestBody),
    });

    const result = await response.json();
    
    // Transform backend response to frontend format
    return {
      reply: result.response.content,
      extracted_data: {},
      is_ready: result.prediction_made,
      action: result.prediction_made ? "redirect_results" : "continue",
      session_id: result.session_id,
      prediction_made: result.prediction_made,
      model_used: result.model_used ?? undefined,
      assessment_id: result.assessment_id ?? undefined,
    };
  },
};

export default healthAPI;

