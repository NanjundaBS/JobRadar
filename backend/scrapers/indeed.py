import logging
import re
from datetime import date, timedelta
from bs4 import BeautifulSoup

from backend.scrapers.base import BaseScraper, RawJob

logger = logging.getLogger(__name__)


class IndeedScraper(BaseScraper):
    source_name = "indeed"

    SEARCHES = [
        "devops engineer",
        "aws devops",
        "cloud engineer",
        "site reliability engineer",
        "platform engineer",
    ]

    async def fetch_jobs(self, keywords: list[str]) -> list[RawJob]:
        # SCRAPER NOTE: Indeed blocks heavy scrapers and uses JS rendering.
        # We use in.indeed.com (India) with HTML parsing of static content.
        jobs = []

        for query in self.SEARCHES[:3]:
            html = await self._get(
                "https://in.indeed.com/jobs",
                params={"q": query, "l": "India", "fromage": "7"},
                headers={"Referer": "https://in.indeed.com/"},
            )
            if not html:
                continue

            parsed = self._parse_indeed(html, query)
            jobs.extend(parsed)
            logger.info(f"Indeed [{query}]: {len(parsed)} jobs")

        return jobs

    def _parse_indeed(self, html: str, query: str) -> list[RawJob]:
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        # Indeed job cards
        cards = soup.find_all(["div", "li"], class_=re.compile(
            r"job_seen_beacon|jobsearch-SerpJobCard|slider_item|tapItem|resultContent"
        ))

        for card in cards:
            try:
                title_el = card.find(["h2", "span", "a"], class_=re.compile(r"jobTitle|title"))
                title = title_el.get_text(strip=True) if title_el else ""
                # Remove "new" badge text
                title = re.sub(r'^new\s+', '', title, flags=re.IGNORECASE).strip()

                comp_el = card.find(["span", "a"], class_=re.compile(r"companyName|company"))
                company = comp_el.get_text(strip=True) if comp_el else ""

                loc_el = card.find(["div", "span"], class_=re.compile(r"companyLocation|location"))
                location = loc_el.get_text(strip=True) if loc_el else "India"

                # Job URL
                link_el = card.find("a", href=True)
                job_url = ""
                if link_el:
                    href = link_el["href"]
                    if href.startswith("/"):
                        job_url = f"https://in.indeed.com{href}"
                    elif href.startswith("http"):
                        job_url = href

                desc_el = card.find(["div", "ul"], class_=re.compile(r"summary|job-snippet|snippet"))
                description = desc_el.get_text(strip=True) if desc_el else ""

                date_el = card.find(["span", "div"], class_=re.compile(r"date|posted"))
                date_text = date_el.get_text(strip=True) if date_el else ""
                posted = self._parse_date(date_text)

                if title and len(title) > 3:
                    jobs.append(RawJob(
                        title=title,
                        company=company or "Unknown",
                        location=location,
                        job_url=job_url or f"https://in.indeed.com/jobs?q={query.replace(' ', '+')}",
                        description=description,
                        experience_text=f"{description} {title}",
                        date_posted=posted,
                        source=self.source_name,
                        career_url=f"https://in.indeed.com/jobs?q={query.replace(' ', '+')}",
                    ))
            except Exception as e:
                logger.debug(f"Indeed card parse error: {e}")

        return jobs

    def _parse_date(self, text: str) -> date:
        text = text.lower().strip()
        today = date.today()
        if "today" in text or "just posted" in text or "hours" in text:
            return today
        m = re.search(r"(\d+)\s*days?", text)
        if m:
            return today - timedelta(days=int(m.group(1)))
        return today
