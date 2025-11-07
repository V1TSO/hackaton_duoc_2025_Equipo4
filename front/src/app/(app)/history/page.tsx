import { requireUser } from "@/lib/auth-helpers";
import { createClient } from "@/lib/supabase/server";
import { getRiskLabel, getRiskColor, formatDate } from "@/lib/utils";
import { TrendingUp, Calendar, Activity } from "lucide-react";
import Link from "next/link";

export const runtime = "edge";

export default async function HistoryPage() {
  const session = await requireUser();
  const supabase = await createClient();

  const { data: assessments } = await supabase
    .from("assessments")
    .select("*")
    .eq("user_id", session.user.id)
    .order("created_at", { ascending: false });

  if (!assessments || assessments.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <Activity className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            No tienes evaluaciones previas
          </h1>
          <p className="text-gray-600 mb-6">
            Realiza tu primera evaluación para comenzar a monitorear tu salud
          </p>
          <Link
            href="/chat"
            className="inline-flex items-center gap-2 bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700 transition-colors"
          >
            Conversar con el Asistente
          </Link>
        </div>
      </div>
    );
  }

  const scores = assessments.map((a) => ({
    date: new Date(a.created_at),
    score: a.risk_score,
  }));

  const avgScore =
    scores.reduce((sum, s) => sum + s.score, 0) / scores.length;
  const latestScore = scores[0].score;
  const trend = latestScore < avgScore ? "mejorando" : "empeorando";

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Historial de Evaluaciones
        </h1>
        <p className="text-gray-600">
          Revisa tu progreso y tendencias de salud a lo largo del tiempo
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="bg-blue-100 p-2 rounded-lg">
              <Activity className="h-5 w-5 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900">Total</h3>
          </div>
          <p className="text-3xl font-bold text-blue-600">
            {assessments.length}
          </p>
          <p className="text-sm text-gray-600 mt-1">evaluaciones</p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="bg-purple-100 p-2 rounded-lg">
              <TrendingUp className="h-5 w-5 text-purple-600" />
            </div>
            <h3 className="font-semibold text-gray-900">Promedio</h3>
          </div>
          <p className="text-3xl font-bold text-purple-600">
            {Math.round(avgScore * 100)}
          </p>
          <p className="text-sm text-gray-600 mt-1">puntuación media</p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="bg-green-100 p-2 rounded-lg">
              <Calendar className="h-5 w-5 text-green-600" />
            </div>
            <h3 className="font-semibold text-gray-900">Tendencia</h3>
          </div>
          <p className="text-2xl font-bold text-green-600 capitalize">
            {trend === "mejorando" ? "↓ Mejorando" : "↑ Subiendo"}
          </p>
          <p className="text-sm text-gray-600 mt-1">vs. promedio</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Tendencia de Riesgo
        </h2>
        <div className="relative h-64">
          <div className="absolute inset-0 flex items-end justify-between gap-2">
            {scores.reverse().map((point, index) => {
              const height = point.score * 100;
              const color =
                point.score < 0.3
                  ? "bg-green-500"
                  : point.score < 0.6
                  ? "bg-yellow-500"
                  : "bg-red-500";

              return (
                <div
                  key={index}
                  className="flex-1 flex flex-col items-center"
                >
                  <div
                    className={`w-full ${color} rounded-t transition-all hover:opacity-80 cursor-pointer`}
                    style={{ height: `${height}%` }}
                    title={`${Math.round(point.score * 100)} - ${formatDate(
                      point.date.toISOString()
                    )}`}
                  />
                </div>
              );
            })}
          </div>
        </div>
        <div className="flex items-center justify-center gap-6 mt-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-500 rounded" />
            <span>Bajo</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-yellow-500 rounded" />
            <span>Moderado</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-500 rounded" />
            <span>Alto</span>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-gray-900">
          Evaluaciones Recientes
        </h2>
        {assessments.map((assessment) => {
          const riskLabel = getRiskLabel(assessment.risk_level);
          const riskColor = getRiskColor(assessment.risk_level);

          return (
            <Link
              key={assessment.id}
              href={`/results/${assessment.id}`}
              className="block bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`text-2xl font-bold ${riskColor}`}>
                      {Math.round(assessment.risk_score * 100)}
                    </span>
                    <span className={`font-semibold ${riskColor}`}>
                      {riskLabel}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">
                    {formatDate(assessment.created_at)}
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-red-600 font-semibold hover:text-red-700">
                    Ver detalles →
                  </span>
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      <div className="mt-8 text-center">
        <Link
          href="/chat"
          className="inline-flex items-center gap-2 bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700 transition-colors"
        >
          Iniciar Nueva Conversación
        </Link>
      </div>
    </div>
  );
}

