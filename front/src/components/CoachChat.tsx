"use client";

import { useState, useEffect, useRef } from "react";
import { Send, Bot, User, MessageSquare } from "lucide-react";
import { healthAPI } from "@/lib/api/client";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface CoachChatProps {
  assessmentId: string;
}

export function CoachChat({ assessmentId }: CoachChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isExpanded && messages.length === 0) {
      // Show welcome message
      const welcomeMessage: Message = {
        id: "welcome",
        role: "assistant",
        content: "¡Hola! Soy tu coach de salud CardioSense. Estoy aquí para ayudarte a seguir tu plan personalizado. ¿Tienes alguna pregunta sobre tus recomendaciones?",
        timestamp: new Date(),
      };
      setMessages([welcomeMessage]);
    }
  }, [isExpanded, messages.length]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await healthAPI.coachMessage(input, assessmentId);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.reply,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Error sending coach message:", err);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Lo siento, hubo un error al procesar tu mensaje. Por favor intenta de nuevo.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
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

  if (!isExpanded) {
    return (
      <section className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-3xl shadow-sm p-6">
        <button
          onClick={() => setIsExpanded(true)}
          className="w-full flex items-center justify-between hover:bg-green-100 rounded-xl p-4 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="bg-green-600 text-white rounded-full p-3">
              <MessageSquare className="h-6 w-6" />
            </div>
            <div className="text-left">
              <h3 className="text-xl font-semibold text-gray-900">
                Chatea con tu Coach
              </h3>
              <p className="text-gray-600 text-sm">
                Haz preguntas sobre tu plan y recibe orientación personalizada
              </p>
            </div>
          </div>
          <Send className="h-5 w-5 text-gray-400" />
        </button>
      </section>
    );
  }

  return (
    <section className="bg-white border border-gray-200 rounded-3xl shadow-sm overflow-hidden">
      <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 backdrop-blur-sm rounded-full p-2">
              <MessageSquare className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Coach de Salud</h3>
              <p className="text-green-100 text-sm">
                Orientación basada en tu plan
              </p>
            </div>
          </div>
          <button
            onClick={() => setIsExpanded(false)}
            className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>

      <div className="h-96 overflow-y-auto p-6 space-y-4 bg-gray-50">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${
              message.role === "user" ? "justify-end" : "justify-start"
            } animate-fade-in`}
          >
            {message.role === "assistant" && (
              <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-green-600 to-emerald-600 rounded-full flex items-center justify-center">
                <Bot className="h-5 w-5 text-white" />
              </div>
            )}

            <div
              className={`max-w-xl rounded-2xl p-4 ${
                message.role === "user"
                  ? "bg-gradient-to-br from-green-600 to-emerald-600 text-white"
                  : "bg-white border border-gray-200"
              }`}
            >
              {message.role === "assistant" ? (
                <MarkdownRenderer content={message.content} />
              ) : (
                <p className="text-sm whitespace-pre-wrap leading-relaxed">
                  {message.content}
                </p>
              )}

              <p
                className={`text-xs mt-2 ${
                  message.role === "user" ? "text-green-100" : "text-gray-400"
                }`}
              >
                {message.timestamp.toLocaleTimeString("es-CL", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
            </div>

            {message.role === "user" && (
              <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-gray-700 to-gray-900 rounded-full flex items-center justify-center">
                <User className="h-5 w-5 text-white" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3 animate-fade-in">
            <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-green-600 to-emerald-600 rounded-full flex items-center justify-center animate-pulse">
              <Bot className="h-5 w-5 text-white" />
            </div>
            <div className="bg-white border border-gray-200 rounded-2xl p-4">
              <div className="flex items-center gap-2">
                <LoadingSpinner size="sm" />
                <span className="text-sm text-gray-700">
                  Tu coach está pensando...
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="bg-white border-t border-gray-200 p-4">
        <div className="flex gap-2 items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Escribe tu pregunta aquí..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-green-500 resize-none text-sm"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl font-semibold hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center gap-2"
          >
            <Send className="h-4 w-4" />
            Enviar
          </button>
        </div>
      </div>
    </section>
  );
}

