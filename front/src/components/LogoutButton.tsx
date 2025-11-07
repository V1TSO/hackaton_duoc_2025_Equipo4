"use client";

import { LogOut } from "lucide-react";
import { signOutAction } from "@/lib/actions/auth";

export function LogoutButton() {
  const handleSignOut = async () => {
    // Clear localStorage before signing out
    if (typeof window !== "undefined") {
      localStorage.clear();
    }
    
    // Call server action
    await signOutAction();
  };

  return (
    <form action={handleSignOut}>
      <button
        type="submit"
        className="w-full flex items-center gap-2 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
      >
        <LogOut className="h-4 w-4" />
        Cerrar sesión
      </button>
    </form>
  );
}

