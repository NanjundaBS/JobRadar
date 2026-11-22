import base64
import logging
import uuid
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import httpx
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.models import Job, RunLog

logger = logging.getLogger(__name__)

GMAIL_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


async def get_gmail_access_token() -> Optional[str]:
    """Exchange refresh token for access token."""
    if not settings.GOOGLE_REFRESH_TOKEN:
        logger.warning("No Gmail refresh token configured — email disabled")
        return None

    async with httpx.AsyncClient() as client:
        resp = await client.post(GMAIL_TOKEN_URL, data={
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "refresh_token": settings.GOOGLE_REFRESH_TOKEN,
            "grant_type": "refresh_token",
        }, timeout=15)

        if resp.status_code == 200:
            return resp.json().get("access_token")
        else:
            logger.error(f"Token exchange failed: {resp.status_code} {resp.text}")
            return None


def _score_color(score: int) -> str:
    if score >= 70:
        return "#10b981"
    elif score >= 50:
        return "#f59e0b"
    return "#6b7280"


def build_html_email(jobs: list, run, new_count: int) -> str:
    """Build rich HTML email with job table."""
    now = datetime.now()
    date_str = now.strftime("%d %b %Y, %I:%M %p IST")

    rows = ""
    for job in jobs:
        skills_str = ", ".join((job.matched_skills or [])[:5]) or "—"
        new_badge = (
            '<span style="background:#3b82f6;color:white;padding:1px 6px;border-radius:9px;'
            'font-size:11px;margin-left:4px;">NEW</span>'
        ) if job.is_new else ""
        hr_email_html = (
            f'<a href="mailto:{job.hr_email}" style="color:#3b82f6;">{job.hr_email}</a>'
            + (' <span style="color:#10b981;font-size:11px;" title="Verified">✓</span>' if job.hr_email_verified else "")
        ) if job.hr_email else '<span style="color:#9ca3af;">Not available</span>'
        score_color = _score_color(job.match_score)
        career_link = (
            f'<a href="{job.career_url}" style="color:#3b82f6;font-size:12px;">Careers →</a>'
        ) if job.career_url else "—"
        type_colors = {
            "Startup": "#d1fae5;color:#065f46",
            "Product": "#ede9fe;color:#4c1d95",
            "Service": "#dbeafe;color:#1e40af",
        }
        type_style = type_colors.get(job.company_type, "#f3f4f6;color:#374151")

        rows += f"""
        <tr style="border-bottom:1px solid #f3f4f6;">
          <td style="padding:10px 8px;font-weight:600;white-space:nowrap;">{job.company_name}{new_badge}</td>
          <td style="padding:10px 8px;">
            <span style="background:{type_style};padding:2px 8px;border-radius:9px;font-size:11px;white-space:nowrap;">
              {job.company_type}
            </span>
          </td>
          <td style="padding:10px 8px;">{career_link}</td>
          <td style="padding:10px 8px;font-weight:500;min-width:150px;">{job.job_title}</td>
          <td style="padding:10px 8px;white-space:nowrap;">
            <a href="{job.job_url}" style="background:#2563eb;color:white;padding:4px 10px;border-radius:6px;font-size:12px;text-decoration:none;">Apply →</a>
          </td>
          <td style="padding:10px 8px;font-size:12px;white-space:nowrap;">{job.experience_required or 'Not specified'}</td>
          <td style="padding:10px 8px;font-size:12px;min-width:120px;">{skills_str}</td>
          <td style="padding:10px 8px;font-size:12px;min-width:150px;color:#374151;">{job.why_it_matches or '—'}</td>
          <td style="padding:10px 8px;font-size:12px;min-width:150px;color:#6b7280;">{(job.job_description_short or '')[:120]}...</td>
          <td style="padding:10px 8px;font-size:12px;">{hr_email_html}</td>
          <td style="padding:10px 8px;font-size:12px;">
            <span style="background:#f3f4f6;padding:2px 6px;border-radius:4px;font-size:11px;">{job.source}</span>
          </td>
          <td style="padding:10px 8px;text-align:center;">
            <span style="color:{score_color};font-weight:700;font-size:18px;">{job.match_score}</span>
          </td>
          <td style="padding:10px 8px;font-size:12px;white-space:nowrap;">
            {job.date_posted.strftime('%d %b') if job.date_posted else '—'}
          </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f9fafb;margin:0;padding:20px;">
  <div style="max-width:1300px;margin:0 auto;background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 6px -1px rgba(0,0,0,.1);">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#1e3a8a 0%,#2563eb 100%);padding:36px 32px;color:white;">
      <table style="width:100%"><tr>
        <td>
          <h1 style="margin:0;font-size:30px;font-weight:800;">🎯 JobRadar</h1>
          <p style="margin:8px 0 0;opacity:.85;font-size:16px;">Top DevOps Job Matches · {date_str}</p>
        </td>
        <td style="text-align:right;vertical-align:middle;">
          <a href="{settings.FRONTEND_URL}" style="background:rgba(255,255,255,.2);color:white;padding:10px 20px;border-radius:8px;text-decoration:none;font-size:14px;font-weight:600;">
            Open Dashboard →
          </a>
        </td>
      </tr></table>
    </div>

    <!-- Summary cards -->
    <table style="width:100%;border-bottom:1px solid #e5e7eb;">
      <tr>
        <td style="padding:20px 24px;text-align:center;border-right:1px solid #e5e7eb;">
          <div style="font-size:36px;font-weight:800;color:#1e40af;">{len(jobs)}</div>
          <div style="color:#6b7280;font-size:13px;margin-top:4px;">Jobs Found</div>
        </td>
        <td style="padding:20px 24px;text-align:center;border-right:1px solid #e5e7eb;">
          <div style="font-size:36px;font-weight:800;color:#10b981;">{new_count}</div>
          <div style="color:#6b7280;font-size:13px;margin-top:4px;">New Since Last Run</div>
        </td>
        <td style="padding:20px 24px;text-align:center;border-right:1px solid #e5e7eb;">
          <div style="font-size:36px;font-weight:800;color:#f59e0b;">{max((j.match_score for j in jobs), default=0)}</div>
          <div style="color:#6b7280;font-size:13px;margin-top:4px;">Top Score</div>
        </td>
        <td style="padding:20px 24px;text-align:center;">
          <div style="font-size:36px;font-weight:800;color:#8b5cf6;">{len(set(j.company_name for j in jobs))}</div>
          <div style="color:#6b7280;font-size:13px;margin-top:4px;">Companies</div>
        </td>
      </tr>
    </table>

    <!-- Jobs table -->
    <div style="overflow-x:auto;padding:0 4px;">
      <table style="width:100%;border-collapse:collapse;font-size:13px;">
        <thead>
          <tr style="background:#f8fafc;">
            <th style="padding:12px 8px;text-align:left;font-size:11px;color:#374151;text-transform:uppercase;letter-spacing:.05em;border-bottom:2px solid #e5e7eb;white-space:nowrap;">Company</th>
            <th style="padding:12px 8px;text-align:left;font-size:11px;color:#374151;text-transform:uppercase;letter-spacing:.05em;border-bottom:2px solid #e5e7eb;">Type</th>
            <th style="padding:12px 8px;text-align:left;font-size:11px;color:#374151;text-transform:uppercase;letter-spacing:.05em;border-bottom:2px solid #e5e7eb;">Careers</th>
            <th style="padding:12px 8px;text-align:left;font-size:11px;color:#374151;text-transform:uppercase;letter-spacing:.05em;border-bottom:2px solid #e5e7eb;min-width:150px;">Job Title</th>
            <th style="padding:12px 8px;text-align:left;font-size:11px;color:#374151;text-transform:uppercase;letter-spacing:.05em;border-bottom:2px solid #e5e7eb;">Link</th>
            <th style="padding:12px 8px;text-align:left;font-size:11px;color:#374151;text-transform:uppercase;letter-spacing:.05em;border-bottom:2px solid #e5e7eb;">Exp</th>
            <th style="padding:12px 8px;text-align:left;font-size:11px;color:#374151;text-transform:uppercase;letter-spacing:.05em;border-bottom:2px solid #e5e7eb;">Skills</th>
            <th style="padding:12px 8px;text-align:left;font-size:11px;color:#374151;text-transform:uppercase;letter-spacing:.05em;border-bottom:2px solid #e5e7eb;min-width:150px;">Why Match</th>
            <th style="padding:12px 8px;text-align:left;font-size:11px;color:#374151;text-transform:uppercase;letter-spacing:.05em;border-bottom:2px solid #e5e7eb;min-width:150px;">Description</th>
            <th style="padding:12px 8px;text-align:left;font-size:11px;color:#374151;text-transform:uppercase;letter-spacing:.05em;border-bottom:2px solid #e5e7eb;min-width:160px;">HR Email</th>
            <th style="padding:12px 8px;text-align:left;font-size:11px;color:#374151;text-transform:uppercase;letter-spacing:.05em;border-bottom:2px solid #e5e7eb;">Source</th>
            <th style="padding:12px 8px;text-align:center;font-size:11px;color:#374151;text-transform:uppercase;letter-spacing:.05em;border-bottom:2px solid #e5e7eb;">Score</th>
            <th style="padding:12px 8px;text-align:left;font-size:11px;color:#374151;text-transform:uppercase;letter-spacing:.05em;border-bottom:2px solid #e5e7eb;">Posted</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>

    <!-- Footer -->
    <div style="padding:28px 32px;background:#f8fafc;border-top:1px solid #e5e7eb;text-align:center;">
      <p style="color:#374151;font-size:14px;margin:0;">
        Generated by <strong>JobRadar</strong> &mdash; running automatically at <strong>11:00 AM</strong> and <strong>4:30 PM IST</strong> daily.
      </p>
      <p style="color:#9ca3af;font-size:12px;margin:10px 0 0;">
        Open <a href="{settings.FRONTEND_URL}" style="color:#3b82f6;">your dashboard</a> to filter, sort, and track applications.
        &bull; HR email data sourced from public listings only.
      </p>
    </div>
  </div>
</body>
</html>"""


async def send_job_report_email(run_id: uuid.UUID, db: AsyncSession) -> bool:
    """Fetch jobs for run and send HTML email via Gmail API."""
    try:
        run = await db.get(RunLog, run_id)
        if not run:
            logger.error(f"RunLog {run_id} not found")
            return False

        result = await db.execute(
            select(Job)
            .where(Job.run_id == run_id)
            .order_by(desc(Job.match_score))
            .limit(25)
        )
        jobs = result.scalars().all()

        if not jobs:
            logger.warning("No jobs for this run — skipping email")
            return False

        new_count = sum(1 for j in jobs if j.is_new)
        now = datetime.now()
        subject = f"JobRadar – Top {len(jobs)} DevOps Matches – {now.strftime('%d %b %Y %I:%M %p IST')}"
        html_body = build_html_email(jobs, run, new_count)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = settings.EMAIL_TO
        msg.attach(MIMEText(html_body, "html"))

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        access_token = await get_gmail_access_token()
        if not access_token:
            logger.error("Could not get Gmail access token — email not sent")
            return False

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                GMAIL_SEND_URL,
                headers={"Authorization": f"Bearer {access_token}"},
                json={"raw": raw},
                timeout=30,
            )
            if resp.status_code == 200:
                logger.info(f"Email sent successfully to {settings.EMAIL_TO}")
                return True
            else:
                logger.error(f"Gmail send failed: {resp.status_code} {resp.text}")
                return False

    except Exception as e:
        logger.error(f"Email send error: {e}", exc_info=True)
        return False
