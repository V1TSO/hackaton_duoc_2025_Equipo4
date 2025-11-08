"use client";

import { useEffect, useState } from 'react';

export type Theme = 'light' | 'dark' | 'system';

export function useDarkMode() {
  const [theme, setTheme] = useState<Theme>('system');
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as Theme | null;
    if (savedTheme) {
      setTheme(savedTheme);
    }
  }, []);

  useEffect(() => {
    const root = window.document.documentElement;
    
    const getSystemTheme = (): 'light' | 'dark' => {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };

    let activeTheme: 'light' | 'dark';
    
    if (theme === 'system') {
      activeTheme = getSystemTheme();
    } else {
      activeTheme = theme as 'light' | 'dark';
    }

    setResolvedTheme(activeTheme);
    
    root.classList.remove('light', 'dark');
    root.classList.add(activeTheme);
    
    if (theme !== 'system') {
      localStorage.setItem('theme', theme);
    } else {
      localStorage.removeItem('theme');
    }
  }, [theme]);

  useEffect(() => {
    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      
      const handleChange = (e: MediaQueryListEvent) => {
        setResolvedTheme(e.matches ? 'dark' : 'light');
      };

      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [theme]);

  return {
    theme,
    resolvedTheme,
    setTheme,
    toggleTheme: () => {
      setTheme(current => {
        if (current === 'light') return 'dark';
        if (current === 'dark') return 'light';
        return 'light';
      });
    },
  };
}

