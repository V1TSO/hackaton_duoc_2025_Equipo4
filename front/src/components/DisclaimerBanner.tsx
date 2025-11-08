"use client";

import { Shield, X } from "lucide-react";
import { useState, useEffect } from "react";

export function DisclaimerBanner() {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const dismissed = localStorage.getItem("disclaimer-dismissed");
    if (dismissed) {
      setIsVisible(false);
    }
  }, []);

  const handleDismiss = () => {
    localStorage.setItem("disclaimer-dismissed", "true");
    setIsVisible(false);
  };

  if (!isVisible) return null;

  return (
    <div className="bg-yellow-50 border-b border-yellow-200 px-4 py-3" role="alert" aria-live="polite">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-1">
          <Shield className="h-5 w-5 text-yellow-600 flex-shrink-0" aria-hidden="true" />
          <p className="text-sm text-yellow-800">
            <strong>Importante:</strong> CardioSense es una herramienta educativa.
            No reemplaza el diagnóstico médico profesional. Siempre consulta con tu médico.
          </p>
        </div>
        <button
          onClick={handleDismiss}
          className="text-yellow-600 hover:text-yellow-800 transition-colors"
          aria-label="Cerrar aviso de disclaimer"
        >
          <X className="h-5 w-5" aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}

export function PermanentDisclaimer() {
  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <div className="flex items-start gap-3">
        <Shield className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
        <div>
          <h4 className="font-semibold text-yellow-800 mb-1">
            Disclaimer Médico
          </h4>
          <p className="text-sm text-yellow-700 leading-relaxed">
            CardioSense utiliza algoritmos basados en datos NHANES para evaluar
            riesgo cardiometabólico. Esta herramienta es únicamente educativa y
            no constituye diagnóstico médico. Los resultados no deben ser
            interpretados como consejo médico profesional. Siempre consulta con
            un profesional de la salud calificado para evaluaciones y
            recomendaciones personalizadas.
          </p>
        </div>
      </div>
    </div>
  );
}

