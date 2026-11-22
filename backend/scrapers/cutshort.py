import logging
import re
from datetime import date
from bs4 import BeautifulSoup

from backend.scrapers.base import BaseScraper, RawJob

logger = logging.getLogger(__name__)


class CutshortScraper(BaseScraper):
    source_name = "cutshort"

    async def fetch_jobs(self, keywords: list[str]) -> list[RawJob]:
        # SCRAPER NOTE: Cutshort is a React SPA; direct HTML scraping may yield limited results.
        # Their public job pages are accessible without auth.
        jobs = []

        urls = [
            "https://cutshort.io/jobs/devops-cloud-sre-platform",
            "https://cutshort.io/jobs/cloud-infrastructure",
        ]

        for url in urls:
            html = await self._get(url, headers={"Referer": "https://cutshort.io/"})
            if html:
                parsed = self._parse_cutshort(html, url)
                jobs.extend(parsed)

        logger.info(f"Cutshort: {len(jobs)} jobs")
        return jobs

    def _parse_cutshort(self, html: str, source_url: str) -> list[RawJob]:
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        cards = soup.find_all(["div", "article"], class_=re.compile(r"job|listing|card|JobCard|opportunity"))

        for card in cards:
            try:
                title_el = card.find(["h2", "h3", "h4", "a"])
                title = title_el.get_text(strip=True) if title_el else ""

                comp_els = card.find_all(["span", "p", "div"])
                company = comp_els[1].get_text(strip=True) if len(comp_els) > 1 else "Unknown"

                link_el = card.find("a", href=True)
                href = link_el["href"] if link_el else ""
                job_url = href if href.startswith("http") else f"https://cutshort.io{href}"

                desc_el = card.find(["p", "div"], class_=re.compile(r"desc|snippet|skill|tag"))
                desc = desc_el.get_text(strip=True) if desc_el else ""

                exp_el = card.find(["span"], class_=re.compile(r"exp|year|experience"))
                exp = exp_el.get_text(strip=True) if exp_el else "2-5 years"

                if title and len(title) > 3:
                    jobs.append(RawJob(
                        title=title,
                        company=company,
                        location="India",
                        job_url=job_url or source_url,
                        description=desc,
                        experience_text=f"{exp} {desc}",
                        date_posted=date.today(),
                        source=self.source_name,
                        career_url=source_url,
                    ))
            except Exception as e:
                logger.debug(f"Cutshort parse error: {e}")

        return jobs
