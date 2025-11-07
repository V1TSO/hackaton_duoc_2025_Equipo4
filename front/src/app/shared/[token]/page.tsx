import { createClient } from "@/lib/supabase/server";
import { notFound } from "next/navigation";
import {
  RiskGauge,
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
import { AlertTriangle, TrendingUp, Heart } from "lucide-react";
import Link from "next/link";

export const runtime = "edge";

export default async function SharedResultsPage({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const { token } = await params;
  const supabase = await createClient();

  const { data: assessment, error } = await supabase
    .from("assessments")
    .select("*")
    .eq("share_token", token)
    .single();

  if (error || !assessment || !assessment.share_token) {
    notFound();
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
    <div className="min-h-screen bg-gray-50">
      <div className="bg-gradient-to-r from-red-600 to-pink-600 text-white px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center gap-3 mb-4">
            <Heart className="h-10 w-10" />
            <h1 className="text-3xl font-bold">CardioSense</h1>
          </div>
          <p className="text-red-100">
            Resultados compartidos de evaluación de riesgo cardiometabólico
          </p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Resultados de Evaluación
          </h2>
          <p className="text-gray-600 mb-8">
            {new Date(assessment.created_at).toLocaleDateString("es-CL", {
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </p>

          <div className="flex flex-col lg:flex-row gap-8 mb-8">
            <div className="flex-1 flex justify-center">
              <RiskGauge score={assessment.risk_score} size="lg" />
            </div>

            <div className="flex-1 space-y-6">
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  Puntuación de Riesgo
                </h3>
                <p className="text-gray-700 leading-relaxed">
                  {riskDescription}
                </p>
              </div>

              {needsDoctor && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="h-6 w-6 text-red-600 flex-shrink-0" />
                    <div>
                      <h4 className="font-semibold text-red-900 mb-1">
                        Recomendación Importante
                      </h4>
                      <p className="text-sm text-red-800">
                        Se recomienda consultar con un profesional de la salud
                        para una evaluación completa y personalizada.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8 mb-8">
          <h3 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
            <TrendingUp className="h-6 w-6 text-red-600" />
            Factores que Influyen en el Riesgo
          </h3>

          <div className="space-y-4">
            {drivers.slice(0, 5).map((driver, index) => {
              const contribution = driver.contribution ?? 0;
              const isNegative = contribution < 0;
              const impactLevel = getImpactLevel(Math.abs(contribution));
              const impactColor = getImpactColor(impactLevel);

              return (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      {driver.description || driver.feature || "Factor desconocido"}
                    </h4>
                    <p className="text-sm text-gray-600">
                      {isNegative 
                        ? "Este factor está ayudando a reducir el riesgo" 
                        : "Este factor está aumentando el riesgo"}
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
          <h3 className="text-2xl font-semibold text-gray-900 mb-6">
            Perfil de Salud
          </h3>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-900 mb-3">
                Medidas Corporales
              </h4>
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
              <h4 className="font-semibold text-gray-900 mb-3">
                Estilo de Vida
              </h4>
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

        <PermanentDisclaimer />

        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-8 mt-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              ¿Quieres conocer tu propio riesgo?
            </h3>
            <p className="text-gray-700 mb-6 max-w-2xl mx-auto">
              Crea tu cuenta gratuita en CardioSense y obtén tu evaluación
              personalizada de riesgo cardiometabólico con recomendaciones del
              Coach IA.
            </p>
            <div className="flex gap-4 justify-center">
              <Link
                href="/register"
                className="inline-flex items-center gap-2 bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700 transition-colors"
              >
                Crear Cuenta Gratis
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 border-2 border-red-600 text-red-600 px-6 py-3 rounded-lg font-semibold hover:bg-red-50 transition-colors"
              >
                Iniciar Sesión
              </Link>
            </div>
          </div>
        </div>
      </div>
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

