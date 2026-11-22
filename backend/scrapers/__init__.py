from backend.scrapers.base import BaseScraper, RawJob
from backend.scrapers.wellfound import WellfoundScraper
from backend.scrapers.ycombinator import YCScraper
from backend.scrapers.naukri import NaukriScraper
from backend.scrapers.indeed import IndeedScraper
from backend.scrapers.foundit import FounditScraper
from backend.scrapers.linkedin import LinkedInScraper
from backend.scrapers.cutshort import CutshortScraper
from backend.scrapers.instahyre import InstahyreScraper
from backend.scrapers.companies import CompanyCrawler


def get_all_scrapers() -> list[BaseScraper]:
    return [
        WellfoundScraper(),
        YCScraper(),
        NaukriScraper(),
        IndeedScraper(),
        FounditScraper(),
        LinkedInScraper(),
        CutshortScraper(),
        InstahyreScraper(),
        CompanyCrawler(),
    ]

__all__ = ["get_all_scrapers", "BaseScraper", "RawJob"]
