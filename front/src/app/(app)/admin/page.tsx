import Link from "next/link";
import { requireAdmin } from "@/lib/auth";

export const runtime = "edge";

export default async function AdminPage() {
  const session = await requireAdmin();

  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col gap-10 px-6 py-16">
      <header className="space-y-2">
        <p className="text-sm uppercase tracking-[0.2em] text-foreground/60">
          Administrador
        </p>
        <h1 className="text-3xl font-semibold text-foreground">
          Panel de control
        </h1>
        <p className="text-sm text-foreground/70">
          Supervisa sesiones, sincroniza conocimiento RAG y gestiona accesos.
        </p>
      </header>

      <section className="grid gap-4 md:grid-cols-2">
        <article className="rounded-xl border border-black/10 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-neutral-900">
          <h2 className="text-lg font-medium">Estado general</h2>
          <ul className="mt-3 space-y-2 text-sm text-foreground/70">
            <li>• Usuario activo: {session.user.email}</li>
            <li>• Rol: admin</li>
            <li>• Progreso coach: vincular con métricas ML</li>
          </ul>
        </article>

        <article className="rounded-xl border border-black/10 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-neutral-900">
          <h2 className="text-lg font-medium">Próximos controles</h2>
          <ul className="mt-3 space-y-2 text-sm text-foreground/70">
            <li>1. Revisar fairness por subgrupo.</li>
            <li>2. Actualizar KB conforme nuevas pautas clínicas.</li>
            <li>3. Auditar logs de `/predict` y `/coach`.</li>
          </ul>
        </article>
      </section>

      <div className="flex flex-col gap-4 sm:flex-row">
        <Link
          href="/app"
          className="rounded-md border border-black/10 px-4 py-2 text-sm font-semibold text-foreground transition hover:border-black/30 dark:border-white/10 dark:hover:border-white/40"
        >
          ← Volver al panel principal
        </Link>
        <form action="/api/auth/logout" method="post">
          <button
            type="submit"
            className="rounded-md bg-black px-4 py-2 text-sm font-semibold text-white transition hover:bg-black/80 dark:bg-white dark:text-black dark:hover:bg-white/80"
          >
            Cerrar sesión
          </button>
        </form>
      </div>

      <footer className="mt-auto border-t border-black/10 pt-6 text-xs text-foreground/60 dark:border-white/10">
        CardioSense es informativo. No reemplaza diagnóstico médico profesional.
      </footer>
    </main>
  );
}

