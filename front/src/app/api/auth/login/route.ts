import { NextResponse } from "next/server";
import { persistAuthSession } from "@/lib/auth";
import { createSupabaseServerClient } from "@/lib/supabaseClient";

export const runtime = "edge";

interface LoginPayload {
  email?: string;
  password?: string;
}

export async function POST(request: Request) {
  const supabase = createSupabaseServerClient();
  let payload: LoginPayload;

  try {
    payload = (await request.json()) as LoginPayload;
  } catch {
    return NextResponse.json({ message: "JSON inválido" }, { status: 400 });
  }

  const email = payload.email?.trim();
  const password = payload.password;

  if (!email || !password) {
    return NextResponse.json(
      { message: "Correo y contraseña son obligatorios" },
      { status: 400 },
    );
  }

  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (error || !data.session) {
    return NextResponse.json(
      { message: error?.message ?? "Credenciales inválidas" },
      { status: 401 },
    );
  }

  await persistAuthSession(data.session);

  return NextResponse.json({ success: true });
}

