import Link from "next/link";
import { requireUser } from "@/lib/auth-helpers";
import { createClient } from "@/lib/supabase/server";
import {
  Activity,
  TrendingUp,
  Calendar,
  ArrowRight,
  AlertCircle,
} from "lucide-react";
import { PermanentDisclaimer } from "@/components";

export const runtime = "edge";

export default async function AppDashboardPage() {
  const session = await requireUser();
  const supabase = await createClient();

  const { data: assessments } = await supabase
    .from("assessments")
    .select("*")
    .eq("user_id", session.user.id)
    .order("created_at", { ascending: false })
    .limit(1);

  const latestAssessment = assessments?.[0];

  const { count: totalAssessments } = await supabase
    .from("assessments")
    .select("*", { count: "exact", head: true })
    .eq("user_id", session.user.id);

  const { data: activePlan } = await supabase
    .from("action_plans")
    .select("*")
    .eq("user_id", session.user.id)
    .gte("end_date", new Date().toISOString().split("T")[0])
    .order("created_at", { ascending: false })
    .limit(1)
    .single();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Bienvenido a CardioSense
        </h1>
        <p className="text-gray-600">
          Panel de control de tu salud cardiometabólica
        </p>
      </header>

      <div className="grid gap-6 md:grid-cols-3 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-red-100 p-3 rounded-lg">
              <Activity className="h-6 w-6 text-red-600" />
            </div>
          </div>
          <h3 className="text-sm font-medium text-gray-600 mb-1">
            Evaluaciones
          </h3>
          <p className="text-3xl font-bold text-gray-900">
            {totalAssessments || 0}
          </p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-blue-100 p-3 rounded-lg">
              <TrendingUp className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <h3 className="text-sm font-medium text-gray-600 mb-1">
            Último riesgo
          </h3>
          <p className="text-3xl font-bold text-gray-900">
            {latestAssessment
              ? `${Math.round(latestAssessment.risk_score * 100)}`
              : "no disponible"}
          </p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-green-100 p-3 rounded-lg">
              <Calendar className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <h3 className="text-sm font-medium text-gray-600 mb-1">
            Plan activo
          </h3>
          <p className="text-3xl font-bold text-gray-900">
            {activePlan ? "Sí" : "No"}
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Conversa con el asistente IA
          </h2>
          <p className="text-gray-600 mb-6">
            Explora tu riesgo cardiometabólico respondiendo preguntas guiadas en
            una experiencia conversacional cuidada.
          </p>
          <Link
            href="/chat"
            className="inline-flex items-center gap-2 bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700 transition-colors"
          >
            Iniciar Conversación
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Habla con el Coach IA
          </h2>
          <p className="text-gray-600 mb-6">
            Obtén recomendaciones personalizadas y respuestas a tus preguntas
            sobre salud cardiovascular.
          </p>
          <Link
            href="/coach"
            className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Abrir Coach
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </div>

      {latestAssessment && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Tu última evaluación
          </h2>
            <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">
                Riesgo: {latestAssessment.risk_level === "low" && "Bajo"}
                {latestAssessment.risk_level === "moderate" && "Moderado"}
                {latestAssessment.risk_level === "high" && "Alto"}
              </p>
              <p className="text-sm text-gray-500">
                {new Date(latestAssessment.created_at).toLocaleDateString(
                  "es-CL",
                  {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  }
                )}
              </p>
            </div>
            <Link
              href={`/results/${latestAssessment.id}`}
              className="text-red-600 hover:text-red-700 font-semibold"
        >
              Ver detalles →
        </Link>
          </div>
        </div>
      )}

      <PermanentDisclaimer />

      {!latestAssessment && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 mt-8">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-6 w-6 text-yellow-600 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-yellow-900 mb-1">
                Primera vez en CardioSense
              </h3>
              <p className="text-sm text-yellow-800">
                Realiza tu primera evaluación para comenzar a monitorear tu
                salud cardiometabólica y recibir recomendaciones personalizadas.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

