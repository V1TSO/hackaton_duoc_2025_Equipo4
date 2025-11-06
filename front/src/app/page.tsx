"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Heart, Shield, Users, Brain, ArrowRight, Activity, Target } from "lucide-react";
import Link from "next/link";

export default function HomePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    const formData = new FormData(event.currentTarget);
    const email = (formData.get("email") as string)?.trim();
    const password = formData.get("password") as string;

    // Simulación de login (reemplazar con tu lógica real)
    try {
      // Credenciales de prueba
      if (
        (email === "admin@cardiosense.com" && password === "admin123") ||
        (email === "usuario@test.com" && password === "user123")
      ) {
        // Simular delay de API
        await new Promise(resolve => setTimeout(resolve, 1000));
        router.push("/dashboard");
      } else {
        throw new Error("Credenciales inválidas");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error inesperado");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-red-50 to-pink-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            {/* Logo y Título */}
            <div className="flex justify-center items-center space-x-3 mb-8">
              <Heart className="h-16 w-16 text-red-500" />
              <h1 className="text-5xl md:text-7xl font-bold text-gray-900">
                <span className="text-red-600">Cardio</span>Sense
              </h1>
            </div>
            
            <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-4xl mx-auto">
              Tu <strong className="text-red-600">Coach Personal de Salud Cardiovascular</strong> 
              powered by AI. Evalúa tu riesgo y recibe recomendaciones personalizadas.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <Link 
                href="/login"
                className="bg-red-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-red-700 flex items-center space-x-2 transition-all shadow-lg"
              >
                <span>🚀 Acceder a CardioSense</span>
                <ArrowRight className="h-5 w-5" />
              </Link>
              
              <Link 
                href="/register"
                className="border-2 border-red-600 text-red-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-red-50 transition-all"
              >
                Crear cuenta nueva
              </Link>
            </div>

            {/* Disclaimer prominente */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 max-w-3xl mx-auto">
              <div className="flex items-center justify-center space-x-2">
                <Shield className="h-5 w-5 text-yellow-600" />
                <p className="text-sm text-yellow-800">
                  <strong>Importante:</strong> CardioSense es una herramienta educativa. 
                  No reemplaza el diagnóstico médico profesional.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              ¿Por qué elegir CardioSense?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Tecnología de vanguardia para cuidar lo más importante: tu salud cardiovascular
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="text-center p-6 rounded-xl bg-red-50 border border-red-100">
              <div className="bg-red-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Activity className="h-8 w-8 text-red-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Evaluación Inteligente</h3>
              <p className="text-gray-600">
                Algoritmo basado en datos NHANES para evaluar tu riesgo cardiometabólico con precisión científica
              </p>
            </div>

            {/* Feature 2 */}
            <div className="text-center p-6 rounded-xl bg-blue-50 border border-blue-100">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Target className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Coaching Personalizado</h3>
              <p className="text-gray-600">
                Recomendaciones específicas para tu perfil: nutrición, ejercicio, y hábitos de vida saludables
              </p>
            </div>

            {/* Feature 3 */}
            <div className="text-center p-6 rounded-xl bg-green-50 border border-green-100">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Brain className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Chatbot Especializado</h3>
              <p className="text-gray-600">
                Asistente AI disponible 24/7 para responder tus preguntas sobre salud cardiovascular
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Información de la empresa */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-6xl mx-auto px-6">
          {/* Encabezado */}
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Sobre CardioSense
            </h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Somos un equipo de profesionales comprometidos con democratizar el acceso 
              a herramientas de evaluación de riesgo cardiovascular mediante inteligencia artificial.
            </p>
          </div>

          {/* Cards informativos */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            {/* Misión */}
            <div className="text-center p-6 bg-white rounded-xl shadow-sm border border-gray-100">
              <div className="bg-red-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Heart className="h-8 w-8 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Nuestra Misión</h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                Empoderar a las personas con herramientas basadas en evidencia científica 
                para entender y mejorar su salud cardiovascular de manera proactiva.
              </p>
            </div>

            {/* Tecnología */}
            <div className="text-center p-6 bg-white rounded-xl shadow-sm border border-gray-100">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Brain className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Tecnología IA</h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                Utilizamos algoritmos de machine learning entrenados con datos NHANES 
                para proporcionar evaluaciones precisas y recomendaciones personalizadas.
              </p>
            </div>

            {/* Equipo */}
            <div className="text-center p-6 bg-white rounded-xl shadow-sm border border-gray-100">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Nuestro Equipo</h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                Desarrolladores, científicos de datos y profesionales de la salud 
                trabajando juntos para crear soluciones innovadoras y accesibles.
              </p>
            </div>
          </div>

          {/* Qué hacemos */}
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
            <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">
              ¿Qué hacemos?
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-red-100 rounded-full flex items-center justify-center mt-1">
                    <span className="text-red-600 text-sm font-bold">1</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Evaluación de Riesgo</h4>
                    <p className="text-gray-600 text-sm">
                      Analizamos factores como edad, presión arterial, IMC, y hábitos de vida 
                      para calcular tu riesgo cardiometabólico.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-red-100 rounded-full flex items-center justify-center mt-1">
                    <span className="text-red-600 text-sm font-bold">2</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Coaching Personalizado</h4>
                    <p className="text-gray-600 text-sm">
                      Generamos planes de 2 semanas con recomendaciones específicas 
                      de nutrición, ejercicio y cambios de estilo de vida.
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-red-100 rounded-full flex items-center justify-center mt-1">
                    <span className="text-red-600 text-sm font-bold">3</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Asistente Inteligente</h4>
                    <p className="text-gray-600 text-sm">
                      Nuestro chatbot especializado responde tus preguntas sobre 
                      salud cardiovascular las 24 horas del día.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-red-100 rounded-full flex items-center justify-center mt-1">
                    <span className="text-red-600 text-sm font-bold">4</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Educación Continua</h4>
                    <p className="text-gray-600 text-sm">
                      Proporcionamos recursos educativos basados en evidencia científica 
                      para que tomes decisiones informadas sobre tu salud.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="py-20 bg-red-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            ¿Listo para conocer tu riesgo cardiovascular?
          </h2>
          <p className="text-xl text-red-100 mb-8">
            Comienza tu evaluación gratuita ahora y recibe tu plan personalizado
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/login"
              className="bg-white text-red-600 px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 inline-flex items-center justify-center space-x-2 transition-all"
            >
              <span>Comenzar Ahora</span>
              <ArrowRight className="h-5 w-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Disclaimer médico final */}
      <div className="bg-yellow-50 border-t border-yellow-200">
        <div className="max-w-4xl mx-auto px-6 py-8">
          <div className="flex items-start justify-center">
            <Shield className="h-5 w-5 text-yellow-600 mr-3 mt-0.5 flex-shrink-0" />
            <div className="text-center">
              <h4 className="font-semibold text-yellow-800 mb-2">Disclaimer Médico</h4>
              <p className="text-sm text-yellow-700 leading-relaxed">
                CardioSense es una herramienta educativa basada en datos NHANES. No constituye diagnóstico médico 
                ni reemplaza la consulta con profesionales de salud. Siempre consulta con tu médico.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
