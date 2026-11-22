import json
import logging
import re
from datetime import date
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from backend.scrapers.base import BaseScraper, RawJob

logger = logging.getLogger(__name__)

COMPANIES_FILE = Path(__file__).parent.parent / "data" / "companies.json"

DEVOPS_KEYWORDS = [
    "devops", "cloud", "platform", "infrastructure", "sre",
    "reliability", "aws", "kubernetes", "terraform", "jenkins",
    "docker", "k8s", "devsecops", "release engineer", "build engineer",
]


class CompanyCrawler(BaseScraper):
    source_name = "company_careers"

    async def fetch_jobs(self, keywords: list[str]) -> list[RawJob]:
        """Crawl career pages of companies listed in companies.json."""
        companies = self._load_companies()
        jobs = []

        for company in companies[:20]:  # Limit to avoid too many requests
            try:
                career_url = company.get("career_url", "")
                if not career_url:
                    continue

                html = await self._get(career_url, headers={"Referer": career_url})
                if not html:
                    continue

                parsed = self._parse_careers_page(html, company, career_url)
                if parsed:
                    jobs.extend(parsed)
                    logger.info(f"Company [{company['name']}]: {len(parsed)} jobs found")
            except Exception as e:
                logger.warning(f"Company crawl error [{company.get('name')}]: {e}")

        logger.info(f"CompanyCrawler: {len(jobs)} total jobs")
        return jobs

    def _load_companies(self) -> list[dict]:
        try:
            with open(COMPANIES_FILE) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Could not load companies.json: {e}")
            return []

    def _parse_careers_page(self, html: str, company: dict, career_url: str) -> list[RawJob]:
        soup = BeautifulSoup(html, "html.parser")
        job_links = []

        # Strategy 1: Find links with devops-related text
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True).lower()
            href = a["href"]

            if not (3 < len(text) < 200):
                continue

            if any(kw in text for kw in DEVOPS_KEYWORDS):
                # Normalize URL
                if not href.startswith("http"):
                    href = urljoin(career_url, href)
                if href not in [j[1] for j in job_links]:
                    job_links.append((a.get_text(strip=True), href))

        # Strategy 2: Common career page job listing patterns (Greenhouse, Lever, Workday)
        if not job_links:
            # Greenhouse
            gh_cards = soup.find_all(["div", "section"], class_=re.compile(r"opening|department|section"))
            for section in gh_cards:
                for a in section.find_all("a", href=True):
                    text = a.get_text(strip=True).lower()
                    if any(kw in text for kw in DEVOPS_KEYWORDS):
                        href = a["href"]
                        if not href.startswith("http"):
                            href = urljoin(career_url, href)
                        job_links.append((a.get_text(strip=True), href))

        jobs = []
        company_type = company.get("type", "Unknown")

        for title, url in job_links[:5]:  # Max 5 per company
            jobs.append(RawJob(
                title=title[:200],
                company=company["name"],
                location="India",
                job_url=url,
                description=f"DevOps/Cloud role at {company['name']}. See job link for full description.",
                experience_text="2-4 years",
                date_posted=date.today(),
                source=self.source_name,
                career_url=career_url,
                raw_data={"company_type": company_type},
            ))

        return jobs
