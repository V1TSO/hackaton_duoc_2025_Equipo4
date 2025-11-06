"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Heart, Shield, ArrowLeft, Mail, Lock, User, Calendar } from "lucide-react";
import Link from "next/link";

export default function RegisterPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    const formData = new FormData(event.currentTarget);
    const email = (formData.get("email") as string)?.trim();
    const password = formData.get("password") as string;
    const confirmPassword = formData.get("confirmPassword") as string;
    const firstName = (formData.get("firstName") as string)?.trim();
    const lastName = (formData.get("lastName") as string)?.trim();
    const age = formData.get("age") as string;

    try {
      // Validaciones básicas
      if (password !== confirmPassword) {
        throw new Error("Las contraseñas no coinciden");
      }

      if (password.length < 6) {
        throw new Error("La contraseña debe tener al menos 6 caracteres");
      }

      if (!firstName || !lastName) {
        throw new Error("Nombre y apellido son requeridos");
      }

      if (!age || parseInt(age) < 18 || parseInt(age) > 120) {
        throw new Error("Edad debe estar entre 18 y 120 años");
      }

      // Simular creación de cuenta
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setSuccess(true);
      
      // Redirigir al login después de 2 segundos
      setTimeout(() => {
        router.push("/login?message=Cuenta creada exitosamente");
      }, 2000);

    } catch (err) {
      setError(err instanceof Error ? err.message : "Error inesperado");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50 flex items-center justify-center px-6">
        <div className="text-center">
          <div className="bg-white rounded-2xl p-8 shadow-xl max-w-md mx-auto">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Heart className="h-8 w-8 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">¡Cuenta Creada!</h2>
            <p className="text-gray-600 mb-6">
              Tu cuenta en CardioSense ha sido creada exitosamente. 
              Te estamos redirigiendo al login...
            </p>
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-50">
      <div className="flex min-h-screen items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          {/* Botón de regreso */}
          <Link 
            href="/" 
            className="inline-flex items-center text-sm text-gray-600 hover:text-red-600 mb-8 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver al inicio
          </Link>

          {/* Card de Registro */}
          <div className="rounded-2xl border border-white/20 bg-white/80 backdrop-blur-sm p-8 shadow-xl">
            {/* Header */}
            <div className="text-center mb-8">
              <div className="flex items-center justify-center mb-4">
                <Heart className="h-10 w-10 text-red-500 mr-3" />
                <h1 className="text-2xl font-bold text-gray-900">CardioSense</h1>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Crear Cuenta
              </h2>
              <p className="text-sm text-gray-600">
                Únete a CardioSense y comienza a cuidar tu salud cardiovascular
              </p>
            </div>

            {/* Formulario */}
            <form className="space-y-4" onSubmit={handleSubmit}>
              {/* Nombre y Apellido */}
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700" htmlFor="firstName">
                    Nombre
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <input
                      id="firstName"
                      name="firstName"
                      type="text"
                      required
                      className="w-full pl-10 pr-3 py-2.5 rounded-lg border border-gray-300 bg-white text-sm outline-none transition focus:border-red-500 focus:ring-2 focus:ring-red-200"
                      placeholder="Juan"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700" htmlFor="lastName">
                    Apellido
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <input
                      id="lastName"
                      name="lastName"
                      type="text"
                      required
                      className="w-full pl-10 pr-3 py-2.5 rounded-lg border border-gray-300 bg-white text-sm outline-none transition focus:border-red-500 focus:ring-2 focus:ring-red-200"
                      placeholder="Pérez"
                    />
                  </div>
                </div>
              </div>

              {/* Email */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700" htmlFor="email">
                  Correo electrónico
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    id="email"
                    name="email"
                    type="email"
                    required
                    autoComplete="email"
                    className="w-full pl-10 pr-3 py-2.5 rounded-lg border border-gray-300 bg-white text-sm outline-none transition focus:border-red-500 focus:ring-2 focus:ring-red-200"
                    placeholder="tu@email.com"
                  />
                </div>
              </div>

              {/* Edad */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700" htmlFor="age">
                  Edad
                </label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    id="age"
                    name="age"
                    type="number"
                    min="18"
                    max="120"
                    required
                    className="w-full pl-10 pr-3 py-2.5 rounded-lg border border-gray-300 bg-white text-sm outline-none transition focus:border-red-500 focus:ring-2 focus:ring-red-200"
                    placeholder="25"
                  />
                </div>
                <p className="text-xs text-gray-500">Necesaria para evaluaciones precisas</p>
              </div>

              {/* Contraseña */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700" htmlFor="password">
                  Contraseña
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    id="password"
                    name="password"
                    type="password"
                    required
                    autoComplete="new-password"
                    className="w-full pl-10 pr-3 py-2.5 rounded-lg border border-gray-300 bg-white text-sm outline-none transition focus:border-red-500 focus:ring-2 focus:ring-red-200"
                    placeholder="••••••••"
                  />
                </div>
                <p className="text-xs text-gray-500">Mínimo 6 caracteres</p>
              </div>

              {/* Confirmar Contraseña */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700" htmlFor="confirmPassword">
                  Confirmar contraseña
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type="password"
                    required
                    autoComplete="new-password"
                    className="w-full pl-10 pr-3 py-2.5 rounded-lg border border-gray-300 bg-white text-sm outline-none transition focus:border-red-500 focus:ring-2 focus:ring-red-200"
                    placeholder="••••••••"
                  />
                </div>
              </div>

              {/* Términos y Condiciones */}
              <div className="flex items-start space-x-2">
                <input
                  id="terms"
                  name="terms"
                  type="checkbox"
                  required
                  className="mt-1 h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                />
                <label htmlFor="terms" className="text-xs text-gray-600">
                  Acepto los <Link href="/terms" className="text-red-600 hover:underline">términos y condiciones</Link> y 
                  la <Link href="/privacy" className="text-red-600 hover:underline">política de privacidad</Link> de CardioSense
                </label>
              </div>

              {error ? (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <p className="text-sm text-red-600 text-center" role="alert">
                    {error}
                  </p>
                </div>
              ) : null}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Creando cuenta...</span>
                  </div>
                ) : (
                  "Crear Cuenta"
                )}
              </button>
            </form>

            {/* Footer del formulario */}
            <div className="mt-6 text-center space-y-4">
              <p className="text-sm text-gray-600">
                ¿Ya tienes cuenta?{" "}
                <Link href="/login" className="text-red-600 hover:text-red-700 font-medium">
                  Inicia sesión aquí
                </Link>
              </p>
              
              <div className="pt-4 border-t border-gray-200">
                <Link 
                  href="/" 
                  className="text-xs text-gray-500 hover:text-gray-700"
                >
                  ← Volver a la página principal
                </Link>
              </div>
            </div>
          </div>

          {/* Disclaimer */}
          <div className="mt-6 bg-yellow-50/80 backdrop-blur-sm border border-yellow-200 rounded-xl p-4">
            <div className="flex items-start space-x-2">
              <Shield className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs text-yellow-800">
                  <strong>Privacidad:</strong> Tus datos están protegidos y solo se usan para 
                  generar evaluaciones personalizadas. CardioSense no comparte información personal 
                  y cumple con estándares de privacidad de datos de salud.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}