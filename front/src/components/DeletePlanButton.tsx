"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Trash2, AlertTriangle } from "lucide-react";
import { createClient } from "@/lib/supabase/client";

interface DeletePlanButtonProps {
  assessmentId: string;
}

export function DeletePlanButton({ assessmentId }: DeletePlanButtonProps) {
  const [showConfirm, setShowConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const router = useRouter();

  const handleDelete = async () => {
    setIsDeleting(true);
    
    try {
      const supabase = createClient();
      
      // Delete the assessment
      const { error } = await supabase
        .from("assessments")
        .delete()
        .eq("id", assessmentId);

      if (error) {
        console.error("Error deleting assessment:", error);
        alert("Error al eliminar el plan. Por favor intenta de nuevo.");
        setIsDeleting(false);
        return;
      }

      // Redirect to evaluation chat
      router.push("/chat");
      router.refresh();
    } catch (err) {
      console.error("Error:", err);
      alert("Error al eliminar el plan. Por favor intenta de nuevo.");
      setIsDeleting(false);
    }
  };

  if (!showConfirm) {
    return (
      <button
        onClick={() => setShowConfirm(true)}
        className="inline-flex items-center gap-2 px-4 py-2 border-2 border-red-600 text-red-600 rounded-lg font-semibold hover:bg-red-50 transition-colors"
      >
        <Trash2 className="h-4 w-4" />
        Eliminar Plan
      </button>
    );
  }

  return (
    <div className="bg-red-50 border-2 border-red-300 rounded-xl p-6">
      <div className="flex items-start gap-3 mb-4">
        <div className="flex-shrink-0">
          <AlertTriangle className="h-6 w-6 text-red-600" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            ¿Eliminar tu plan de salud?
          </h3>
          <p className="text-sm text-gray-700">
            Esta acción eliminará permanentemente tu plan actual y toda la información asociada. 
            Podrás crear un nuevo plan después.
          </p>
        </div>
      </div>
      
      <div className="flex gap-3">
        <button
          onClick={handleDelete}
          disabled={isDeleting}
          className="px-4 py-2 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isDeleting ? "Eliminando..." : "Sí, eliminar"}
        </button>
        <button
          onClick={() => setShowConfirm(false)}
          disabled={isDeleting}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Cancelar
        </button>
      </div>
    </div>
  );
}

