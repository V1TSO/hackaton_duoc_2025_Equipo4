export function formatDate(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return new Intl.DateTimeFormat("es-CL", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(d);
}

export function formatDateTime(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return new Intl.DateTimeFormat("es-CL", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(d);
}

export function formatShortDate(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return new Intl.DateTimeFormat("es-CL", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(d);
}

export function formatPercentage(value: number, decimals: number = 1): string {
  if (value === null || value === undefined || isNaN(value)) return "—";
  return `${(value * 100).toFixed(decimals)}%`;
}

export function formatNumber(value: number, decimals: number = 1): string {
  if (value === null || value === undefined || isNaN(value)) return "—";
  return value.toFixed(decimals);
}

export function formatBMI(weight: number, heightCm: number): string {
  if (
    weight === null || weight === undefined || isNaN(weight) ||
    heightCm === null || heightCm === undefined || isNaN(heightCm) ||
    heightCm <= 0 || weight <= 0
  ) {
    return "—";
  }
  const heightM = heightCm / 100;
  const bmi = weight / (heightM * heightM);
  if (isNaN(bmi)) return "—";
  return bmi.toFixed(1);
}

export function getBMICategory(weight: number, heightCm: number): string {
  if (
    weight === null || weight === undefined || isNaN(weight) ||
    heightCm === null || heightCm === undefined || isNaN(heightCm) ||
    heightCm <= 0 || weight <= 0
  ) {
    return "—";
  }
  const heightM = heightCm / 100;
  const bmi = weight / (heightM * heightM);
  if (isNaN(bmi)) return "—";

  if (bmi < 18.5) return "Bajo peso";
  if (bmi < 25) return "Normal";
  if (bmi < 30) return "Sobrepeso";
  return "Obesidad";
}

export function getImpactLevel(contribution: number | null | undefined): string {
  if (contribution === null || contribution === undefined || isNaN(contribution)) {
    return "Bajo";
  }
  const absValue = Math.abs(contribution);
  if (absValue >= 0.15) return "Alto";
  if (absValue >= 0.08) return "Moderado";
  return "Bajo";
}

export function getImpactColor(level: string): string {
  switch (level.toLowerCase()) {
    case "alto":
      return "bg-red-100 text-red-700 border-red-300";
    case "moderado":
      return "bg-yellow-100 text-yellow-700 border-yellow-300";
    case "bajo":
      return "bg-green-100 text-green-700 border-green-300";
    default:
      return "bg-gray-100 text-gray-700 border-gray-300";
  }
}

