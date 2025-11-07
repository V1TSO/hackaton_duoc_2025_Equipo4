import { AssessmentData } from "@/lib/types";
import { Check, Circle } from "lucide-react";

interface DataExtractionCardProps {
  extractedData: Partial<AssessmentData>;
}

interface FieldInfo {
  key: keyof AssessmentData;
  label: string;
  unit?: string;
  category: "anthropometry" | "lifestyle" | "diet";
}

const FIELD_CONFIG: FieldInfo[] = [
  { key: "age", label: "Edad", unit: "años", category: "anthropometry" },
  { key: "sex", label: "Sexo", category: "anthropometry" },
  { key: "height_cm", label: "Altura", unit: "cm", category: "anthropometry" },
  { key: "weight_kg", label: "Peso", unit: "kg", category: "anthropometry" },
  { key: "waist_cm", label: "Circunferencia de cintura", unit: "cm", category: "anthropometry" },
  { key: "sleep_hours", label: "Horas de sueño", unit: "h", category: "lifestyle" },
  { key: "smokes_cig_day", label: "Cigarrillos por día", category: "lifestyle" },
  { key: "days_mvpa_week", label: "Días de actividad física", unit: "días", category: "lifestyle" },
  { key: "fruit_veg_portions_day", label: "Porciones de frutas/verduras", unit: "por día", category: "diet" },
];

const CATEGORY_CONFIG = {
  anthropometry: { label: "Antropometría", color: "blue" },
  lifestyle: { label: "Estilo de Vida", color: "green" },
  diet: { label: "Alimentación", color: "lime" },
};

export function DataExtractionCard({ extractedData }: DataExtractionCardProps) {
  const collectedFields = FIELD_CONFIG.filter(
    (field) => extractedData[field.key] !== undefined && extractedData[field.key] !== null
  );
  const totalFields = FIELD_CONFIG.length;
  const collectedCount = collectedFields.length;
  const progressPercent = Math.round((collectedCount / totalFields) * 100);

  const fieldsByCategory = FIELD_CONFIG.reduce((acc, field) => {
    if (!acc[field.category]) acc[field.category] = [];
    acc[field.category].push(field);
    return acc;
  }, {} as Record<string, FieldInfo[]>);

  const formatValue = (field: FieldInfo, value: unknown) => {
    if (field.key === "sex") {
      return value === "M" ? "Masculino" : "Femenino";
    }
    return `${value}${field.unit ? ` ${field.unit}` : ""}`;
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border-2 border-gray-100 p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">Datos Recopilados</h3>
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-gray-600">
            {collectedCount}/{totalFields} campos
          </span>
          <span className="text-lg font-bold text-blue-600">{progressPercent}%</span>
        </div>
      </div>

      <div className="relative w-full bg-gray-200 rounded-full h-3 overflow-hidden mb-6">
        <div
          className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-600 to-indigo-600 transition-all duration-500 ease-out rounded-full"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {Object.entries(fieldsByCategory).map(([category, fields]) => {
        const categoryConfig = CATEGORY_CONFIG[category as keyof typeof CATEGORY_CONFIG];
        
        const getCategoryClasses = (category: string) => {
          switch (category) {
            case "anthropometry":
              return {
                header: "text-blue-700",
                bg: "bg-blue-50",
                border: "border-blue-200",
                icon: "bg-blue-600",
                text: "text-blue-700",
              };
            case "lifestyle":
              return {
                header: "text-green-700",
                bg: "bg-green-50",
                border: "border-green-200",
                icon: "bg-green-600",
                text: "text-green-700",
              };
            case "diet":
              return {
                header: "text-lime-700",
                bg: "bg-lime-50",
                border: "border-lime-200",
                icon: "bg-lime-600",
                text: "text-lime-700",
              };
            default:
              return {
                header: "text-gray-700",
                bg: "bg-gray-50",
                border: "border-gray-200",
                icon: "bg-gray-600",
                text: "text-gray-700",
              };
          }
        };

        const classes = getCategoryClasses(category);

        return (
          <div key={category} className="mb-4 last:mb-0">
            <h4 className={`text-sm font-bold ${classes.header} mb-2 uppercase tracking-wide`}>
              {categoryConfig.label}
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {fields.map((field) => {
                const isCollected = extractedData[field.key] !== undefined && extractedData[field.key] !== null;
                const value = extractedData[field.key];

                return (
                  <div
                    key={field.key}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg border-2 transition-all ${
                      isCollected
                        ? `${classes.bg} ${classes.border}`
                        : "bg-gray-50 border-gray-200"
                    }`}
                  >
                    <div className="flex-shrink-0">
                      {isCollected ? (
                        <div className={`w-6 h-6 ${classes.icon} rounded-full flex items-center justify-center`}>
                          <Check className="h-4 w-4 text-white" />
                        </div>
                      ) : (
                        <Circle className="h-6 w-6 text-gray-300" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-semibold ${isCollected ? "text-gray-900" : "text-gray-400"}`}>
                        {field.label}
                      </p>
                      {isCollected && (
                        <p className={`text-sm font-bold ${classes.text}`}>
                          {formatValue(field, value)}
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

