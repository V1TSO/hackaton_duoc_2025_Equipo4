import { requireUser } from "@/lib/auth-helpers";
import { createClient } from "@/lib/supabase/server";
import { notFound, redirect } from "next/navigation";
import {
  RiskGauge,
  ShareButton,
  PermanentDisclaimer,
} from "@/components";
import {
  getRiskDescription,
  shouldRecommendDoctor,
  formatBMI,
  getBMICategory,
  getImpactLevel,
  getImpactColor,
} from "@/lib/utils";
import { AlertTriangle, TrendingUp, ArrowRight, MessageSquare, Calendar } from "lucide-react";
import Link from "next/link";

export const runtime = "edge";

export default async function ResultsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const session = await requireUser();
  const supabase = await createClient();

  const { data: assessment, error } = await supabase
    .from("assessments")
    .select("*")
    .eq("id", id)
    .single();

  if (error || !assessment) {
    notFound();
  }

  if (assessment.user_id !== session.user.id) {
    redirect("/app");
  }

  const riskDescription = getRiskDescription(assessment.risk_level);
  const needsDoctor = shouldRecommendDoctor(assessment.risk_score ?? 0);
  const assessmentData = (assessment.assessment_data ?? {}) as {
    age?: number;
    sex?: string;
    height_cm?: number;
    weight_kg?: number;
    waist_cm?: number;
    sleep_hours?: number;
    smokes_cig_day?: number;
    days_mvpa_week?: number;
    fruit_veg_portions_day?: number;
  };
  const drivers = (assessment.drivers ?? []) as Array<{
    feature: string;
    value?: number;
    contribution?: number;
    description?: string;
  }>;

  const bmi = formatBMI(assessmentData.weight_kg ?? 0, assessmentData.height_cm ?? 0);
  const bmiCategory = getBMICategory(
    assessmentData.weight_kg ?? 0,
    assessmentData.height_cm ?? 0
  );

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8 mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Resultados de tu Evaluación
        </h1>
        <p className="text-gray-600 mb-8">
          {new Date(assessment.created_at).toLocaleDateString("es-CL", {
            year: "numeric",
            month: "long",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>

        <div className="flex flex-col lg:flex-row gap-8 mb-8">
          <div className="flex-1 flex justify-center">
            <RiskGauge score={assessment.risk_score} size="lg" />
          </div>

          <div className="flex-1 space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">
                Tu Puntuación de Riesgo
              </h2>
              <p className="text-gray-700 leading-relaxed">
                {riskDescription}
              </p>
            </div>

            {needsDoctor && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="h-6 w-6 text-red-600 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-red-900 mb-1">
                      Recomendación Importante
                    </h3>
                    <p className="text-sm text-red-800">
                      Te recomendamos consultar con un profesional de la salud
                      para una evaluación completa y personalizada.
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div className="flex flex-wrap gap-3">
              <Link
                href={`/coach?assessment=${id}`}
                className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                <MessageSquare className="h-5 w-5" />
                Hablar con el Coach
              </Link>
              <ShareButton
                assessmentId={id}
                existingToken={assessment.share_token}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8 mb-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
          <TrendingUp className="h-6 w-6 text-red-600" />
          Factores que Influyen en tu Riesgo
        </h2>
        <p className="text-gray-600 mb-6">
          Estos son los principales factores que contribuyen a tu puntuación de
          riesgo:
        </p>

        <div className="space-y-4">
          {drivers.slice(0, 5).map((driver, index) => {
            const contribution = driver.contribution ?? 0;
            const isNegative = contribution < 0;
            const impactLevel = getImpactLevel(Math.abs(contribution));
            const impactColor = getImpactColor(impactLevel);

            return (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900 mb-1">
                    {driver.description || driver.feature || "Factor desconocido"}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {isNegative 
                      ? "Este factor está ayudando a reducir tu riesgo" 
                      : "Este factor está aumentando tu riesgo"}
                  </p>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <span className={`text-lg ${isNegative ? "text-green-600" : "text-red-600"}`}>
                    {isNegative ? "↓" : "↑"}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium border ${impactColor}`}>
                    Impacto {impactLevel}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8 mb-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">
          Tu Perfil de Salud
        </h2>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h3 className="font-semibold text-gray-900 mb-3">
              Medidas Corporales
            </h3>
            <div className="space-y-3">
              <InfoRow
                label="Altura"
                value={assessmentData.height_cm ? `${assessmentData.height_cm} cm` : "—"}
              />
              <InfoRow 
                label="Peso" 
                value={assessmentData.weight_kg ? `${assessmentData.weight_kg} kg` : "—"} 
              />
              <InfoRow
                label="Circunferencia de cintura"
                value={assessmentData.waist_cm ? `${assessmentData.waist_cm} cm` : "—"}
              />
              <InfoRow label="IMC" value={bmi !== "—" ? `${bmi} (${bmiCategory})` : "—"} />
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="font-semibold text-gray-900 mb-3">
              Estilo de Vida
            </h3>
            <div className="space-y-3">
              <InfoRow
                label="Horas de sueño"
                value={assessmentData.sleep_hours ? `${assessmentData.sleep_hours} horas/día` : "—"}
              />
              <InfoRow
                label="Tabaquismo"
                value={
                  assessmentData.smokes_cig_day !== undefined && assessmentData.smokes_cig_day !== null
                    ? assessmentData.smokes_cig_day === 0
                      ? "No fuma"
                      : `${assessmentData.smokes_cig_day} cigarrillos/día`
                    : "—"
                }
              />
              <InfoRow
                label="Actividad física"
                value={assessmentData.days_mvpa_week !== undefined && assessmentData.days_mvpa_week !== null ? `${assessmentData.days_mvpa_week} días/semana` : "—"}
              />
              <InfoRow
                label="Frutas y verduras"
                value={assessmentData.fruit_veg_portions_day !== undefined && assessmentData.fruit_veg_portions_day !== null ? `${assessmentData.fruit_veg_portions_day} porciones/día` : "—"}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-8 mb-8">
        <div className="flex items-start gap-4">
          <Calendar className="h-8 w-8 text-blue-600 flex-shrink-0" />
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              ¿Listo para Mejorar tu Salud?
            </h2>
            <p className="text-gray-700 mb-4">
              Obtén un plan personalizado de 2 semanas con recomendaciones
              específicas para reducir tu riesgo cardiometabólico.
            </p>
            <Link
              href={`/coach?assessment=${id}`}
              className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Crear Mi Plan
              <ArrowRight className="h-5 w-5" />
            </Link>
          </div>
        </div>
      </div>

      <PermanentDisclaimer />
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-gray-100">
      <span className="text-sm text-gray-600">{label}</span>
      <span className="text-sm font-medium text-gray-900">{value}</span>
    </div>
  );
}

