import logging
from datetime import date
from bs4 import BeautifulSoup

from backend.scrapers.base import BaseScraper, RawJob

logger = logging.getLogger(__name__)


class YCScraper(BaseScraper):
    source_name = "ycombinator"

    async def fetch_jobs(self, keywords: list[str]) -> list[RawJob]:
        # SCRAPER NOTE: Work at a Startup is a React SPA.
        # We use their public search + HN Algolia API as fallback.
        jobs = []

        # Try WaaS public search
        html = await self._get(
            "https://www.workatastartup.com/jobs",
            params={"role": "eng", "subRole": "devops,platform,infrastructure,sre"},
        )
        if html:
            jobs.extend(self._parse_waas(html))

        # HN Algolia Jobs API
        hn_jobs = await self._fetch_hn_jobs()
        jobs.extend(hn_jobs)

        logger.info(f"YC: {len(jobs)} jobs")
        return jobs

    def _parse_waas(self, html: str) -> list[RawJob]:
        import re
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        cards = soup.find_all(["div", "li"], class_=re.compile(r"job|listing|JobListing|company-job"))
        for card in cards:
            try:
                title_el = card.find(["h2", "h3", "a"], class_=re.compile(r"title|role|job-title"))
                title = title_el.get_text(strip=True) if title_el else ""

                comp_el = card.find(["span", "div", "a"], class_=re.compile(r"company|startup|name"))
                company = comp_el.get_text(strip=True) if comp_el else "YC Startup"

                link_el = card.find("a", href=True)
                job_url = link_el["href"] if link_el else "https://www.workatastartup.com/jobs"
                if job_url and not job_url.startswith("http"):
                    job_url = f"https://www.workatastartup.com{job_url}"

                desc_el = card.find(["p", "div"], class_=re.compile(r"desc|snippet|summary|skill"))
                description = desc_el.get_text(strip=True) if desc_el else ""

                if title and len(title) > 3:
                    jobs.append(RawJob(
                        title=title[:200],
                        company=company,
                        location="Remote / Global",
                        job_url=job_url,
                        description=description,
                        experience_text=description,
                        date_posted=date.today(),
                        source=self.source_name,
                        career_url="https://www.workatastartup.com/jobs",
                    ))
            except Exception as e:
                logger.debug(f"WaaS parse error: {e}")

        return jobs

    async def _fetch_hn_jobs(self) -> list[RawJob]:
        """Fetch DevOps-related jobs from HN via Algolia API."""
        jobs = []
        try:
            data = await self._get_json(
                "https://hn.algolia.com/api/v1/search",
                params={
                    "query": "devops OR cloud engineer OR platform engineer OR SRE OR infrastructure engineer",
                    "tags": "job",
                    "hitsPerPage": 20,
                },
            )
            if data and "hits" in data:
                for hit in data["hits"]:
                    title = hit.get("title") or "DevOps / Cloud Role"
                    obj_id = hit.get("objectID", "")
                    url = hit.get("url") or f"https://news.ycombinator.com/item?id={obj_id}"
                    text = (hit.get("story_text") or hit.get("comment_text") or "")[:500]

                    jobs.append(RawJob(
                        title=title[:200],
                        company="HN Company",
                        location="Remote",
                        job_url=url,
                        description=text,
                        experience_text=text[:200],
                        date_posted=date.today(),
                        source="hackernews",
                    ))
        except Exception as e:
            logger.warning(f"HN jobs fetch error: {e}")
        return jobs
