'use client';

import { FilterState } from '@/app/page';

const COMPANY_TYPES = ['Startup', 'Product', 'Service'];
const SOURCES = ['naukri', 'wellfound', 'ycombinator', 'indeed', 'foundit', 'linkedin', 'cutshort', 'instahyre', 'company_careers', 'hackernews'];
const STATUSES = ['new', 'applied', 'saved', 'ignored'];

interface FilterBarProps {
  filters: FilterState;
  onChange: (key: keyof FilterState, value: string | number | boolean | undefined) => void;
  onClear: () => void;
}

const selectCls = "px-3 py-2 text-sm bg-white dark:bg-slate-900 border border-gray-300 dark:border-slate-600 rounded-lg text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer";

export function FilterBar({ filters, onChange, onClear }: FilterBarProps) {
  const hasFilters = filters.search || filters.company_type || filters.source || filters.status || filters.min_score > 0 || filters.is_new;

  return (
    <div className="flex flex-wrap gap-2 items-center">
      {/* Search */}
      <div className="relative">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm pointer-events-none">🔍</span>
        <input
          type="text"
          placeholder="Search jobs, companies, skills..."
          value={filters.search}
          onChange={e => onChange('search', e.target.value)}
          className="pl-9 pr-4 py-2 text-sm bg-white dark:bg-slate-900 border border-gray-300 dark:border-slate-600 rounded-lg text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 w-72"
        />
      </div>

      {/* Company type */}
      <select value={filters.company_type} onChange={e => onChange('company_type', e.target.value)} className={selectCls}>
        <option value="">All Types</option>
        {COMPANY_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
      </select>

      {/* Source */}
      <select value={filters.source} onChange={e => onChange('source', e.target.value)} className={selectCls}>
        <option value="">All Sources</option>
        {SOURCES.map(s => <option key={s} value={s}>{s}</option>)}
      </select>

      {/* Status */}
      <select value={filters.status} onChange={e => onChange('status', e.target.value)} className={selectCls}>
        <option value="">All Status</option>
        {STATUSES.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
      </select>

      {/* Min score slider */}
      <div className="flex items-center gap-2">
        <label className="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">Min Score:</label>
        <input
          type="range" min={0} max={100} step={5}
          value={filters.min_score}
          onChange={e => onChange('min_score', Number(e.target.value))}
          className="w-20 accent-blue-600"
        />
        <span className="text-xs font-mono font-semibold text-gray-700 dark:text-gray-300 w-6 text-right">
          {filters.min_score > 0 ? filters.min_score : 'All'}
        </span>
      </div>

      {/* New only */}
      <label className="flex items-center gap-1.5 cursor-pointer select-none">
        <input
          type="checkbox"
          checked={filters.is_new === true}
          onChange={e => onChange('is_new', e.target.checked ? true : undefined)}
          className="w-4 h-4 accent-blue-600 cursor-pointer"
        />
        <span className="text-sm text-gray-600 dark:text-gray-400">New only</span>
      </label>

      {/* Clear */}
      {hasFilters && (
        <button
          onClick={onClear}
          className="text-xs text-gray-400 hover:text-red-500 dark:hover:text-red-400 underline transition-colors"
        >
          ✕ Clear
        </button>
      )}
    </div>
  );
}
