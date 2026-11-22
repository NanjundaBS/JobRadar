import logging
import re
from datetime import date, datetime
from bs4 import BeautifulSoup

from backend.scrapers.base import BaseScraper, RawJob

logger = logging.getLogger(__name__)


class LinkedInScraper(BaseScraper):
    source_name = "linkedin"

    # LinkedIn experience level filters: 2=Entry (1-3yr), 3=Associate (3-5yr)
    SEARCHES = [
        {"keywords": "DevOps Engineer", "f_E": "2,3"},
        {"keywords": "Cloud Engineer India", "f_E": "2,3"},
        {"keywords": "Platform Engineer India", "f_E": "2,3"},
        {"keywords": "Site Reliability Engineer India", "f_E": "2,3"},
    ]

    async def fetch_jobs(self, keywords: list[str]) -> list[RawJob]:
        # SCRAPER NOTE: LinkedIn heavily rate-limits scrapers and requires auth
        # for most features. We use the public guest search endpoint which yields
        # limited results (25 per request). Auth-required features are skipped.
        jobs = []

        for search in self.SEARCHES[:2]:
            html = await self._get(
                "https://www.linkedin.com/jobs/search/",
                params={
                    "keywords": search["keywords"],
                    "location": "India",
                    "f_E": search["f_E"],
                    "f_TPR": "r604800",  # Last 7 days
                    "start": "0",
                    "geoId": "102713980",  # India geo ID
                },
                headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.linkedin.com/jobs/",
                },
            )
            if not html:
                continue

            parsed = self._parse_linkedin(html, search["keywords"])
            jobs.extend(parsed)
            logger.info(f"LinkedIn [{search['keywords']}]: {len(parsed)} jobs")

        return jobs

    def _parse_linkedin(self, html: str, keyword: str) -> list[RawJob]:
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        # LinkedIn public guest job cards
        cards = soup.find_all(["div", "li"], class_=re.compile(
            r"job-search-card|base-card|jobs-search__results-list__item|result-card"
        ))

        for card in cards:
            try:
                title_el = card.find(["h3", "span", "a"], class_=re.compile(
                    r"job-title|base-search-card__title|result-card__title"
                ))
                title = title_el.get_text(strip=True) if title_el else ""

                comp_el = card.find(["h4", "a", "span"], class_=re.compile(
                    r"company|base-search-card__subtitle|result-card__subtitle"
                ))
                company = comp_el.get_text(strip=True) if comp_el else ""

                loc_el = card.find(["span", "div"], class_=re.compile(r"location|job-search-card__location"))
                location = loc_el.get_text(strip=True) if loc_el else "India"

                link_el = card.find("a", href=re.compile(r"linkedin\.com/jobs|/jobs/view"))
                job_url = link_el["href"] if link_el else "https://linkedin.com/jobs"
                # Strip tracking params
                job_url = job_url.split("?")[0]

                time_el = card.find(["time"])
                date_text = time_el.get("datetime", "") if time_el else ""
                try:
                    posted = datetime.fromisoformat(date_text[:10]).date() if date_text else date.today()
                except Exception:
                    posted = date.today()

                if title and len(title) > 3:
                    jobs.append(RawJob(
                        title=title,
                        company=company or "Unknown",
                        location=location,
                        job_url=job_url,
                        description=keyword,
                        experience_text=f"{keyword} 2-4 years",
                        date_posted=posted,
                        source=self.source_name,
                    ))
            except Exception as e:
                logger.debug(f"LinkedIn parse error: {e}")

        return jobs
