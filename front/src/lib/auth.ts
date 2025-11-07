// src/lib/auth.ts

// 1. Definir la forma de la respuesta de la API de login
interface LoginResponse {
  success: boolean;
  message?: string;
  role?: string;
}

/**
 * Funciones de autenticación para el lado del CLIENTE (Client Components).
 * Estas funciones envuelven las llamadas a las API Routes.
 */
export const auth = {
  /**
   * Llama a la API de login.
   */
  login: async (email: string, password: string) => {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    // 2. Aplicar el "type casting" a la respuesta JSON
    const data = (await response.json()) as LoginResponse;

    if (!response.ok) {
      // 3. Ahora 'data.message' es reconocido por TypeScript
      return { success: false, error: data.message || "Error al iniciar sesión" };
    }

    // 4. Ahora 'data.role' es reconocido por TypeScript
    return { success: true, user: { role: data.role || "user" } };
  },

  /**
   * Llama a la API de logout (si la tienes).
   */
  logout: async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    // Usualmente seguido de un router.push('/login') en el componente
  },
};