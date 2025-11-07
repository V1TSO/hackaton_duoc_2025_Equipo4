// src/lib/supabaseClient.ts
import { createServerClient, type CookieOptions } from "@supabase/ssr";
import { cookies } from "next/headers"; // ✅ no importes ReadonlyRequestCookies

/**
 * Crea un cliente de Supabase para el lado del servidor (API Routes o Server Components)
 * compatible con Next.js 15 (cookies() asíncrono)
 */
export async function createSupabaseServerClient() {
  // ✅ cookies() ahora devuelve una Promesa → necesitas await
  const cookieStore = await cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value;
        },
        set(name: string, value: string, options: CookieOptions) {
          try {
            cookieStore.set({ name, value, ...options });
          } catch (error) {
            console.error("Error al establecer cookie:", error);
          }
        },
        remove(name: string, options: CookieOptions) {
          try {
            cookieStore.set({ name, value: "", ...options });
          } catch (error) {
            console.error("Error al eliminar cookie:", error);
          }
        },
      },
    }
  );
}
