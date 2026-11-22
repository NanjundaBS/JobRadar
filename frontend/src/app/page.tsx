'use client';

import { useState, useCallback } from 'react';
import useSWR, { mutate } from 'swr';
import { StatsCards } from '@/components/StatsCards';
import { JobsTable } from '@/components/JobsTable';
import { FilterBar } from '@/components/FilterBar';
import { Header } from '@/components/Header';

const fetcher = (url: string) => fetch(url).then(r => r.json());

export interface FilterState {
  search: string;
  company_type: string;
  source: string;
  min_score: number;
  status: string;
  sort_by: string;
  sort_dir: string;
  page: number;
  page_size: number;
  is_new?: boolean;
}

const DEFAULT_FILTERS: FilterState = {
  search: '',
  company_type: '',
  source: '',
  min_score: 0,
  status: '',
  sort_by: 'match_score',
  sort_dir: 'desc',
  page: 1,
  page_size: 25,
};

function buildQueryString(filters: FilterState): string {
  const params = new URLSearchParams();
  if (filters.search) params.set('search', filters.search);
  if (filters.company_type) params.set('company_type', filters.company_type);
  if (filters.source) params.set('source', filters.source);
  if (filters.min_score > 0) params.set('min_score', String(filters.min_score));
  if (filters.status) params.set('status', filters.status);
  if (filters.is_new === true) params.set('is_new', 'true');
  params.set('sort_by', filters.sort_by);
  params.set('sort_dir', filters.sort_dir);
  params.set('page', String(filters.page));
  params.set('page_size', String(filters.page_size));
  return params.toString();
}

export default function Dashboard() {
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [triggering, setTriggering] = useState(false);
  const [triggerMsg, setTriggerMsg] = useState('');

  const jobsUrl = `/api/jobs?${buildQueryString(filters)}`;
  const { data: jobsData, isLoading: jobsLoading } = useSWR(jobsUrl, fetcher, { refreshInterval: 60000 });
  const { data: stats, isLoading: statsLoading } = useSWR('/api/stats', fetcher, { refreshInterval: 60000 });

  const handleFilterChange = useCallback((key: keyof FilterState, value: string | number | boolean | undefined) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }));
  }, []);

  const handlePageChange = useCallback((page: number) => {
    setFilters(prev => ({ ...prev, page }));
  }, []);

  const handleStatusUpdate = useCallback(async (jobId: string, status: string) => {
    await fetch(`/api/jobs/${jobId}/status?status=${status}`, { method: 'PATCH' });
    mutate(jobsUrl);
  }, [jobsUrl]);

  const handleRefresh = useCallback(async () => {
    setTriggering(true);
    setTriggerMsg('');
    try {
      const res = await fetch('/api/runs/trigger', { method: 'POST' });
      const data = await res.json();
      setTriggerMsg(data.message || 'Pipeline triggered!');
      setTimeout(() => setTriggerMsg(''), 8000);
    } catch {
      setTriggerMsg('Failed to trigger run');
    } finally {
      setTriggering(false);
    }
  }, []);

  const handleExportCSV = useCallback(() => {
    const params = new URLSearchParams();
    if (filters.min_score > 0) params.set('min_score', String(filters.min_score));
    if (filters.status) params.set('status', filters.status);
    window.open(`/api/jobs/export/csv?${params.toString()}`, '_blank');
  }, [filters]);

  const handleSort = useCallback((col: string) => {
    setFilters(prev => ({
      ...prev,
      sort_by: col,
      sort_dir: prev.sort_by === col && prev.sort_dir === 'desc' ? 'asc' : 'desc',
      page: 1,
    }));
  }, []);

  const handleClearFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-950 transition-colors">
      <Header onRefresh={handleRefresh} triggering={triggering} triggerMsg={triggerMsg} />

      <main className="max-w-screen-2xl mx-auto px-4 py-6 space-y-5">
        <StatsCards stats={stats} loading={statsLoading} />

        <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
          <FilterBar filters={filters} onChange={handleFilterChange} onClear={handleClearFilters} />
          <button
            onClick={handleExportCSV}
            className="shrink-0 flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
          >
            ↓ Export CSV
          </button>
        </div>

        <JobsTable
          data={jobsData}
          loading={jobsLoading}
          filters={filters}
          onSort={handleSort}
          onPageChange={handlePageChange}
          onStatusUpdate={handleStatusUpdate}
        />
      </main>
    </div>
  );
}
