import logging
import re
from datetime import date
from bs4 import BeautifulSoup

from backend.scrapers.base import BaseScraper, RawJob

logger = logging.getLogger(__name__)


class FounditScraper(BaseScraper):
    source_name = "foundit"

    async def fetch_jobs(self, keywords: list[str]) -> list[RawJob]:
        # SCRAPER NOTE: Foundit (formerly Monster India) is JS-heavy.
        # We try their search URL with HTML parsing.
        jobs = []

        for q in ["devops engineer", "cloud engineer", "aws devops"]:
            html = await self._get(
                "https://www.foundit.in/srp/results",
                params={"query": q, "location": "India"},
                headers={"Referer": "https://www.foundit.in/"},
            )
            if html:
                parsed = self._parse_foundit(html)
                jobs.extend(parsed)

        logger.info(f"Foundit: {len(jobs)} jobs")
        return jobs

    def _parse_foundit(self, html: str) -> list[RawJob]:
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        cards = soup.find_all(["div", "article"], class_=re.compile(
            r"srpResultCardContainer|job-card|card-apply|jobCard|result-item"
        ))

        for card in cards:
            try:
                title_el = card.find(["a", "h3", "h2"], class_=re.compile(r"title|jobTitle|position|job-title"))
                title = title_el.get_text(strip=True) if title_el else ""

                comp_el = card.find(["span", "a", "div"], class_=re.compile(r"company|companyName|employer"))
                company = comp_el.get_text(strip=True) if comp_el else ""

                loc_el = card.find(["span", "div"], class_=re.compile(r"location|loc|city"))
                location = loc_el.get_text(strip=True) if loc_el else "India"

                exp_el = card.find(["span"], class_=re.compile(r"exp|experience|yrs"))
                exp = exp_el.get_text(strip=True) if exp_el else ""

                link_el = title_el if title_el and title_el.name == "a" else card.find("a", href=True)
                href = link_el["href"] if link_el else ""
                job_url = href if href.startswith("http") else f"https://www.foundit.in{href}"

                if title and len(title) > 3:
                    jobs.append(RawJob(
                        title=title,
                        company=company or "Unknown",
                        location=location,
                        job_url=job_url,
                        description="",
                        experience_text=exp,
                        date_posted=date.today(),
                        source=self.source_name,
                    ))
            except Exception as e:
                logger.debug(f"Foundit parse error: {e}")

        return jobs
