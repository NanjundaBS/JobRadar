from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import datetime
import asyncio
import logging
import random

import httpx

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


@dataclass
class RawJob:
    title: str
    company: str
    location: str
    job_url: str
    description: str
    experience_text: str
    date_posted: Optional[datetime.date]
    source: str
    career_url: Optional[str] = None
    raw_data: dict = field(default_factory=dict)


class BaseScraper(ABC):
    source_name: str = "base"

    @abstractmethod
    async def fetch_jobs(self, keywords: list[str]) -> list[RawJob]:
        """Fetch jobs matching keywords. Must handle rate limits and errors gracefully."""
        pass

    async def _get(self, url: str, headers: dict = None, params: dict = None, timeout: int = 30) -> Optional[str]:
        """HTTP GET with 3 retries and exponential backoff."""
        h = {**HEADERS, **(headers or {})}
        for attempt in range(3):
            try:
                await asyncio.sleep(random.uniform(0.5, 1.5))
                async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
                    resp = await client.get(url, headers=h, params=params)
                    if resp.status_code == 429:
                        wait = 2 ** attempt * 5
                        logger.warning(f"{self.source_name}: Rate limited (429), waiting {wait}s")
                        await asyncio.sleep(wait)
                        continue
                    if resp.status_code in (403, 401):
                        logger.warning(f"{self.source_name}: {resp.status_code} for {url}")
                        return None
                    if resp.status_code == 200:
                        return resp.text
                    logger.warning(f"{self.source_name}: HTTP {resp.status_code} for {url}")
                    return None
            except httpx.TimeoutException:
                logger.warning(f"{self.source_name}: Timeout on attempt {attempt + 1}")
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
            except httpx.HTTPError as e:
                logger.warning(f"{self.source_name}: HTTP error on attempt {attempt + 1}: {e}")
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"{self.source_name}: Unexpected error: {e}")
                break
        return None

    async def _get_json(self, url: str, headers: dict = None, params: dict = None) -> Optional[dict]:
        """HTTP GET returning parsed JSON."""
        h = {**HEADERS, "Accept": "application/json", **(headers or {})}
        for attempt in range(3):
            try:
                await asyncio.sleep(random.uniform(0.3, 1.0))
                async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
                    resp = await client.get(url, headers=h, params=params)
                    if resp.status_code in (200, 201):
                        return resp.json()
                    if resp.status_code == 429:
                        await asyncio.sleep(2 ** attempt * 5)
                        continue
                    logger.warning(f"{self.source_name}: JSON fetch HTTP {resp.status_code} for {url}")
                    return None
            except Exception as e:
                logger.warning(f"{self.source_name}: JSON fetch error (attempt {attempt + 1}): {e}")
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
        return None
