import Link from "next/link";
import { requireUser, getUserRole } from "@/lib/auth";

export const runtime = "edge";

export default async function AppDashboardPage() {
  const session = await requireUser();
  const role = getUserRole(session.user);

  return (
    <main className="mx-auto flex min-h-screen max-w-4xl flex-col gap-10 px-6 py-16">
      <header className="space-y-2">
        <p className="text-sm uppercase tracking-[0.2em] text-foreground/60">
          CardioSense
        </p>
    
        <h1 className="text-3xl font-semibold text-foreground">
          Panel de riesgo cardiometabólico
        </h1>
        <p className="text-sm text-foreground/70">
          Sesión iniciada como {session.user.email}. Mantén siempre visible el
          disclaimer médico y valida los datos antes de enviar a la API.
        </p>
      </header>

      <section className="grid gap-4 md:grid-cols-2">
        <article className="rounded-xl border border-black/10 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-neutral-900">
          <h2 className="text-lg font-medium">Próximos pasos</h2>
          <ul className="mt-3 space-y-2 text-sm text-foreground/70">
            <li>1. Construye el formulario de intake alineado a NHANES.</li>
            <li>2. Llama a `/predict` y presenta métricas clave.</li>
            <li>3. Habilita el módulo Coach con `/coach` y citas RAG.</li>
          </ul>
        </article>

        <article className="rounded-xl border border-black/10 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-neutral-900">
          <h2 className="text-lg font-medium">Sesión</h2>
          <dl className="mt-3 space-y-2 text-sm text-foreground/70">
            <div className="flex items-center justify-between">
              <dt>Correo</dt>
              <dd className="font-mono text-foreground">{session.user.email}</dd>
            </div>
            <div className="flex items-center justify-between">
              <dt>Rol</dt>
              <dd className="font-mono text-foreground">{role ?? "user"}</dd>
            </div>
          </dl>

          <form action="/api/auth/logout" method="post" className="mt-6">
            <button
              type="submit"
              className="w-full rounded-md bg-black px-3 py-2 text-sm font-semibold text-white transition hover:bg-black/80 dark:bg-white dark:text-black dark:hover:bg-white/80"
            >
              Cerrar sesión
            </button>
          </form>
        </article>
      </section>

      {role === "admin" ? (
        <Link
          href="/admin"
          className="text-sm font-semibold text-black underline-offset-4 transition hover:underline dark:text-white"
        >
          Ir al panel de administración →
        </Link>
      ) : null}

      <footer className="mt-auto border-t border-black/10 pt-6 text-xs text-foreground/60 dark:border-white/10">
        CardioSense es informativo. No reemplaza diagnóstico médico profesional.
      </footer>
    </main>
  );
}

