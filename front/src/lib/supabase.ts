import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

// Debug para ver qué está pasando
if (typeof window !== 'undefined') {
  console.log('🔧 Supabase Debug:', {
    url: supabaseUrl ? '✅ Set' : '❌ Missing',
    key: supabaseAnonKey ? '✅ Set' : '❌ Missing'
  })
}

if (!supabaseUrl) {
  throw new Error('❌ NEXT_PUBLIC_SUPABASE_URL no está definida')
}

if (!supabaseAnonKey) {
  throw new Error('❌ NEXT_PUBLIC_SUPABASE_ANON_KEY no está definida')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
  }
})

// Tipos para tu base de datos
export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  age: number
  created_at: string
  updated_at: string
}

export interface HealthProfile {
  id: string
  user_id: string
  weight?: number
  height?: number
  blood_pressure_systolic?: number
  blood_pressure_diastolic?: number
  cholesterol_total?: number
  glucose_level?: number
  smoking_status?: 'never' | 'former' | 'current'
  exercise_frequency?: number
  created_at: string
  updated_at: string
}

// Exportar funciones de autenticación - CORREGIDO
export const supabaseAuth = {
  // Registrar usuario
  async signUp(email: string, password: string, userData: { 
    firstName: string, 
    lastName: string, 
    age: number 
  }) {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          first_name: userData.firstName,
          last_name: userData.lastName,
          age: userData.age,
        }
      }
    })
    
    return { data, error }
  },

  // Iniciar sesión
  async signIn(email: string, password: string) {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    
    return { data, error }
  },

  // Cerrar sesión
  async signOut() {
    const { error } = await supabase.auth.signOut()
    return { error }
  },

  // Obtener usuario actual
  async getCurrentUser() {
    const { data: { user }, error } = await supabase.auth.getUser()
    return { user, error }
  },

  // Escuchar cambios de autenticación
  onAuthStateChange(callback: (event: string, session: any) => void) {
    return supabase.auth.onAuthStateChange(callback)
  }
}