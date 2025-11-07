"use client";

import { useActionState } from "react";
import { useFormStatus } from "react-dom";
import { Heart, Shield, ArrowLeft, Mail, Lock, User, Calendar } from "lucide-react";
import Link from "next/link";
import { signUpAction } from "@/lib/actions/auth";

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {pending ? (
        <div className="flex items-center justify-center space-x-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          <span>Creando cuenta...</span>
        </div>
      ) : (
        "Crear Cuenta"
      )}
    </button>
  );
}

export default function RegisterPage() {
  const [state, formAction] = useActionState(signUpAction, { error: "" });

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-50">
      <div className="flex min-h-screen items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <Link
            href="/"
            className="inline-flex items-center text-sm text-gray-600 hover:text-red-600 mb-8 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver al inicio
          </Link>

          <div className="rounded-2xl border border-white/20 bg-white/80 backdrop-blur-sm p-8 shadow-xl">
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

            <form className="space-y-4" action={formAction}>
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

              <div className="grid grid-cols-2 gap-3">
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
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700" htmlFor="sex">
                    Sexo
                  </label>
                  <select
                    id="sex"
                    name="sex"
                    required
                    className="w-full px-3 py-2.5 rounded-lg border border-gray-300 bg-white text-sm outline-none transition focus:border-red-500 focus:ring-2 focus:ring-red-200"
                  >
                    <option value="">Seleccionar</option>
                    <option value="M">Masculino</option>
                    <option value="F">Femenino</option>
                  </select>
                </div>
              </div>

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

              {state?.error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <p className="text-sm text-red-600 text-center" role="alert">
                    {state.error}
                  </p>
                </div>
              )}

              <SubmitButton />
            </form>

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
