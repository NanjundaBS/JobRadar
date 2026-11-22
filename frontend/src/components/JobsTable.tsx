'use client';

import { useState } from 'react';
import { clsx } from 'clsx';
import { FilterState } from '@/app/page';

export interface Job {
  id: string;
  company_name: string;
  company_type: string;
  career_url: string | null;
  job_title: string;
  job_url: string;
  location: string | null;
  experience_required: string | null;
  matched_skills: string[] | null;
  why_it_matches: string | null;
  job_description_short: string | null;
  hr_email: string | null;
  hr_email_verified: boolean;
  source: string;
  match_score: number;
  date_posted: string | null;
  is_new: boolean;
  status: string;
  created_at: string;
}

interface JobsTableProps {
  data: { items: Job[]; total: number; page: number; page_size: number; total_pages: number } | undefined;
  loading: boolean;
  filters: FilterState;
  onSort: (col: string) => void;
  onPageChange: (page: number) => void;
  onStatusUpdate: (id: string, status: string) => void;
}

const SCORE_COLOR = (s: number) =>
  s >= 70
    ? 'text-green-600 dark:text-green-400'
    : s >= 50
    ? 'text-yellow-600 dark:text-yellow-400'
    : 'text-gray-500 dark:text-gray-400';

const STATUS_COLORS: Record<string, string> = {
  new: 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300',
  applied: 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300',
  saved: 'bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-300',
  ignored: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400',
};

const SOURCE_COLORS: Record<string, string> = {
  naukri: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
  wellfound: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300',
  linkedin: 'bg-sky-100 text-sky-700 dark:bg-sky-900/40 dark:text-sky-300',
  indeed: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
  ycombinator: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300',
  default: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
};

function SortIcon({ col, filters }: { col: string; filters: FilterState }) {
  if (filters.sort_by !== col) return <span className="text-gray-300 dark:text-gray-600 ml-1">↕</span>;
  return <span className="text-blue-500 ml-1">{filters.sort_dir === 'desc' ? '↓' : '↑'}</span>;
}

function ExpandableCell({ text, maxLen = 80 }: { text: string; maxLen?: number }) {
  const [expanded, setExpanded] = useState(false);
  if (!text) return <span className="text-gray-400">—</span>;
  if (text.length <= maxLen) return <span>{text}</span>;
  return (
    <span>
      {expanded ? text : text.slice(0, maxLen) + '...'}
      <button
        onClick={() => setExpanded(!expanded)}
        className="ml-1 text-blue-500 hover:underline text-xs font-semibold"
      >
        {expanded ? 'less' : 'more'}
      </button>
    </span>
  );
}

export function JobsTable({ data, loading, filters, onSort, onPageChange, onStatusUpdate }: JobsTableProps) {
  const thClass =
    'px-3 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide whitespace-nowrap';
  const tdClass = 'px-3 py-3 text-sm text-gray-800 dark:text-gray-200 align-top';

  const SortableTh = ({ col, label }: { col: string; label: string }) => (
    <th
      className={`${thClass} cursor-pointer hover:text-gray-700 dark:hover:text-gray-200 select-none`}
      onClick={() => onSort(col)}
    >
      {label}
      <SortIcon col={col} filters={filters} />
    </th>
  );

  if (loading) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-gray-200 dark:border-slate-700 overflow-hidden shadow-sm">
        <div className="p-12 text-center text-gray-400 animate-pulse">Loading matched jobs...</div>
      </div>
    );
  }

  const jobs = data?.items || [];
  const total = data?.total || 0;
  const totalPages = data?.total_pages || 1;
  const currentPage = data?.page || 1;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-gray-200 dark:border-slate-700 overflow-hidden shadow-sm">
      {/* Table header info */}
      <div className="px-4 py-3 border-b border-gray-200 dark:border-slate-700 flex items-center justify-between">
        <span className="text-sm text-gray-600 dark:text-gray-400">
          <span className="font-semibold text-gray-900 dark:text-white">{total}</span> jobs found
          {filters.search && ` matching "${filters.search}"`}
        </span>
        <span className="text-xs text-gray-400">Auto-refreshes every 60s</span>
      </div>

      {/* Scrollable table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-slate-700">
          <thead className="bg-gray-50 dark:bg-slate-800/60">
            <tr>
              <SortableTh col="company_name" label="Company" />
              <th className={thClass}>Type</th>
              <th className={thClass}>Careers</th>
              <SortableTh col="match_score" label="Score" />
              <th className={thClass}>Job Title</th>
              <th className={thClass}>Apply</th>
              <th className={thClass}>Exp Required</th>
              <th className={thClass}>Matched Skills</th>
              <th className={thClass}>Why Match</th>
              <th className={thClass}>Description</th>
              <th className={thClass}>HR Email</th>
              <th className={thClass}>Source</th>
              <SortableTh col="date_posted" label="Posted" />
              <th className={thClass}>Status / Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-slate-800">
            {jobs.length === 0 ? (
              <tr>
                <td colSpan={14} className="px-4 py-16 text-center text-gray-400 dark:text-gray-500">
                  <div className="text-4xl mb-3">🔍</div>
                  <div className="font-medium text-base text-gray-600 dark:text-gray-300">No jobs found</div>
                  <div className="text-sm mt-1">Try adjusting your filters or click "Refresh Now" to trigger a run</div>
                </td>
              </tr>
            ) : (
              jobs.map((job) => (
                <tr
                  key={job.id}
                  className={clsx(
                    'hover:bg-gray-50 dark:hover:bg-slate-800/50 transition-colors',
                    job.is_new && 'border-l-4 border-blue-500 bg-blue-50/20 dark:bg-blue-900/10'
                  )}
                >
                  {/* Company */}
                  <td className={tdClass}>
                    <div className="font-semibold text-gray-900 dark:text-white whitespace-nowrap">
                      {job.company_name}
                      {job.is_new && (
                        <span className="ml-1.5 text-[10px] bg-blue-500 text-white px-1.5 py-0.5 rounded-full font-bold">
                          NEW
                        </span>
                      )}
                    </div>
                  </td>
                  {/* Type */}
                  <td className={tdClass}>
                    <span
                      className={clsx(
                        'text-xs px-2 py-0.5 rounded-full font-medium whitespace-nowrap',
                        job.company_type === 'Startup'
                          ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300'
                          : job.company_type === 'Product'
                          ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300'
                          : 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300'
                      )}
                    >
                      {job.company_type || 'Unknown'}
                    </span>
                  </td>
                  {/* Career URL */}
                  <td className={tdClass}>
                    {job.career_url ? (
                      <a
                        href={job.career_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 dark:text-blue-400 hover:underline text-xs whitespace-nowrap"
                      >
                        Careers →
                      </a>
                    ) : (
                      <span className="text-gray-400 text-xs">—</span>
                    )}
                  </td>
                  {/* Score */}
                  <td className={`${tdClass} text-center`}>
                    <span className={clsx('text-xl font-extrabold', SCORE_COLOR(job.match_score))}>
                      {job.match_score}
                    </span>
                  </td>
                  {/* Job Title */}
                  <td className={tdClass}>
                    <div className="font-medium max-w-[200px] text-gray-900 dark:text-white">{job.job_title}</div>
                    {job.location && <div className="text-xs text-gray-400 mt-0.5">📍 {job.location}</div>}
                  </td>
                  {/* Apply Link */}
                  <td className={tdClass}>
                    <a
                      href={job.job_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors whitespace-nowrap shadow-sm"
                    >
                      Apply →
                    </a>
                  </td>
                  {/* Experience */}
                  <td className={tdClass}>
                    <span className="text-xs font-mono text-gray-700 dark:text-gray-300 whitespace-nowrap">
                      {job.experience_required || 'Not specified'}
                    </span>
                  </td>
                  {/* Skills */}
                  <td className={tdClass}>
                    <div className="flex flex-wrap gap-1 max-w-[170px]">
                      {(job.matched_skills || []).slice(0, 4).map((s) => (
                        <span
                          key={s}
                          className="text-xs bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-gray-300 px-1.5 py-0.5 rounded font-medium"
                        >
                          {s}
                        </span>
                      ))}
                      {(job.matched_skills?.length || 0) > 4 && (
                        <span className="text-xs text-gray-400">
                          +{(job.matched_skills?.length || 0) - 4}
                        </span>
                      )}
                    </div>
                  </td>
                  {/* Why match */}
                  <td className={tdClass}>
                    <div className="max-w-[200px] text-xs text-gray-600 dark:text-gray-400">
                      <ExpandableCell text={job.why_it_matches || ''} maxLen={80} />
                    </div>
                  </td>
                  {/* Description */}
                  <td className={tdClass}>
                    <div className="max-w-[200px] text-xs text-gray-500 dark:text-gray-500">
                      <ExpandableCell text={job.job_description_short || ''} maxLen={90} />
                    </div>
                  </td>
                  {/* HR Email */}
                  <td className={tdClass}>
                    {job.hr_email ? (
                      <div className="whitespace-nowrap">
                        <a
                          href={`mailto:${job.hr_email}`}
                          className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                        >
                          {job.hr_email}
                        </a>
                        {job.hr_email_verified && (
                          <span className="ml-1 text-xs text-green-500 font-bold" title="Verified Public Email">
                            ✓
                          </span>
                        )}
                      </div>
                    ) : (
                      <span className="text-xs text-gray-400 whitespace-nowrap">Not available</span>
                    )}
                  </td>
                  {/* Source */}
                  <td className={tdClass}>
                    <span
                      className={clsx(
                        'text-xs px-2 py-0.5 rounded-full font-medium whitespace-nowrap',
                        SOURCE_COLORS[job.source] || SOURCE_COLORS.default
                      )}
                    >
                      {job.source}
                    </span>
                  </td>
                  {/* Date */}
                  <td className={tdClass}>
                    <span className="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
                      {job.date_posted
                        ? new Date(job.date_posted).toLocaleDateString('en-IN', {
                            day: '2-digit',
                            month: 'short',
                          })
                        : '—'}
                    </span>
                  </td>
                  {/* Status / Actions */}
                  <td className={tdClass}>
                    <div className="flex flex-col gap-1 w-24">
                      <span
                        className={clsx(
                          'text-xs px-2 py-0.5 rounded-full font-medium text-center',
                          STATUS_COLORS[job.status] || STATUS_COLORS.new
                        )}
                      >
                        {job.status}
                      </span>
                      <select
                        value={job.status}
                        onChange={(e) => onStatusUpdate(job.id, e.target.value)}
                        className="text-xs bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-600 rounded px-1 py-1 text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer"
                      >
                        <option value="new">New</option>
                        <option value="applied">Applied</option>
                        <option value="saved">Saved</option>
                        <option value="ignored">Ignored</option>
                      </select>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="px-4 py-3 border-t border-gray-200 dark:border-slate-700 flex items-center justify-between">
          <span className="text-sm text-gray-500 dark:text-gray-400">
            Page {currentPage} of {totalPages} ({total} total jobs)
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage <= 1}
              className="px-3 py-1.5 text-sm bg-gray-100 dark:bg-slate-800 text-gray-700 dark:text-gray-300 rounded-lg disabled:opacity-40 hover:bg-gray-200 dark:hover:bg-slate-700 transition-colors"
            >
              ← Prev
            </button>
            {[...Array(Math.min(5, totalPages))].map((_, i) => {
              const p = Math.max(1, currentPage - 2) + i;
              if (p > totalPages) return null;
              return (
                <button
                  key={p}
                  onClick={() => onPageChange(p)}
                  className={clsx(
                    'px-3 py-1.5 text-sm rounded-lg transition-colors font-medium',
                    p === currentPage
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-slate-700'
                  )}
                >
                  {p}
                </button>
              );
            })}
            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage >= totalPages}
              className="px-3 py-1.5 text-sm bg-gray-100 dark:bg-slate-800 text-gray-700 dark:text-gray-300 rounded-lg disabled:opacity-40 hover:bg-gray-200 dark:hover:bg-slate-700 transition-colors"
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
