import json
import logging
import re
from datetime import date, datetime
from typing import Optional
from bs4 import BeautifulSoup

from backend.scrapers.base import BaseScraper, RawJob

logger = logging.getLogger(__name__)

NAUKRI_SEARCHES = [
    "devops-engineer-jobs",
    "aws-devops-engineer-jobs",
    "cloud-engineer-jobs",
    "platform-engineer-jobs",
    "site-reliability-engineer-jobs",
]


class NaukriScraper(BaseScraper):
    source_name = "naukri"

    async def fetch_jobs(self, keywords: list[str]) -> list[RawJob]:
        # SCRAPER NOTE: Naukri.com is heavily JS-rendered.
        # We attempt JSON-LD + their internal search API.
        # Full access requires Naukri's official API (registration).
        jobs = []

        # Try their internal search API
        api_jobs = await self._try_naukri_api()
        jobs.extend(api_jobs)

        # Fallback: HTML scraping
        if not api_jobs:
            for search_path in NAUKRI_SEARCHES[:2]:
                url = f"https://www.naukri.com/{search_path}"
                html = await self._get(url, headers={
                    "Referer": "https://www.naukri.com/",
                    "X-Requested-With": "XMLHttpRequest",
                })
                if not html:
                    continue
                parsed = self._parse_naukri_html(html, url)
                jobs.extend(parsed)

        logger.info(f"Naukri: {len(jobs)} jobs")
        return jobs

    def _parse_naukri_html(self, html: str, source_url: str) -> list[RawJob]:
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        # Try JSON-LD structured data
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get("@type") == "JobPosting":
                        job = self._parse_jsonld_job(item, source_url)
                        if job:
                            jobs.append(job)
            except Exception:
                pass

        # Fallback HTML card parsing
        if not jobs:
            cards = soup.find_all(["article", "div"], class_=re.compile(
                r"jobTuple|job-tuple|srp-jobtuple|cust-job-tuple"
            ))
            for card in cards:
                try:
                    title_el = card.find(["a", "h2"], class_=re.compile(r"title|jobTitle|job-title"))
                    title = title_el.get_text(strip=True) if title_el else ""

                    comp_el = card.find(["a", "span"], class_=re.compile(r"comp-name|companyInfo|comp"))
                    company = comp_el.get_text(strip=True) if comp_el else ""

                    link = (title_el.get("href", source_url) if title_el else source_url)
                    if link and not link.startswith("http"):
                        link = f"https://www.naukri.com{link}"

                    exp_el = card.find(["span", "li"], class_=re.compile(r"exp|experience|ellipsis"))
                    exp = exp_el.get_text(strip=True) if exp_el else ""

                    loc_el = card.find(["span", "li"], class_=re.compile(r"loc|location|ellipsis"))
                    location = loc_el.get_text(strip=True) if loc_el else "India"

                    desc_el = card.find(["span", "div"], class_=re.compile(r"job-desc|desc|snippet"))
                    desc = desc_el.get_text(strip=True) if desc_el else ""

                    if title:
                        jobs.append(RawJob(
                            title=title,
                            company=company or "Unknown",
                            location=location,
                            job_url=link,
                            description=desc,
                            experience_text=exp,
                            date_posted=date.today(),
                            source=self.source_name,
                        ))
                except Exception as e:
                    logger.debug(f"Naukri card parse error: {e}")

        return jobs

    def _parse_jsonld_job(self, data: dict, source_url: str) -> Optional[RawJob]:
        try:
            title = data.get("title", "")
            company = ""
            if "hiringOrganization" in data:
                company = data["hiringOrganization"].get("name", "")

            location = ""
            if "jobLocation" in data:
                loc = data["jobLocation"]
                if isinstance(loc, dict):
                    addr = loc.get("address", {})
                    location = f"{addr.get('addressLocality', '')}, {addr.get('addressCountry', '')}".strip(", ")

            job_url = data.get("url", source_url)
            description = str(data.get("description", ""))[:500]

            exp_reqs = data.get("experienceRequirements", "")
            if isinstance(exp_reqs, dict):
                months = exp_reqs.get("monthsOfExperience", 0)
                exp_text = f"{months // 12} years" if months else ""
            else:
                exp_text = str(exp_reqs)

            date_str = data.get("datePosted", "")
            try:
                posted = datetime.fromisoformat(date_str[:10]).date() if date_str else date.today()
            except Exception:
                posted = date.today()

            if title:
                return RawJob(
                    title=title,
                    company=company or "Unknown",
                    location=location or "India",
                    job_url=job_url,
                    description=description,
                    experience_text=exp_text,
                    date_posted=posted,
                    source=self.source_name,
                )
        except Exception as e:
            logger.debug(f"JSON-LD parse error: {e}")
        return None

    async def _try_naukri_api(self) -> list[RawJob]:
        """Try Naukri's internal search API (undocumented)."""
        try:
            data = await self._get_json(
                "https://www.naukri.com/jobapi/v3/search",
                headers={
                    "appid": "109",
                    "systemid": "Naukri",
                    "Referer": "https://www.naukri.com/",
                },
                params={
                    "noOfResults": 20,
                    "urlType": "search_by_keyword",
                    "searchType": "adv",
                    "keyword": "devops engineer",
                    "location": "india",
                    "jobAge": 7,
                    "experience": "2",
                },
            )
            if not data or "jobDetails" not in data:
                return []

            jobs = []
            for item in data.get("jobDetails", []):
                try:
                    placeholders = item.get("placeholders", [])
                    location = placeholders[0].get("label", "India") if placeholders else "India"
                    jobs.append(RawJob(
                        title=item.get("title", ""),
                        company=item.get("companyName", "Unknown"),
                        location=location,
                        job_url=item.get("jdURL", "https://www.naukri.com"),
                        description=item.get("jobDescription", "")[:500],
                        experience_text=item.get("experienceText", ""),
                        date_posted=date.today(),
                        source=self.source_name,
                        raw_data={"naukri_id": item.get("jobId")},
                    ))
                except Exception:
                    pass
            return jobs
        except Exception as e:
            logger.warning(f"Naukri API error: {e}")
            return []
