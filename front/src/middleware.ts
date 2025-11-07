// src/middleware.ts

import { NextResponse, type NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  // Rutas que requieren autenticación
  const protectedRoutes = ["/dashboard", "/chat", "/profile", "/admin"];

  // Rutas públicas donde NO queremos usuarios autenticados
  const authRoutes = ["/login", "/register"];

  // Verificar tokens de autenticación en cookies
  const authTokens = [
    "sb-access-token",
    "supabase-auth-token", // Nombre de cookie legacy
    "sb-refresh-token",
  ];

  const hasValidToken = authTokens.some(
    (tokenName) =>
      request.cookies.has(tokenName) && request.cookies.get(tokenName)?.value,
  );

  // Bloquear acceso a rutas protegidas sin autenticación
  if (protectedRoutes.some((route) => pathname.startsWith(route))) {
    if (!hasValidToken) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("redirect", pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  // Redirigir usuarios autenticados lejos de login/register
  if (authRoutes.some((route) => pathname.startsWith(route))) {
    if (hasValidToken) {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Aplicar a todas las rutas excepto:
     * - API routes
     * - _next/static (archivos estáticos)
     * - _next/image (optimización de imágenes)
     * - favicon.ico
     * - archivos públicos
     */
    "/((?!api|_next/static|_next/image|favicon.ico|.*\\.).*)",
  ],
};