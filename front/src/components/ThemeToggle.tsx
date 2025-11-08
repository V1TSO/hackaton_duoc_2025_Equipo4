"use client";

import { Moon, Sun } from 'lucide-react';
import { useDarkMode } from '@/lib/hooks/useDarkMode';

export function ThemeToggle() {
  const { resolvedTheme, toggleTheme } = useDarkMode();

  return (
    <button
      onClick={toggleTheme}
      className="flex items-center justify-center w-10 h-10 rounded-lg bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 transition-colors"
      aria-label={resolvedTheme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
      title={resolvedTheme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
    >
      {resolvedTheme === 'dark' ? (
        <Sun className="h-5 w-5 text-yellow-500" aria-hidden="true" />
      ) : (
        <Moon className="h-5 w-5 text-gray-700" aria-hidden="true" />
      )}
    </button>
  );
}

