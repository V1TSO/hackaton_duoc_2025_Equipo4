"use client";

import { useActionState, Suspense } from "react";
import { useFormStatus } from "react-dom";
import { Heart, Shield, ArrowLeft, Mail, Lock } from "lucide-react";
import Link from "next/link";
import { signInAction } from "@/lib/actions/auth";
import { useSearchParams } from "next/navigation";

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-4 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {pending ? "Iniciando sesión..." : "Iniciar Sesión"}
    </button>
  );
}

function LoginForm() {
  const searchParams = useSearchParams();
  const message = searchParams.get("message");
  const [state, formAction] = useActionState(signInAction, { error: "" });

  return (
    <>
      {message && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl">
          <p className="text-sm text-green-600 text-center">
            {decodeURIComponent(message)}
          </p>
        </div>
      )}

      <form className="space-y-5" action={formAction}>
        <div className="space-y-2">
          <label
            className="text-sm font-medium text-gray-700"
            htmlFor="email"
          >
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
              className="w-full pl-10 pr-3 py-3 rounded-xl border border-gray-300 bg-white text-sm outline-none transition focus:border-red-500 focus:ring-2 focus:ring-red-200"
              placeholder="tu@email.com"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label
            className="text-sm font-medium text-gray-700"
            htmlFor="password"
          >
            Contraseña
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              id="password"
              name="password"
              type="password"
              required
              autoComplete="current-password"
              className="w-full pl-10 pr-3 py-3 rounded-xl border border-gray-300 bg-white text-sm outline-none transition focus:border-red-500 focus:ring-2 focus:ring-red-200"
              placeholder="••••••••"
            />
          </div>
        </div>

        {state?.error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4">
            <p className="text-sm text-red-600 text-center" role="alert">
              {state.error}
            </p>
          </div>
        )}

        <SubmitButton />
      </form>
    </>
  );
}

export default function LoginPage() {
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
                Iniciar Sesión
              </h2>
              <p className="text-sm text-gray-600">
                Accede a tu dashboard personalizado
              </p>
            </div>

            <Suspense fallback={<div className="text-center">Cargando...</div>}>
              <LoginForm />
            </Suspense>

            <div className="mt-6 text-center space-y-4">
              <p className="text-sm text-gray-600">
                ¿No tienes cuenta?{" "}
                <Link
                  href="/register"
                  className="text-red-600 hover:text-red-700 font-medium"
                >
                  Regístrate aquí
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

          <div className="mt-8 bg-yellow-50/80 backdrop-blur-sm border border-yellow-200 rounded-xl p-4">
            <div className="flex items-center justify-center space-x-2">
              <Shield className="h-4 w-4 text-yellow-600" />
              <p className="text-xs text-yellow-800 text-center">
                <strong>Disclaimer:</strong> CardioSense es una herramienta
                educativa, no un diagnóstico médico.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
