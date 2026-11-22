'use client';

import { useTheme } from './ThemeProvider';

interface HeaderProps {
  onRefresh: () => void;
  triggering: boolean;
  triggerMsg: string;
}

export function Header({ onRefresh, triggering, triggerMsg }: HeaderProps) {
  const { theme, toggle } = useTheme();

  return (
    <header className="sticky top-0 z-40 bg-white dark:bg-slate-900 border-b border-gray-200 dark:border-slate-700 shadow-sm">
      <div className="max-w-screen-2xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-md">
            🎯
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900 dark:text-white leading-none">JobRadar</h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">DevOps Job Intelligence · 2–4 Year Roles</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {triggerMsg && (
            <span className="text-sm text-green-600 dark:text-green-400 max-w-xs text-right">{triggerMsg}</span>
          )}

          <button
            onClick={onRefresh}
            disabled={triggering}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
          >
            {triggering ? (
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            ) : (
              <span>⟳</span>
            )}
            {triggering ? 'Running...' : 'Refresh Now'}
          </button>

          <button
            onClick={toggle}
            className="p-2 rounded-lg bg-gray-100 dark:bg-slate-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-slate-700 transition-colors text-lg"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </div>
      </div>
    </header>
  );
}
