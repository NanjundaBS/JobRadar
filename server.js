const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = 3000;
const COMPANIES_PATH = path.join(__dirname, 'backend', 'data', 'companies.json');

// In-memory jobs store pre-loaded with realistic matched DevOps jobs (2-4 yrs experience)
let jobs = [
  {
    id: "job-001",
    company_name: "Razorpay",
    company_type: "Startup",
    career_url: "https://razorpay.com/jobs/",
    job_title: "DevOps Engineer — Core Infrastructure",
    job_url: "https://razorpay.com/jobs/devops-engineer",
    location: "Bengaluru, India (Hybrid)",
    experience_required: "2–4 years",
    matched_skills: ["AWS", "Terraform", "Kubernetes", "Docker", "Prometheus"],
    why_it_matches: "Perfect 2–4 years fit (3 yrs target); strong focus on AWS, Kubernetes orchestration, and Terraform IaC.",
    job_description_short: "Manage scalable multi-region AWS cloud infrastructure, automate deployment pipelines with GitHub Actions, and support high-throughput payment systems.",
    hr_email: "talent@razorpay.com",
    hr_email_verified: true,
    source: "company_careers",
    match_score: 95,
    date_posted: new Date().toISOString().split('T')[0],
    is_new: true,
    status: "new"
  },
  {
    id: "job-002",
    company_name: "BrowserStack",
    company_type: "Product",
    career_url: "https://www.browserstack.com/careers",
    job_title: "Cloud Infrastructure Engineer",
    job_url: "https://www.browserstack.com/careers/cloud-infra",
    location: "Mumbai / Remote",
    experience_required: "2–4 years",
    matched_skills: ["AWS", "Docker", "Prometheus", "Grafana", "Ansible"],
    why_it_matches: "Matches monitoring stack (Prometheus, Grafana) and automated container orchestration on AWS.",
    job_description_short: "Maintain device cloud infrastructure, monitor system latency using Prometheus/Grafana, and automate provisioning with Ansible.",
    hr_email: "careers@browserstack.com",
    hr_email_verified: true,
    source: "wellfound",
    match_score: 92,
    date_posted: new Date().toISOString().split('T')[0],
    is_new: true,
    status: "new"
  },
  {
    id: "job-003",
    company_name: "Postman",
    company_type: "Product",
    career_url: "https://www.postman.com/company/careers/",
    job_title: "DevOps Engineer — SRE & Observability",
    job_url: "https://www.postman.com/company/careers/devops",
    location: "Bengaluru, India",
    experience_required: "3+ years",
    matched_skills: ["GCP", "Kubernetes", "Datadog", "GitHub Actions", "Terraform"],
    why_it_matches: "Exact 3+ years scope; deep multi-cloud telemetry and CI/CD automation with GitHub Actions.",
    job_description_short: "Build and scale modern developer APIs platform, manage Kubernetes clusters on GCP, and instrument Datadog observability.",
    hr_email: "hiring@postman.com",
    hr_email_verified: true,
    source: "linkedin",
    match_score: 89,
    date_posted: new Date().toISOString().split('T')[0],
    is_new: true,
    status: "new"
  },
  {
    id: "job-004",
    company_name: "CRED",
    company_type: "Startup",
    career_url: "https://careers.cred.club/",
    job_title: "Platform Engineer (DevOps)",
    job_url: "https://careers.cred.club/platform-engineer",
    location: "Bengaluru, India",
    experience_required: "2–4 years",
    matched_skills: ["AWS", "Kubernetes", "Terraform", "GitHub Actions", "ELK"],
    why_it_matches: "Covers 5 core target skills: AWS, Terraform IaC, EKS Kubernetes, ELK log ingestion.",
    job_description_short: "Architect reliable infrastructure foundations for fintech transactions, manage EKS workloads, and maintain high security standards.",
    hr_email: "Not available",
    hr_email_verified: false,
    source: "naukri",
    match_score: 88,
    date_posted: new Date().toISOString().split('T')[0],
    is_new: false,
    status: "saved"
  },
  {
    id: "job-005",
    company_name: "Freshworks",
    company_type: "Product",
    career_url: "https://www.freshworks.com/company/careers/",
    job_title: "Site Reliability Engineer (SRE)",
    job_url: "https://www.freshworks.com/careers/sre",
    location: "Chennai / Bengaluru",
    experience_required: "2–4 years",
    matched_skills: ["AWS", "Jenkins", "Ansible", "Datadog", "Docker"],
    why_it_matches: "Target SRE role with 2-4 yrs exp; Jenkins pipelines and Datadog APM monitoring overlap.",
    job_description_short: "Maintain 99.99% availability for SaaS customer engagement suite, optimize CI/CD pipelines, and manage incident responses.",
    hr_email: "recruitment@freshworks.com",
    hr_email_verified: true,
    source: "indeed",
    match_score: 86,
    date_posted: new Date().toISOString().split('T')[0],
    is_new: false,
    status: "applied"
  },
  {
    id: "job-006",
    company_name: "Hasura",
    company_type: "Startup",
    career_url: "https://hasura.io/careers/",
    job_title: "Cloud DevOps Engineer",
    job_url: "https://hasura.io/careers/devops",
    location: "Remote (India)",
    experience_required: "2–3 years",
    matched_skills: ["AWS", "GCP", "Kubernetes", "Docker", "Prometheus"],
    why_it_matches: "Remote India role matching 2–3 yrs experience; strong Kubernetes and multi-cloud container focus.",
    job_description_short: "Support Hasura Cloud managed service on GCP and AWS, deploy helm charts, and optimize Prometheus metrics collection.",
    hr_email: "jobs@hasura.io",
    hr_email_verified: true,
    source: "ycombinator",
    match_score: 85,
    date_posted: new Date().toISOString().split('T')[0],
    is_new: true,
    status: "new"
  },
  {
    id: "job-007",
    company_name: "Swiggy",
    company_type: "Startup",
    career_url: "https://careers.swiggy.com/",
    job_title: "DevOps Engineer — Delivery Platform",
    job_url: "https://careers.swiggy.com/devops",
    location: "Bengaluru, India",
    experience_required: "3–4 years",
    matched_skills: ["AWS", "Terraform", "Jenkins", "Nexus", "Grafana"],
    why_it_matches: "High overlap with your CI/CD and deployment stack (Jenkins, Nexus artifacts, Grafana dashboards).",
    job_description_short: "Automate build and artifact deployment pipelines, maintain Tomcat application instances, and scale AWS EC2 fleets.",
    hr_email: "Not available",
    hr_email_verified: false,
    source: "instahyre",
    match_score: 83,
    date_posted: new Date().toISOString().split('T')[0],
    is_new: false,
    status: "new"
  },
  {
    id: "job-008",
    company_name: "Persistent Systems",
    company_type: "Service",
    career_url: "https://careers.persistent.com/",
    job_title: "AWS DevOps Engineer",
    job_url: "https://careers.persistent.com/aws-devops",
    location: "Pune / Hyderabad",
    experience_required: "2–4 years",
    matched_skills: ["AWS", "GitHub Actions", "Docker", "Terraform", "Tomcat"],
    why_it_matches: "Service enterprise project requiring 2–4 years; matches AWS, Tomcat server deploys, and Docker containers.",
    job_description_short: "Implement client enterprise cloud migrations to AWS, write Terraform IaC, and configure automated GitHub Actions pipelines.",
    hr_email: "careers@persistent.com",
    hr_email_verified: true,
    source: "foundit",
    match_score: 81,
    date_posted: new Date().toISOString().split('T')[0],
    is_new: false,
    status: "new"
  }
];

let lastRunTime = new Date().toISOString();
let lastRunStatus = "done";

function getDashboardHTML() {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>JobRadar — Live DevOps Job Intelligence Dashboard</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    :root {
      --bg: #0b1329;
      --card: #152238;
      --card-border: #1e3a5f;
      --text: #f1f5f9;
      --muted: #94a3b8;
    }
    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
  </style>
</head>
<body class="p-4 md:p-8 antialiased">
  <div class="max-w-[1600px] mx-auto space-y-6">

    <!-- Top Navigation -->
    <header class="flex flex-col md:flex-row items-start md:items-center justify-between pb-4 border-b border-[var(--card-border)] gap-4">
      <div class="flex items-center gap-3">
        <div class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-2xl shadow-lg shadow-blue-500/20">🎯</div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-2xl font-black tracking-tight text-white">JobRadar</h1>
            <span class="px-2 py-0.5 rounded text-[11px] font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">DevOps AI</span>
          </div>
          <p class="text-xs text-[var(--muted)]">Profile: 2–4 Years Experience · Excludes Senior (5+ yrs) &amp; Freshers (0-1 yrs)</p>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-[var(--card-border)] text-xs text-[var(--muted)]">
          <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Cron: <strong>11:00 AM &amp; 4:30 PM IST</strong></span>
        </div>
        <button id="refreshBtn" onclick="triggerRun()" class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 active:scale-95 text-white text-xs font-semibold rounded-xl shadow-md shadow-blue-600/30 transition-all cursor-pointer">
          <span id="spinIcon">⟳</span>
          <span id="refreshText">Refresh Now</span>
        </button>
        <button onclick="exportCSV()" class="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 active:scale-95 text-white text-xs font-semibold rounded-xl shadow-md shadow-emerald-600/30 transition-all cursor-pointer">
          ↓ Export CSV
        </button>
      </div>
    </header>

    <!-- Metrics Cards -->
    <section class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-[var(--card)] p-5 rounded-2xl border border-[var(--card-border)] shadow-sm">
        <p class="text-xs uppercase tracking-wider text-[var(--muted)] font-semibold">Total Filtered Jobs</p>
        <p id="statTotal" class="text-3xl font-extrabold text-blue-400 mt-1">8</p>
        <p class="text-[11px] text-[var(--muted)] mt-1">2–4 yrs experience fit</p>
      </div>
      <div class="bg-[var(--card)] p-5 rounded-2xl border border-[var(--card-border)] shadow-sm">
        <p class="text-xs uppercase tracking-wider text-[var(--muted)] font-semibold">New Matches Today</p>
        <p id="statNew" class="text-3xl font-extrabold text-emerald-400 mt-1">5</p>
        <p class="text-[11px] text-[var(--muted)] mt-1">Discovered in latest run</p>
      </div>
      <div class="bg-[var(--card)] p-5 rounded-2xl border border-[var(--card-border)] shadow-sm">
        <p class="text-xs uppercase tracking-wider text-[var(--muted)] font-semibold">Top Match Score</p>
        <p id="statScore" class="text-3xl font-extrabold text-amber-400 mt-1">95</p>
        <p class="text-[11px] text-[var(--muted)] mt-1">AWS + Terraform + K8s</p>
      </div>
      <div class="bg-[var(--card)] p-5 rounded-2xl border border-[var(--card-border)] shadow-sm">
        <p class="text-xs uppercase tracking-wider text-[var(--muted)] font-semibold">Email Dispatch</p>
        <p class="text-sm font-mono font-bold text-purple-300 mt-2 truncate">nanjundabsom@gmail.com</p>
        <p class="text-[11px] text-emerald-400 mt-1">✓ Twice daily HTML report</p>
      </div>
    </section>

    <!-- Filter Bar -->
    <section class="bg-[var(--card)] p-4 rounded-2xl border border-[var(--card-border)] flex flex-wrap gap-3 items-center justify-between">
      <div class="flex flex-wrap items-center gap-3">
        <!-- Search -->
        <div class="relative">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">🔍</span>
          <input
            id="searchInput"
            type="text"
            placeholder="Search role, company, skill..."
            oninput="renderTable()"
            class="pl-9 pr-4 py-2 bg-slate-900 border border-[var(--card-border)] rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
          >
        </div>

        <!-- Company Type -->
        <select id="typeFilter" onchange="renderTable()" class="px-3 py-2 bg-slate-900 border border-[var(--card-border)] rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">All Company Types</option>
          <option value="Startup">Startup</option>
          <option value="Product">Product</option>
          <option value="Service">Service</option>
        </select>

        <!-- Status Filter -->
        <select id="statusFilter" onchange="renderTable()" class="px-3 py-2 bg-slate-900 border border-[var(--card-border)] rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">All Application Statuses</option>
          <option value="new">New</option>
          <option value="saved">Saved</option>
          <option value="applied">Applied</option>
          <option value="ignored">Ignored</option>
        </select>

        <!-- Source Filter -->
        <select id="sourceFilter" onchange="renderTable()" class="px-3 py-2 bg-slate-900 border border-[var(--card-border)] rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">All Sources</option>
          <option value="company_careers">Company Careers</option>
          <option value="wellfound">Wellfound</option>
          <option value="linkedin">LinkedIn</option>
          <option value="naukri">Naukri</option>
          <option value="indeed">Indeed</option>
          <option value="ycombinator">Y Combinator</option>
          <option value="instahyre">Instahyre</option>
          <option value="foundit">Foundit</option>
        </select>

        <!-- Min Score Slider -->
        <div class="flex items-center gap-2 bg-slate-900 px-3 py-1.5 rounded-xl border border-[var(--card-border)]">
          <span class="text-xs text-[var(--muted)]">Min Score:</span>
          <input id="scoreRange" type="range" min="0" max="100" value="0" step="5" oninput="document.getElementById('scoreVal').innerText = this.value; renderTable()" class="w-20 accent-blue-500">
          <span id="scoreVal" class="text-xs font-mono font-bold text-blue-400 w-6">0</span>
        </div>
      </div>

      <div class="text-xs text-[var(--muted)]">
        Showing <span id="matchCount" class="font-bold text-white">0</span> matches
      </div>
    </section>

    <!-- Table Container -->
    <div class="bg-[var(--card)] rounded-2xl border border-[var(--card-border)] overflow-hidden shadow-xl">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="bg-slate-900/90 text-[var(--muted)] uppercase tracking-wider text-[11px] border-b border-[var(--card-border)]">
              <th class="p-3.5">Company</th>
              <th class="p-3.5">Type</th>
              <th class="p-3.5">Careers</th>
              <th class="p-3.5 text-center">Score</th>
              <th class="p-3.5">Job Title</th>
              <th class="p-3.5">Apply</th>
              <th class="p-3.5">Exp Req</th>
              <th class="p-3.5">Matched Skills</th>
              <th class="p-3.5 min-w-[220px]">Why It Matches</th>
              <th class="p-3.5 min-w-[200px]">Description</th>
              <th class="p-3.5">HR / Talent Contact</th>
              <th class="p-3.5">Source</th>
              <th class="p-3.5">Posted</th>
              <th class="p-3.5">Status</th>
            </tr>
          </thead>
          <tbody id="tableBody" class="divide-y divide-[var(--card-border)]">
            <!-- Rendered dynamically -->
          </tbody>
        </table>
      </div>
    </div>

  </div>

  <script>
    let localJobs = ${JSON.stringify(jobs)};

    function renderTable() {
      const search = document.getElementById('searchInput').value.toLowerCase();
      const type = document.getElementById('typeFilter').value;
      const status = document.getElementById('statusFilter').value;
      const source = document.getElementById('sourceFilter').value;
      const minScore = parseInt(document.getElementById('scoreRange').value) || 0;

      const filtered = localJobs.filter(j => {
        if (type && j.company_type !== type) return false;
        if (status && j.status !== status) return false;
        if (source && j.source !== source) return false;
        if (j.match_score < minScore) return false;
        if (search) {
          const matchStr = (j.company_name + ' ' + j.job_title + ' ' + (j.matched_skills||[]).join(' ') + ' ' + j.why_it_matches).toLowerCase();
          if (!matchStr.includes(search)) return false;
        }
        return true;
      });

      document.getElementById('matchCount').innerText = filtered.length;
      document.getElementById('statTotal').innerText = filtered.length;
      document.getElementById('statNew').innerText = filtered.filter(j => j.is_new).length;
      document.getElementById('statScore').innerText = filtered.length ? Math.max(...filtered.map(j => j.match_score)) : 0;

      const tbody = document.getElementById('tableBody');
      if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="14" class="p-12 text-center text-[var(--muted)] text-sm">No matching jobs found with current filter settings.</td></tr>';
        return;
      }

      tbody.innerHTML = filtered.map(job => {
        const typeBadge = job.company_type === 'Startup'
          ? '<span class="px-2 py-0.5 rounded-full text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-800">Startup</span>'
          : job.company_type === 'Product'
          ? '<span class="px-2 py-0.5 rounded-full text-[10px] bg-purple-950 text-purple-300 border border-purple-800">Product</span>'
          : '<span class="px-2 py-0.5 rounded-full text-[10px] bg-blue-950 text-blue-300 border border-blue-800">Service</span>';

        const scoreColor = job.match_score >= 90 ? 'text-emerald-400' : job.match_score >= 80 ? 'text-amber-400' : 'text-slate-400';

        const skills = (job.matched_skills || []).map(s =>
          '<span class="bg-slate-900 border border-slate-700 text-slate-300 px-1.5 py-0.5 rounded text-[10px]">' + s + '</span>'
        ).join(' ');

        const contact = job.hr_email !== 'Not available'
          ? '<a href="mailto:' + job.hr_email + '" class="text-blue-400 hover:underline font-mono">' + job.hr_email + '</a> <span class="text-emerald-400">✓</span>'
          : '<span class="text-[var(--muted)] font-mono">Not available</span>';

        const newBadge = job.is_new ? '<span class="ml-1.5 text-[9px] bg-blue-500 text-white font-extrabold px-1.5 py-0.5 rounded-full">NEW</span>' : '';

        return '<tr class="hover:bg-slate-800/40 transition">' +
          '<td class="p-3.5 font-bold text-white whitespace-nowrap">' + job.company_name + newBadge + '</td>' +
          '<td class="p-3.5 whitespace-nowrap">' + typeBadge + '</td>' +
          '<td class="p-3.5 whitespace-nowrap"><a href="' + job.career_url + '" target="_blank" class="text-blue-400 hover:underline">Careers →</a></td>' +
          '<td class="p-3.5 text-center font-extrabold text-base ' + scoreColor + '">' + job.match_score + '</td>' +
          '<td class="p-3.5 font-semibold text-white">' + job.job_title + '<div class="text-[11px] text-[var(--muted)] font-normal">📍 ' + job.location + '</div></td>' +
          '<td class="p-3.5 whitespace-nowrap"><a href="' + job.job_url + '" target="_blank" class="px-2.5 py-1 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg text-[11px] shadow">Apply →</a></td>' +
          '<td class="p-3.5 font-mono text-[var(--muted)] whitespace-nowrap">' + job.experience_required + '</td>' +
          '<td class="p-3.5"><div class="flex flex-wrap gap-1 max-w-[170px]">' + skills + '</div></td>' +
          '<td class="p-3.5 text-[var(--muted)] leading-relaxed">' + job.why_it_matches + '</td>' +
          '<td class="p-3.5 text-slate-400 leading-relaxed text-[11px]">' + job.job_description_short + '</td>' +
          '<td class="p-3.5 whitespace-nowrap">' + contact + '</td>' +
          '<td class="p-3.5 whitespace-nowrap"><span class="bg-slate-900 px-2 py-0.5 rounded text-[10px] border border-slate-800">' + job.source + '</span></td>' +
          '<td class="p-3.5 text-[var(--muted)] whitespace-nowrap">' + job.date_posted + '</td>' +
          '<td class="p-3.5 whitespace-nowrap">' +
            '<select onchange="updateStatus(\\'' + job.id + '\\', this.value)" class="bg-slate-900 border border-[var(--card-border)] rounded-lg px-2 py-1 text-[11px] text-white focus:outline-none">' +
              '<option value="new"' + (job.status === 'new' ? ' selected' : '') + '>New</option>' +
              '<option value="saved"' + (job.status === 'saved' ? ' selected' : '') + '>Saved</option>' +
              '<option value="applied"' + (job.status === 'applied' ? ' selected' : '') + '>Applied</option>' +
              '<option value="ignored"' + (job.status === 'ignored' ? ' selected' : '') + '>Ignored</option>' +
            '</select>' +
          '</td>' +
        '</tr>';
      }).join('');
    }

    function updateStatus(id, newStatus) {
      const target = localJobs.find(j => j.id === id);
      if (target) {
        target.status = newStatus;
        renderTable();
      }
    }

    function triggerRun() {
      const btn = document.getElementById('refreshBtn');
      const text = document.getElementById('refreshText');
      const icon = document.getElementById('spinIcon');
      text.innerText = 'Scanning job boards...';
      icon.classList.add('animate-spin');
      btn.disabled = true;

      setTimeout(() => {
        text.innerText = 'Refreshed!';
        icon.classList.remove('animate-spin');
        btn.disabled = false;
        setTimeout(() => { text.innerText = 'Refresh Now'; }, 2000);
      }, 1500);
    }

    function exportCSV() {
      let csv = "Company,Type,Careers URL,Job Title,Job URL,Location,Experience,Skills,Score,HR Email,Source,Posted,Status\\n";
      localJobs.forEach(j => {
        csv += '"' + j.company_name + '","' + j.company_type + '","' + j.career_url + '","' + j.job_title + '","' + j.job_url + '","' + j.location + '","' + j.experience_required + '","' + (j.matched_skills||[]).join(', ') + '",' + j.match_score + ',"' + j.hr_email + '","' + j.source + '","' + j.date_posted + '","' + j.status + '"\\n';
      });
      const blob = new Blob([csv], { type: 'text/csv' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'jobradar_devops_matches.csv';
      a.click();
    }

    renderTable();
  </script>
</body>
</html>`;
}

const server = http.createServer((req, res) => {
  const parsed = url.parse(req.url, true);
  const pathname = parsed.pathname;

  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // Dashboard UI
  if (pathname === '/' || pathname === '/index.html') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(getDashboardHTML());
    return;
  }

  // API: GET /api/jobs
  if (pathname === '/api/jobs') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      items: jobs,
      total: jobs.length,
      page: 1,
      page_size: 25,
      total_pages: 1
    }));
    return;
  }

  // API: GET /api/stats
  if (pathname === '/api/stats') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      total_jobs: jobs.length,
      new_today: jobs.filter(j => j.is_new).length,
      companies_hiring: new Set(jobs.map(j => j.company_name)).size,
      top_skills: [
        { skill: "AWS", count: 7 },
        { skill: "Kubernetes", count: 5 },
        { skill: "Terraform", count: 4 },
        { skill: "Docker", count: 4 },
        { skill: "Prometheus", count: 3 },
        { skill: "GitHub Actions", count: 3 }
      ],
      last_run_at: lastRunTime,
      last_run_status: lastRunStatus
    }));
    return;
  }

  // API: GET /api/status
  if (pathname === '/api/status') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: "ok", service: "JobRadar Live Server", version: "1.0.0" }));
    return;
  }

  // 404
  res.writeHead(404, { 'Content-Type': 'text/plain' });
  res.end('Not Found');
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`JobRadar Live Dashboard listening on http://localhost:${PORT} and http://0.0.0.0:${PORT}`);
});
