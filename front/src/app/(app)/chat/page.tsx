"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Send, Bot, User, ArrowRight } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { healthAPI } from "@/lib/api/client";
import { createClient } from "@/lib/supabase/client";
import { LoadingSpinner, PermanentDisclaimer } from "@/components";
import type { ConversationMessage } from "@/lib/types";

export default function AssessmentPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [modelUsed, setModelUsed] = useState<string | null>(null);
  const [assessmentId, setAssessmentId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const loadHistory = async () => {
      setIsLoadingHistory(true);
      
      try {
        const supabase = createClient();
        
        // 1. Get current user
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) {
          // No user logged in, show welcome message
          showWelcomeMessage();
          setIsLoadingHistory(false);
          return;
        }

        // 2. Load the user's session from Supabase (there's only one per user)
        const { data: sessionData, error: sessionError } = await supabase
          .from("chat_sessions")
          .select("id, assessment_id")
          .eq("user_id", user.id)
          .order("created_at", { ascending: false })
          .limit(1);

        if (sessionError) {
          console.error("Error loading session:", sessionError);
          showWelcomeMessage();
          setIsLoadingHistory(false);
          return;
        }

        // 3. If we have a session, check if it has a completed assessment
        if (sessionData && sessionData.length > 0) {
          const activeSessionId = sessionData[0].id;
          const assessmentId = sessionData[0].assessment_id;
          
          // If there's already an assessment, redirect to coach page
          if (assessmentId) {
            router.push(`/coach?assessment=${assessmentId}`);
            return;
          }
          
          // Load existing messages for incomplete session
          const { data: historyData, error: historyError } = await supabase
            .from("chat_messages")
            .select("id, role, content, created_at")
            .eq("session_id", activeSessionId)
            .order("created_at", { ascending: true });

          if (!historyError && historyData && historyData.length > 0) {
            // Convert Supabase messages to ConversationMessage format
            const loadedMessages: ConversationMessage[] = historyData.map((msg) => ({
              id: msg.id,
              role: msg.role as "user" | "assistant",
              content: msg.content,
              timestamp: new Date(msg.created_at),
            }));
            
            setMessages(loadedMessages);
            setSessionId(activeSessionId);
            setIsLoadingHistory(false);
            return;
          }
        }

        // 4. No active session found, show welcome message
        showWelcomeMessage();
        
      } catch (error) {
        console.error("Error loading history:", error);
        showWelcomeMessage();
      }
      
      setIsLoadingHistory(false);
    };

    const showWelcomeMessage = () => {
      const welcomeMessage: ConversationMessage = {
        id: "welcome",
        role: "assistant",
        content: "¡Hola! Soy tu asistente de salud CardioSense 🩺\n\nVoy a ayudarte a evaluar tu riesgo cardiometabólico de manera conversacional. Solo cuéntame sobre ti de forma natural, como si conversáramos.\n\nPor ejemplo, puedes decirme: \"Tengo 35 años, mido 170cm, peso 75kg y mi cintura mide 85cm. Duermo unas 7 horas y hago ejercicio 3 veces por semana.\"\n\n¿Qué me puedes contar sobre ti?",
        timestamp: new Date(),
      };
      setMessages([welcomeMessage]);
    };

    loadHistory();
  }, [router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ConversationMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setError(null);

    try {
      const response = await healthAPI.message(input, sessionId || undefined);

      // Store session_id if this is the first message
      if (response.session_id && !sessionId) {
        setSessionId(response.session_id);
      }

      if (response.model_used) {
        setModelUsed(response.model_used);
      }

      if (response.assessment_id) {
        setAssessmentId(response.assessment_id);
      }

      const assistantMessage: ConversationMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.reply,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // If prediction is complete, redirect to coach page
      if (response.prediction_made) {
        setTimeout(() => {
          if (response.assessment_id) {
            router.push(`/coach?assessment=${response.assessment_id}`);
          } else {
            router.push(`/coach`);
          }
        }, 1500);
      }
    } catch (err) {
      console.error("Error sending message:", err);
      let errorMessage = "Error al procesar tu mensaje. Inténtalo de nuevo.";

      if (err instanceof Error) {
        if (err.message.includes("fetch") || err.message.includes("Network")) {
          errorMessage = "No se pudo conectar con el servidor. Verifica que el backend esté ejecutándose.";
        } else {
          errorMessage = err.message;
        }
      }

      setError(errorMessage);

      const errorAssistantMessage: ConversationMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Lo siento, hubo un error: ${errorMessage}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorAssistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-red-50 via-white to-pink-50">
      <div className="bg-gradient-to-r from-red-600 via-pink-600 to-red-600 text-white px-4 sm:px-6 lg:px-8 py-6 shadow-lg">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-white/20 backdrop-blur-sm rounded-full p-3">
                <Bot className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold">Evaluación de Salud</h1>
                <p className="text-red-100 text-base">
                  Cuéntame sobre tu salud de forma natural
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        <div className="max-w-5xl mx-auto h-full flex flex-col">
          {error && (
            <div className="bg-red-50 border-b-2 border-red-200 px-4 py-3">
              <p className="text-sm text-red-900 text-center font-medium">
                <strong className="text-red-700">⚠️ Error:</strong> {error}
              </p>
            </div>
          )}

          <div className="bg-gradient-to-r from-yellow-50 to-amber-50 border-b-2 border-yellow-200 px-4 py-3 shadow-sm">
            <p className="text-sm text-yellow-900 text-center font-medium">
              <strong className="text-yellow-700">⚕️ Recordatorio:</strong> Esta es una evaluación educativa. No reemplaza el consejo médico profesional.
            </p>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {isLoadingHistory ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <LoadingSpinner size="lg" />
                  <p className="mt-4 text-gray-600 font-medium">Cargando historial...</p>
                </div>
              </div>
            ) : (
              <>
                {modelUsed && (
                  <div className="bg-white border border-red-200 rounded-2xl p-4 shadow-sm animate-fade-in">
                    <p className="text-sm font-semibold text-red-600 uppercase tracking-wide">
                      Evaluación completada
                    </p>
                    <p className="text-base text-gray-700 mt-1">
                      El asistente seleccionó el modelo
                      {" "}
                      <span className="font-semibold text-gray-900">
                        {modelUsed === "cardiovascular" ? "Cardiovascular" : "Diabetes"}
                      </span>
                      {" "}
                      para tu perfil.
                    </p>
                    {assessmentId && (
                      <div className="mt-3">
                        <Link
                          href={`/coach?assessment=${assessmentId}`}
                          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
                        >
                          Ver plan personalizado
                          <ArrowRight className="h-4 w-4" />
                        </Link>
                      </div>
                    )}
                  </div>
                )}

                
                {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-4 ${
                  message.role === "user" ? "justify-end" : "justify-start"
                } animate-fade-in`}
              >
                {message.role === "assistant" && (
                  <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-red-600 to-pink-600 rounded-full flex items-center justify-center shadow-lg">
                    <Bot className="h-6 w-6 text-white" />
                  </div>
                )}

                <div
                  className={`max-w-2xl rounded-2xl p-5 shadow-md ${
                    message.role === "user"
                      ? "bg-gradient-to-br from-red-600 to-pink-600 text-white"
                      : "bg-white border-2 border-gray-100"
                  }`}
                >
                  {message.role === "assistant" ? (
                    <div className="prose prose-sm max-w-none text-gray-800">
                      <ReactMarkdown
                        components={{
                          p: ({ children }) => <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>,
                          strong: ({ children }) => <strong className="font-bold text-gray-900">{children}</strong>,
                          em: ({ children }) => <em className="italic">{children}</em>,
                          ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>,
                          ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>,
                          li: ({ children }) => <li className="ml-2">{children}</li>,
                          h1: ({ children }) => <h1 className="text-xl font-bold mb-2 text-gray-900">{children}</h1>,
                          h2: ({ children }) => <h2 className="text-lg font-bold mb-2 text-gray-900">{children}</h2>,
                          h3: ({ children }) => <h3 className="text-base font-bold mb-2 text-gray-900">{children}</h3>,
                          code: ({ children }) => (
                            <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono text-red-600">
                              {children}
                            </code>
                          ),
                          blockquote: ({ children }) => (
                            <blockquote className="border-l-4 border-gray-300 pl-4 italic my-3">
                              {children}
                            </blockquote>
                          ),
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p className="text-base whitespace-pre-wrap leading-relaxed text-white">
                      {message.content}
                    </p>
                  )}

                  <p
                    className={`text-xs mt-3 ${
                      message.role === "user" ? "text-red-100" : "text-gray-400"
                    }`}
                  >
                    {message.timestamp.toLocaleTimeString("es-CL", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>

                {message.role === "user" && (
                  <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-gray-700 to-gray-900 rounded-full flex items-center justify-center shadow-lg">
                    <User className="h-6 w-6 text-white" />
                  </div>
                )}
              </div>
            ))}

                {isLoading && (
                  <div className="flex gap-4 animate-fade-in">
                    <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-red-600 to-pink-600 rounded-full flex items-center justify-center shadow-lg animate-pulse">
                      <Bot className="h-6 w-6 text-white" />
                    </div>
                    <div className="bg-white border-2 border-gray-100 rounded-2xl p-5 shadow-md">
                      <div className="flex items-center gap-3">
                        <LoadingSpinner size="sm" />
                        <span className="text-base text-gray-700 font-medium">
                          Procesando tu información...
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          <div className="bg-white border-t-2 border-gray-200 p-4 shadow-lg">
            <div className="max-w-4xl mx-auto">
              <div className="flex gap-3 items-end">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Escribe tus datos aquí... (Presiona Enter para enviar)"
                  className="flex-1 px-5 py-4 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 resize-none transition-all text-base"
                  rows={2}
                  disabled={isLoading}
                />
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  className="px-8 py-4 bg-gradient-to-r from-red-600 to-pink-600 text-white rounded-xl font-bold hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center gap-2"
                >
                  <Send className="h-5 w-5" />
                  Enviar
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border-t-2 border-gray-200 px-4 py-3">
        <div className="max-w-5xl mx-auto">
          <PermanentDisclaimer />
        </div>
      </div>
    </div>
  );
}
