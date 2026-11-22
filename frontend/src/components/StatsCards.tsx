'use client';

function StatCard({ label, value, sub, colorClass }: { label: string; value: string | number; sub?: string; colorClass: string }) {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-gray-200 dark:border-slate-700 p-5 shadow-sm">
      <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide font-medium">{label}</p>
      <p className={`text-3xl font-extrabold mt-1 ${colorClass}`}>{value}</p>
      {sub && <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">{sub}</p>}
    </div>
  );
}

function SkillsCard({ skills }: { skills: { skill: string; count: number }[] }) {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-gray-200 dark:border-slate-700 p-5 shadow-sm col-span-2">
      <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide font-medium mb-3">Top Skills In Demand</p>
      <div className="flex flex-wrap gap-2">
        {skills.slice(0, 10).map((s, i) => (
          <span key={s.skill} className="flex items-center gap-1 text-xs bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 px-2.5 py-1 rounded-full font-medium">
            {s.skill}
            <span className="bg-blue-200 dark:bg-blue-800 text-blue-900 dark:text-blue-100 rounded-full px-1.5 text-xs font-bold">{s.count}</span>
          </span>
        ))}
      </div>
    </div>
  );
}

export function StatsCards({ stats, loading }: { stats: any; loading: boolean }) {
  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white dark:bg-slate-900 rounded-xl border border-gray-200 dark:border-slate-700 p-5 h-24 animate-pulse">
            <div className="h-3 w-20 bg-gray-200 dark:bg-slate-700 rounded mb-3" />
            <div className="h-8 w-16 bg-gray-200 dark:bg-slate-700 rounded" />
          </div>
        ))}
      </div>
    );
  }

  const lastRunStatus = stats?.last_run_status;
  const lastRunColor =
    lastRunStatus === 'done' ? 'text-green-600 dark:text-green-400' :
    lastRunStatus === 'error' ? 'text-red-500 dark:text-red-400' :
    lastRunStatus === 'running' ? 'text-yellow-500 dark:text-yellow-400' :
    'text-gray-400';

  const lastRunTime = stats?.last_run_at
    ? new Date(stats.last_run_at).toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata', hour12: true,
        day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit',
      })
    : undefined;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Total Jobs" value={stats?.total_jobs ?? 0} colorClass="text-blue-600 dark:text-blue-400" />
        <StatCard label="New Today" value={stats?.new_today ?? 0} sub="since midnight" colorClass="text-green-600 dark:text-green-400" />
        <StatCard label="Companies Hiring" value={stats?.companies_hiring ?? 0} colorClass="text-purple-600 dark:text-purple-400" />
        <StatCard
          label="Last Pipeline Run"
          value={lastRunStatus ? lastRunStatus.toUpperCase() : 'Never'}
          sub={lastRunTime}
          colorClass={lastRunColor}
        />
      </div>
      {stats?.top_skills?.length > 0 && (
        <div className="grid grid-cols-1">
          <SkillsCard skills={stats.top_skills} />
        </div>
      )}
    </div>
  );
}
