import logging
import re
from datetime import date, timedelta
from typing import Optional
from bs4 import BeautifulSoup

from backend.scrapers.base import BaseScraper, RawJob

logger = logging.getLogger(__name__)

DEVOPS_ROLES = [
    "devops-engineer",
    "cloud-engineer",
    "site-reliability-engineer",
    "platform-engineer",
    "infrastructure-engineer",
]


class WellfoundScraper(BaseScraper):
    source_name = "wellfound"

    async def fetch_jobs(self, keywords: list[str]) -> list[RawJob]:
        # SCRAPER NOTE: Wellfound requires JS for full job listings.
        # We use their public search URL and parse HTML job cards.
        # Auth-gated data (salary, equity) is skipped.
        jobs = []

        for role in DEVOPS_ROLES[:3]:
            url = f"https://wellfound.com/jobs?role={role}&locationTag=India"
            html = await self._get(url, headers={"Referer": "https://wellfound.com/"})
            if not html:
                continue

            parsed = self._parse_wellfound(html, url)
            jobs.extend(parsed)
            logger.info(f"Wellfound [{role}]: {len(parsed)} jobs")

        return jobs

    def _parse_wellfound(self, html: str, source_url: str) -> list[RawJob]:
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        # Wellfound uses React; look for JSON in script tags first
        for script in soup.find_all("script", type="application/json"):
            try:
                import json
                data = json.loads(script.string or "")
                if isinstance(data, dict) and "jobs" in data:
                    for item in data["jobs"]:
                        job = self._parse_json_item(item, source_url)
                        if job:
                            jobs.append(job)
            except Exception:
                pass

        # Fallback: HTML card parsing
        if not jobs:
            cards = soup.find_all(["div", "li"], class_=re.compile(
                r"styles_component|JobListing|job-listing|startup-link|result"
            ))
            for card in cards:
                try:
                    title_el = card.find(["a", "h3", "h2"], class_=re.compile(r"title|role|position|name"))
                    title = title_el.get_text(strip=True) if title_el else ""

                    comp_el = card.find(["span", "h2", "div"], class_=re.compile(r"startup|company|name"))
                    company = comp_el.get_text(strip=True) if comp_el else "Unknown"

                    link_el = card.find("a", href=True)
                    job_url = link_el["href"] if link_el else source_url
                    if job_url and not job_url.startswith("http"):
                        job_url = f"https://wellfound.com{job_url}"

                    loc_el = card.find(["span"], class_=re.compile(r"location|remote|loc"))
                    location = loc_el.get_text(strip=True) if loc_el else "India"

                    desc_el = card.find(["p", "div"], class_=re.compile(r"description|snippet|desc"))
                    description = desc_el.get_text(strip=True) if desc_el else ""

                    if title and len(title) > 3:
                        jobs.append(RawJob(
                            title=title[:200],
                            company=company,
                            location=location,
                            job_url=job_url,
                            description=description,
                            experience_text=description,
                            date_posted=date.today(),
                            source=self.source_name,
                            career_url=source_url,
                        ))
                except Exception as e:
                    logger.debug(f"Wellfound card parse error: {e}")

        return jobs

    def _parse_json_item(self, item: dict, source_url: str) -> Optional[RawJob]:
        try:
            title = item.get("title") or item.get("role", "")
            company = (item.get("company") or {}).get("name", "Unknown")
            job_url = item.get("url") or item.get("link") or source_url
            location = item.get("location") or item.get("remote_ok", "India")
            description = item.get("description") or item.get("job_type", "")
            if isinstance(location, bool):
                location = "Remote" if location else "India"
            if title:
                return RawJob(
                    title=title,
                    company=company,
                    location=str(location),
                    job_url=job_url,
                    description=str(description)[:500],
                    experience_text=str(description)[:200],
                    date_posted=date.today(),
                    source=self.source_name,
                    career_url=source_url,
                )
        except Exception:
            pass
        return None
