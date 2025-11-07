import Link from "next/link";
import { requireUser } from "@/lib/auth-helpers";
import { createClient } from "@/lib/supabase/server";
import { formatDate, getRiskLabel, getRiskDescription, getImpactLevel, getImpactColor } from "@/lib/utils";
import type { RiskLevel } from "@/lib/utils";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";
import { CoachChatSection } from "./CoachChatSection";
import { DeletePlanSection } from "./DeletePlanSection";
import {
  Activity,
  ClipboardList,
  HeartPulse,
  AlertTriangle,
  Bot,
} from "lucide-react";

export const runtime = "edge";

interface CoachPageProps {
  searchParams: Promise<{
    assessment?: string;
  }>;
}

export default async function CoachPage({ searchParams }: CoachPageProps) {
  const session = await requireUser();
  const supabase = await createClient();

  const params = await searchParams;
  const assessmentId = params?.assessment;

  let query = supabase
    .from("assessments")
    .select(
      "id, created_at, risk_score, risk_level, drivers, assessment_data"
    )
    .eq("user_id", session.user.id)
    .order("created_at", { ascending: false });

  if (assessmentId) {
    query = query.eq("id", assessmentId);
  }

  const { data, error } = await query.limit(1);

  if (error) {
    console.error("Error loading assessment:", error);
    throw new Error("No se pudo cargar la última evaluación.");
  }

  const assessment = data?.[0];

  if (!assessment) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 text-blue-600 mb-6">
          <Bot className="h-8 w-8" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Aún no tienes un plan generado
        </h1>
        <p className="text-gray-600 mb-6">
          Inicia una conversación con el asistente IA para analizar tus datos y construir un plan de acción personalizado.
        </p>
        <Link
          href="/chat"
          className="inline-flex items-center gap-2 bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700 transition-colors"
        >
          Iniciar evaluación →
        </Link>
      </div>
    );
  }

  const riskLevel = (assessment.risk_level ?? "low") as RiskLevel;
  const rawAssessmentData = (assessment.assessment_data ?? {}) as Record<string, unknown>;
  
  // Extract profile data - assessment_data is now properly structured
  const profile = rawAssessmentData;
  const modelUsed = ((rawAssessmentData.model_used ?? rawAssessmentData.modelo ?? "diabetes") as string);

  // Drivers come from either the new structure or the old flat structure
  const drivers = Array.isArray(assessment.drivers) 
    ? assessment.drivers 
    : (Array.isArray(rawAssessmentData.drivers) ? rawAssessmentData.drivers : []);

  const planText: string = typeof rawAssessmentData.plan_text === "string"
    ? rawAssessmentData.plan_text
    : "Aún no se ha generado un plan para esta evaluación.";

  const citations: string[] = Array.isArray(rawAssessmentData.citations)
    ? (rawAssessmentData.citations as string[])
    : [];

  const riskPillClasses =
    riskLevel === "low"
      ? "text-green-600 bg-green-50 border-green-200"
      : riskLevel === "moderate"
      ? "text-yellow-600 bg-yellow-50 border-yellow-200"
      : "text-red-600 bg-red-50 border-red-200";

  // Format activity level for display
  const formatActivityLevel = (activity: unknown): string => {
    if (!activity) return "—";
    const activityMap: Record<string, string> = {
      "sedentario": "0-1 días/semana",
      "ligero": "2-3 días/semana",
      "moderado": "4-5 días/semana",
      "activo": "6 días/semana",
      "muy_activo": "7 días/semana"
    };
    return activityMap[String(activity).toLowerCase()] ?? String(activity);
  };

  // Format smoking for display
  const formatSmoking = (smoking: unknown): string => {
    if (smoking === null || smoking === undefined) return "—";
    if (typeof smoking === "boolean") {
      return smoking ? "Sí (fumador activo)" : "No";
    }
    return String(smoking);
  };

  return (
    <div className="bg-linear-to-br from-blue-50 via-white to-indigo-50 min-h-screen">
      <header className="bg-linear-to-r from-blue-600 via-indigo-600 to-purple-600 text-white shadow-lg">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <div className="bg-white/20 backdrop-blur-sm rounded-full p-3">
                <HeartPulse className="h-8 w-8 text-white" />
              </div>
              <div>
                <p className="text-sm uppercase tracking-wide text-blue-100">
                  Plan personalizado
                </p>
                <h1 className="text-4xl font-bold">
                  Coach de Salud CardioSense
                </h1>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-4 text-sm text-blue-100">
              <span className="inline-flex items-center gap-2 bg-white/10 px-3 py-1 rounded-full">
                <ClipboardList className="h-4 w-4" />
                Modelo: {modelUsed === "cardiovascular" ? "Cardiovascular" : "Diabetes"}
              </span>
              <span className="inline-flex items-center gap-2 bg-white/10 px-3 py-1 rounded-full">
                <Activity className="h-4 w-4" />
                Última actualización: {formatDate(assessment.created_at)}
              </span>
              <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border ${riskPillClasses}`}>
                <span className="font-semibold">{getRiskLabel(riskLevel)}</span>
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
        <section className="bg-white border border-blue-100 rounded-3xl shadow-sm p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Tu Perfil de Salud</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Medidas Corporales</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Altura</span>
                  <span className="text-sm font-medium text-gray-900">{profile.altura_cm ? `${Number(profile.altura_cm).toFixed(0)} cm` : "—"}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Peso</span>
                  <span className="text-sm font-medium text-gray-900">{profile.peso_kg ? `${Number(profile.peso_kg).toFixed(1)} kg` : "—"}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Circunferencia de cintura</span>
                  <span className="text-sm font-medium text-gray-900">{profile.circunferencia_cintura ? `${Number(profile.circunferencia_cintura).toFixed(0)} cm` : "—"}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">IMC</span>
                  <span className="text-sm font-medium text-gray-900">{profile.imc ? `${Number(profile.imc).toFixed(1)} (${Number(profile.imc) >= 30 ? "Obesidad" : Number(profile.imc) >= 25 ? "Sobrepeso" : "Normal"})` : "—"}</span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Estilo de Vida</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Horas de sueño</span>
                  <span className="text-sm font-medium text-gray-900">{profile.horas_sueno ? `${Number(profile.horas_sueno).toFixed(1)} horas/día` : "—"}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Tabaquismo</span>
                  <span className="text-sm font-medium text-gray-900">{formatSmoking(profile.tabaquismo) || "—"}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Actividad física</span>
                  <span className="text-sm font-medium text-gray-900">{formatActivityLevel(profile.actividad_fisica) || "—"}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Frutas y verduras</span>
                  <span className="text-sm font-medium text-gray-900">—</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-linear-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-200">
            <div className="flex items-start gap-4">
              <div className="shrink-0 mt-1">
                <div className={`w-3 h-3 rounded-full ${riskLevel === "low" ? "bg-green-500" : riskLevel === "moderate" ? "bg-yellow-500" : "bg-red-500"}`}></div>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Evaluación de Riesgo</h3>
                <p className="text-gray-700 mb-3">
                  {getRiskDescription(riskLevel)}
                </p>
                <div className="flex items-center gap-4">
                  <span className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border font-semibold ${riskPillClasses}`}>
                    {getRiskLabel(riskLevel)}
                  </span>
                  <span className="text-sm text-gray-600">
                    Modelo: {modelUsed === "cardiovascular" ? "Cardiovascular" : "Diabetes"}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {drivers.length > 0 && (
          <section className="bg-white border border-gray-200 rounded-3xl shadow-sm p-8">
            <div className="flex items-start gap-3 mb-6">
              <div className="bg-red-100 text-red-600 rounded-full p-2">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Factores que Influyen en tu Riesgo</h3>
                <p className="text-gray-600 text-sm mt-1">
                  Estos son los principales factores que contribuyen a tu puntuación de riesgo:
                </p>
              </div>
            </div>
            
            <div className="space-y-4">
              {drivers.slice(0, 5).map((driver: string | Record<string, unknown>, index: number) => {
                const isString = typeof driver === "string";
                const driverObj = isString ? null : driver as Record<string, unknown>;
                const feature = isString ? driver : String(driverObj?.feature || "");
                const description = isString ? driver : String(driverObj?.description || feature || "Factor desconocido");
                const rawShapValue = isString ? null : (driverObj?.shap_value ?? driverObj?.contribution);
                const shapValue = typeof rawShapValue === "number" ? rawShapValue : null;
                const impact = isString ? null : (driverObj?.impact || (shapValue && shapValue > 0 ? "aumenta" : "reduce"));
                
                // Get impact level using our utility function
                const impactLevel = getImpactLevel(shapValue);
                const impactColor = getImpactColor(impactLevel);
                
                return (
                  <div key={`${feature}-${index}`} className="bg-linear-to-r from-red-50 to-pink-50 border-l-4 border-red-400 rounded-lg p-5">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-base font-bold text-gray-900">{description}</span>
                          {impact && (
                            <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${
                              impact === "aumenta" 
                                ? "bg-red-100 text-red-700" 
                                : "bg-green-100 text-green-700"
                            }`}>
                              {impact === "aumenta" ? "↑ Aumenta" : "↓ Reduce"}
                            </span>
                          )}
                        </div>
                        
                        <p className="text-xs text-gray-600">
                          {impact === "aumenta" 
                            ? "Este factor contribuye a tu riesgo. Mejorar este indicador puede ayudarte." 
                            : "Este factor está reduciendo tu riesgo. Mantén este buen indicador."}
                        </p>
                      </div>
                      
                      <div className="shrink-0 text-right">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium border ${impactColor}`}>
                          Impacto {impactLevel}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        <section className="bg-white border border-gray-200 rounded-3xl shadow-sm p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-red-100 text-red-600 rounded-full p-2">
              <ClipboardList className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-gray-900">
                Plan de acción recomendado (2 semanas)
              </h3>
              <p className="text-gray-600 text-sm">
                Adaptado a tu perfil y respaldado por la base de conocimiento clínica utilizada en el hackathon.
              </p>
            </div>
          </div>

          <MarkdownRenderer content={planText} />

          {citations.length > 0 && (
            <div className="mt-6 border-t border-gray-200 pt-4">
              <p className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-gray-500" />
                Fuentes utilizadas
              </p>
              <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                {citations.map((citation, idx) => (
                  <li key={idx}>{citation}</li>
                ))}
              </ul>
            </div>
          )}
        </section>

        <CoachChatSection assessmentId={assessment.id} />

        <DeletePlanSection assessmentId={assessment.id} />

        <section className="bg-linear-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-3xl shadow-sm p-8">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 text-green-600 mb-4">
              <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Tu Evaluación está Completa</h3>
            <p className="text-gray-600 text-sm max-w-2xl mx-auto">
              Has completado tu evaluación de salud CardioSense. Este plan personalizado está basado en tus datos y la evidencia clínica más reciente.
            </p>
            <p className="text-gray-500 text-xs mt-4">
              💡 <strong>Recuerda:</strong> Este sistema es educativo y no reemplaza el consejo médico profesional. Consulta con un profesional de la salud para una evaluación completa.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}

