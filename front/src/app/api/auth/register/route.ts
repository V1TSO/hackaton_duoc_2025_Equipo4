import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabaseClient";

export async function POST(request: Request) {
  try {
    // ✅ Tipamos el body del request
    const body = await request.json() as { email: string; password: string; name?: string };
    const { email, password, name } = body; // ← Aseguramos que exista en el scope

    if (!email || !password) {
      return NextResponse.json(
        { error: "Faltan campos obligatorios (email, password)" },
        { status: 400 }
      );
    }

    const supabase = await createSupabaseServerClient();

    // ✅ Registro de usuario en Supabase Auth
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { name }, // se guarda en user_metadata
      },
    });

    if (error) {
      console.error("Error Supabase SignUp:", error.message);
      return NextResponse.json({ error: error.message }, { status: 400 });
    }

    // ✅ Inserta/actualiza perfil en tabla 'profiles'
    if (data.user) {
      await supabase.from("profiles").upsert({
        id: data.user.id,
        name: name ?? null,
        created_at: new Date().toISOString(),
      });
    }

    return NextResponse.json({
      message: "Usuario registrado exitosamente",
      user: data.user,
    });
  } catch (error: any) {
    console.error("Error en registro:", error);
    return NextResponse.json(
      { error: "Error interno del servidor" },
      { status: 500 }
    );
  }
}
