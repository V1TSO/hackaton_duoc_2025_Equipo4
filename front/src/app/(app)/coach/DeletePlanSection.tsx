"use client";

import { DeletePlanButton } from "@/components/DeletePlanButton";

interface DeletePlanSectionProps {
  assessmentId: string;
}

export function DeletePlanSection({ assessmentId }: DeletePlanSectionProps) {
  return (
    <section className="bg-white border border-gray-200 rounded-3xl shadow-sm p-8">
      <div className="max-w-2xl mx-auto">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Gestionar Plan
        </h3>
        <p className="text-gray-600 text-sm mb-6">
          Si deseas realizar una nueva evaluación, primero debes eliminar tu plan actual. 
          Esta acción es permanente y no se puede deshacer.
        </p>
        <DeletePlanButton assessmentId={assessmentId} />
      </div>
    </section>
  );
}

