import Link from "next/link";
import ReactMarkdown from "react-markdown";
import { requireUser } from "@/lib/auth-helpers";
import { createClient } from "@/lib/supabase/server";
import { formatDate, getRiskLabel, getRiskDescription } from "@/lib/utils";
import type { RiskLevel } from "@/lib/utils";
import {
  Activity,
  ClipboardList,
  HeartPulse,
  AlertTriangle,
  ArrowRight,
  Bot,
} from "lucide-react";

export const runtime = "edge";

interface CoachPageProps {
  searchParams?: {
    assessment?: string;
  };
}

export default async function CoachPage({ searchParams }: CoachPageProps) {
  const session = await requireUser();
  const supabase = await createClient();

  const assessmentId = searchParams?.assessment;

  let query = supabase
    .from("assessments")
    .select(
      "id, created_at, risk_score, risk_level, drivers, model_used, assessment_data"
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
          Iniciar conversación
          <ArrowRight className="h-5 w-5" />
        </Link>
      </div>
    );
  }

  const riskLevel = (assessment.risk_level ?? "low") as RiskLevel;
  const riskScore = assessment.risk_score ?? 0;
  const baseDrivers: string[] = Array.isArray(assessment.drivers) ? assessment.drivers : [];
  const profile = (assessment.assessment_data ?? {}) as Record<string, unknown>;
  const modelUsed = (assessment.model_used ?? profile.modelo ?? "diabetes") as string;

  const drivers: string[] = Array.isArray(profile.drivers)
    ? (profile.drivers as string[])
    : baseDrivers;

  const planText: string = typeof profile.plan_text === "string"
    ? profile.plan_text
    : "Aún no se ha generado un plan para esta evaluación.";

  const citations: string[] = Array.isArray(profile.citations)
    ? (profile.citations as string[])
    : [];

  const riskPillClasses =
    riskLevel === "low"
      ? "text-green-600 bg-green-50 border-green-200"
      : riskLevel === "moderate"
      ? "text-yellow-600 bg-yellow-50 border-yellow-200"
      : "text-red-600 bg-red-50 border-red-200";

  const profileHighlights = [
    { label: "Edad", value: profile.edad ? `${profile.edad} años` : "—" },
    { label: "Sexo", value: profile.genero === "M" ? "Masculino" : profile.genero === "F" ? "Femenino" : "—" },
    { label: "IMC", value: profile.imc ? Number(profile.imc).toFixed(1) : "—" },
    { label: "Cintura", value: profile.circunferencia_cintura ? `${profile.circunferencia_cintura} cm` : "—" },
    { label: "Presión sistólica", value: profile.presion_sistolica ? `${profile.presion_sistolica} mmHg` : "—" },
    { label: "Sueño", value: profile.horas_sueno ? `${profile.horas_sueno} h` : "—" },
  ];

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
                <span className="text-sm">{Math.round(riskScore * 100)}%</span>
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
        <section className="bg-white border border-blue-100 rounded-3xl shadow-sm p-8">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
            <div className="flex-1">
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">Resumen de Riesgo</h2>
              <p className="text-gray-600 max-w-2xl">
                {getRiskDescription(riskLevel)}
              </p>
            </div>
            <div className="grid grid-cols-2 gap-3 w-full md:w-72">
              {profileHighlights.map((item) => (
                <div key={item.label} className="bg-blue-50 border border-blue-100 rounded-xl px-3 py-2 text-left">
                  <p className="text-xs uppercase tracking-wide text-blue-500 font-semibold">
                    {item.label}
                  </p>
                  <p className="text-sm font-medium text-gray-800">{item.value}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {drivers.length > 0 && (
          <section className="bg-white border border-gray-200 rounded-3xl shadow-sm p-8">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Principales impulsores</h3>
            <p className="text-gray-600 mb-6">
              Factores que el modelo identificó como los principales contribuyentes a tu riesgo actual.
            </p>
            <div className="grid md:grid-cols-2 gap-4">
              {drivers.slice(0, 4).map((driver, index) => (
                <div key={`${driver}-${index}`} className="border border-gray-200 rounded-2xl p-4 bg-gray-50">
                  <p className="text-sm font-semibold text-gray-900">{driver}</p>
                  <p className="text-xs text-gray-500 mt-1">Impacto relevante en la estimación del riesgo.</p>
                </div>
              ))}
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

          <div className="prose prose-sm max-w-none text-gray-800">
            <ReactMarkdown>{planText}</ReactMarkdown>
          </div>

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

        <section className="bg-white border border-blue-100 rounded-3xl shadow-sm p-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">¿Quieres refinar tu plan?</h3>
            <p className="text-gray-600 text-sm">
              Regresa a la conversación para actualizar tus datos o resolver dudas con el asistente IA.
            </p>
          </div>
          <div className="flex gap-3">
            <Link
              href="/chat"
              className="inline-flex items-center gap-2 px-5 py-3 rounded-lg font-semibold text-white bg-red-600 hover:bg-red-700 transition-colors"
            >
              Continuar conversación
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              href="/history"
              className="inline-flex items-center gap-2 px-5 py-3 rounded-lg font-semibold text-red-600 border border-red-200 hover:bg-red-50 transition-colors"
            >
              Ver historial
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}

