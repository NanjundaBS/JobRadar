import logging
import re
from datetime import date
from bs4 import BeautifulSoup

from backend.scrapers.base import BaseScraper, RawJob

logger = logging.getLogger(__name__)


class InstahyreScraper(BaseScraper):
    source_name = "instahyre"

    async def fetch_jobs(self, keywords: list[str]) -> list[RawJob]:
        # SCRAPER NOTE: Instahyre has a React frontend.
        # We try their internal API first, then HTML fallback.
        jobs = []

        # Try their public API
        data = await self._get_json(
            "https://www.instahyre.com/api/v1/opportunity/",
            params={
                "search": "devops",
                "experience_min": 2,
                "experience_max": 5,
                "page_size": 20,
            },
            headers={"Referer": "https://www.instahyre.com/"},
        )

        if data and isinstance(data, dict):
            for item in data.get("results", []):
                try:
                    company_data = item.get("company", {})
                    company = company_data.get("name", "Unknown") if isinstance(company_data, dict) else str(company_data)
                    exp_min = item.get("experience_min", 2)
                    exp_max = item.get("experience_max", 5)
                    jobs.append(RawJob(
                        title=item.get("designation", ""),
                        company=company,
                        location=item.get("location", "India"),
                        job_url=f"https://www.instahyre.com/job/{item.get('id', '')}",
                        description=item.get("description", "")[:500],
                        experience_text=f"{exp_min}-{exp_max} years",
                        date_posted=date.today(),
                        source=self.source_name,
                    ))
                except Exception:
                    pass

        # Fallback: HTML scraping
        if not jobs:
            html = await self._get(
                "https://www.instahyre.com/search-jobs/",
                params={"q": "devops"},
                headers={"Referer": "https://www.instahyre.com/"},
            )
            if html:
                jobs.extend(self._parse_instahyre(html))

        logger.info(f"Instahyre: {len(jobs)} jobs")
        return jobs

    def _parse_instahyre(self, html: str) -> list[RawJob]:
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        cards = soup.find_all(["div", "article"], class_=re.compile(r"job|listing|opportunity|card"))
        for card in cards:
            try:
                title_el = card.find(["h2", "h3", "h4", "a"])
                title = title_el.get_text(strip=True) if title_el else ""

                comp_el = card.find(["span", "div"], class_=re.compile(r"company|employer|name"))
                company = comp_el.get_text(strip=True) if comp_el else "Unknown"

                link_el = card.find("a", href=True)
                href = link_el["href"] if link_el else ""
                job_url = href if href.startswith("http") else f"https://www.instahyre.com{href}"

                if title and len(title) > 3:
                    jobs.append(RawJob(
                        title=title,
                        company=company,
                        location="India",
                        job_url=job_url,
                        description="",
                        experience_text="2-5 years",
                        date_posted=date.today(),
                        source=self.source_name,
                    ))
            except Exception:
                pass

        return jobs
