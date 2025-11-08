"use client";

import { useState } from "react";
import { RotateCcw, AlertTriangle } from "lucide-react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

export function ResetAccountButton() {
  const [isResetting, setIsResetting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const router = useRouter();

  const handleReset = async () => {
    if (!showConfirm) {
      setShowConfirm(true);
      return;
    }

    setIsResetting(true);

    try {
      const supabase = createClient();
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) {
        alert("No hay sesión activa. Por favor inicia sesión.");
        setIsResetting(false);
        return;
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      
      const response = await fetch(`${apiUrl}/api/users/reset-account`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${session.access_token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Error al resetear la cuenta");
      }

      const result = await response.json();
      
      // Limpiar localStorage
      if (typeof window !== "undefined") {
        localStorage.clear();
      }

      // Mostrar mensaje de éxito
      alert(`✅ Cuenta reseteada correctamente.\n\nEliminados:\n- ${result.deleted?.messages || 0} mensajes\n- ${result.deleted?.sessions || 0} sesiones\n- ${result.deleted?.assessments || 0} planes\n- ${result.deleted?.analisis || 0} análisis`);

      // Redirigir a la página de chat limpia
      router.push("/chat");
      router.refresh();
    } catch (error) {
      console.error("Error al resetear cuenta:", error);
      alert(`Error al resetear la cuenta: ${error instanceof Error ? error.message : "Error desconocido"}`);
    } finally {
      setIsResetting(false);
      setShowConfirm(false);
    }
  };

  if (showConfirm) {
    return (
      <div className="space-y-2">
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-xs font-semibold text-red-800 mb-1">
                ¿Estás seguro?
              </p>
              <p className="text-xs text-red-700">
                Esta acción eliminará permanentemente todos tus mensajes, sesiones, planes y análisis. Esta acción NO se puede deshacer.
              </p>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleReset}
            disabled={isResetting}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-xs font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isResetting ? (
              <>
                <div className="h-3 w-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Reseteando...
              </>
            ) : (
              <>
                <RotateCcw className="h-3 w-3" />
                Sí, resetear todo
              </>
            )}
          </button>
          <button
            onClick={() => setShowConfirm(false)}
            disabled={isResetting}
            className="px-3 py-2 text-xs font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50"
          >
            Cancelar
          </button>
        </div>
      </div>
    );
  }

  return (
    <button
      onClick={handleReset}
      className="w-full flex items-center gap-2 px-3 py-2 text-sm font-medium text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
      title="Resetear toda la cuenta (elimina todos los datos)"
    >
      <RotateCcw className="h-4 w-4" />
      Resetear cuenta
    </button>
  );
}

