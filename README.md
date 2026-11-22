# 🎯 JobRadar — DevOps Job Intelligence Platform

An intelligent, autonomous AI agent application that continuously scouts, deduplicates, scores, enriches, and alerts DevOps professionals to opportunities matching a **2–4 years experience** profile.

---

## ⚡ Overview & Features

- **Multi-Source Scraping Pipeline**:
  - **Job Boards**: Naukri, Indeed India, Wellfound, Y Combinator (Work at a Startup + HN Who's Hiring), Foundit, LinkedIn Jobs, Cutshort, Instahyre.
  - **Career Crawlers**: 45+ pre-seeded Indian tech companies (Startups, Product companies, and Service giants).
- **Target Experience Enforcement**: Strict filtering for **2–4 years**. Automatically excludes senior/lead/principal (5+ yrs) and freshers/interns (0–1 yrs).
- **Smart Scoring Engine (0–100)**:
  - Skill overlap analysis (AWS, GCP, GitHub Actions, Jenkins, Terraform, Ansible, Docker, Kubernetes, Prometheus, Grafana, Datadog, ELK, Nexus, Tomcat).
  - Experience suitability scoring.
  - Location affinity bonus (India / Remote).
  - Keeps top 25–30 scored matches per cycle.
- **Enrichment & Verified Contacts**:
  - Company categorization: *Startup*, *Product*, or *Service*.
  - Sourced direct career page links and publicly listed or verified talent emails (never guessed or fabricated).
- **Email Agent (Twice Daily)**:
  - Runs automatically via scheduler at **11:00 AM IST** and **4:30 PM IST**.
  - Sends a responsive HTML email table to `nanjundabsom@gmail.com` via Gmail OAuth 2.0.
  - Badges new jobs discovered since the previous run.
- **Live Next.js 14 Dashboard**:
  - Filterable by role, company type, source, status, and minimum score.
  - Real-time search and multi-column sorting.
  - Application lifecycle status: `New`, `Applied`, `Saved`, `Ignored`.
  - Export to CSV functionality for spreadsheet tracking.
  - Summary metrics and top skills in demand.
  - Dark / Light mode toggle.
  - Manual "Refresh Now" trigger button.

---

## 🏗️ Architecture

```
                                  ┌─────────────────────────────┐
                                  │      Job Boards & APIs      │
                                  │ Naukri, Indeed, Wellfound,  │
                                  │ YC, LinkedIn, Cutshort, etc │
                                  └──────────────┬──────────────┘
                                                 │
                                                 ▼
┌──────────────────────────┐       ┌────────────────────────────┐
│ APScheduler (Cron)       ├──────►│ Pipeline Engine            │
│ 11:00 AM & 4:30 PM IST   │       │ Scrape ➔ Dedupe ➔ Score    │
└──────────────────────────┘       └──────────────┬─────────────┘
                                                 │
                                                 ▼
                                   ┌────────────────────────────┐
                                   │ PostgreSQL Database (Async)│
                                   │ Jobs, Companies, RunLogs   │
                                   └──────────────┬─────────────┘
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        ▼                                                 ▼
        ┌───────────────────────────────┐                 ┌──────────────────────────────┐
        │ Gmail API OAuth 2.0           │                 │ Next.js 14 Dashboard         │
        │ HTML Email to nanjundabsom    │                 │ Live UI on http://localhost  │
        └───────────────────────────────┘                 └──────────────────────────────┘
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy 2.0 (asyncio + asyncpg), Pydantic v2, APScheduler.
- **Scrapers**: HTTPX (retries + backoff), BeautifulSoup4, Playwright Chromium.
- **Database**: PostgreSQL 16.
- **Frontend**: Next.js 14 (App Router), React 18, Tailwind CSS, SWR, TypeScript.
- **Email Delivery**: Google Gmail REST API via OAuth 2.0 Bearer tokens.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ (Node 20 recommended)
- PostgreSQL (or Docker)

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure your database connection string and email are set:
```ini
DATABASE_URL=postgresql+asyncpg://jobradar:jobradar@localhost:5432/jobradar
EMAIL_TO=nanjundabsom@gmail.com
EMAIL_FROM=nanjundabsom@gmail.com
```

### 3. Setting Up Gmail OAuth
To allow JobRadar to send your twice-daily HTML email reports:
1. Head to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project and enable the **Gmail API** under *APIs & Services*.
3. Go to *Credentials* ➔ *Create Credentials* ➔ *OAuth client ID* (Application type: **Desktop App**).
4. Export your credentials:
   ```bash
   set GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
   set GOOGLE_CLIENT_SECRET=your_client_secret
   ```
5. Run the helper script to complete browser sign-in and receive your refresh token:
   ```bash
   python scripts/get_gmail_token.py
   ```
6. Add the output `GOOGLE_REFRESH_TOKEN` to your `.env`.

---

## 🐳 Quick Run with Docker Compose

To launch PostgreSQL, FastAPI Backend, and Next.js Frontend with one command:
```bash
docker compose up -d --build
```
- **Dashboard**: `http://localhost:3000`
- **FastAPI Docs**: `http://localhost:8000/docs`

---

## 💻 Manual Local Development

### Step 1: Run PostgreSQL
Ensure a Postgres instance is running locally with database `jobradar`:
```sql
CREATE DATABASE jobradar;
CREATE USER jobradar WITH PASSWORD 'jobradar';
GRANT ALL PRIVILEGES ON DATABASE jobradar TO jobradar;
```

### Step 2: Seed Companies
```bash
python scripts/seed_companies.py
```

### Step 3: Start the Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 4: Start the Frontend
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:3000` to interact with your live dashboard!

---

## 📊 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/jobs` | `GET` | List filtered, paginated & sorted DevOps jobs |
| `/api/jobs/{id}/status` | `PATCH` | Update status (`new`, `applied`, `saved`, `ignored`) |
| `/api/jobs/export/csv` | `GET` | Export current filtered query as CSV |
| `/api/stats` | `GET` | Summary counters, top skills & last pipeline status |
| `/api/runs` | `GET` | History of all scrape & email pipeline runs |
| `/api/runs/trigger` | `POST` | Trigger an immediate ad-hoc pipeline execution |
| `/api/status` | `GET` | Health check endpoint |

---

## ⏰ Cron Schedule

The scheduler runs in `backend/scheduler.py` using `Asia/Kolkata` timezone:
- **Morning Run**: `11:00 AM IST`
- **Afternoon Run**: `04:30 PM IST`

Each scheduled run executes the pipeline, records job metrics, commits updates to PostgreSQL, and delivers the top 25 matches directly to your inbox.
