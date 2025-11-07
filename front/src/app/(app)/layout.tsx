import { requireUser } from "@/lib/auth-helpers";
import { DisclaimerBanner, ApiStatusBanner, LogoutButton } from "@/components";
import {
  Heart,
  LayoutDashboard,
  ClipboardList,
  MessageSquare,
  ListTodo,
  History,
} from "lucide-react";
import Link from "next/link";

export const runtime = "edge";

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await requireUser();

  return (
    <div className="min-h-screen bg-gray-50">
      <DisclaimerBanner />
      <ApiStatusBanner />
      
      <div className="flex">
        <aside className="hidden md:flex md:flex-col md:w-64 bg-white border-r border-gray-200 min-h-screen">
          <div className="p-6 border-b border-gray-200">
            <Link href="/app" className="flex items-center gap-2">
              <Heart className="h-8 w-8 text-red-600" />
              <span className="text-xl font-bold text-gray-900">CardioSense</span>
            </Link>
          </div>

          <nav className="flex-1 p-4 space-y-1">
            <NavLink href="/app" icon={LayoutDashboard}>
              Dashboard
            </NavLink>
            <NavLink href="/chat" icon={MessageSquare}>
              Conversación IA
            </NavLink>
            <NavLink href="/coach" icon={ClipboardList}>
              Plan Personalizado
            </NavLink>
            <NavLink href="/plan" icon={ListTodo}>
              Mi Plan
            </NavLink>
            <NavLink href="/history" icon={History}>
              Historial
            </NavLink>
          </nav>

          <div className="p-4 border-t border-gray-200">
            <div className="mb-3 p-3 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-600 mb-1">Sesión iniciada</p>
              <p className="text-sm font-medium text-gray-900 truncate">
                {session.user.email}
              </p>
            </div>
            <LogoutButton />
          </div>
        </aside>

        <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50">
          <nav className="flex justify-around items-center py-2">
            <MobileNavLink href="/app" icon={LayoutDashboard}>
              Dashboard
            </MobileNavLink>
            <MobileNavLink href="/chat" icon={MessageSquare}>
              Chat
            </MobileNavLink>
            <MobileNavLink href="/coach" icon={ClipboardList}>
              Plan
            </MobileNavLink>
            <MobileNavLink href="/plan" icon={ListTodo}>
              Mi Plan
            </MobileNavLink>
            <MobileNavLink href="/history" icon={History}>
              Historial
            </MobileNavLink>
          </nav>
        </div>

        <main className="flex-1 pb-20 md:pb-0">
          {children}
        </main>
      </div>
    </div>
  );
}

function NavLink({
  href,
  icon: Icon,
  children,
}: {
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className="flex items-center gap-3 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-red-50 hover:text-red-600 rounded-lg transition-colors"
    >
      <Icon className="h-5 w-5" />
      {children}
    </Link>
  );
}

function MobileNavLink({
  href,
  icon: Icon,
  children,
}: {
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className="flex flex-col items-center gap-1 px-2 py-1 text-xs font-medium text-gray-600 hover:text-red-600 transition-colors"
    >
      <Icon className="h-5 w-5" />
      <span className="hidden xs:inline">{children}</span>
    </Link>
  );
}

