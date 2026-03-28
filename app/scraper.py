import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
import logging

logger = logging.getLogger(__name__)


def _is_retryable(exc: Exception) -> bool:
    """Return False for 403 errors — no point retrying a blocked request."""
    if isinstance(exc, requests.HTTPError):
        resp = getattr(exc, "response", None)
        if resp is not None and resp.status_code == 403:
            return False
    return True


class GoldRateScraper:
    """Scraper for fetching gold rates from chandukakasaraf.in."""

    BASE_URL = "https://chandukakasaraf.in/todays-gold-rate/"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
        retry=retry_if_exception(_is_retryable),
    )
    def fetch_gold_rates(self) -> Optional[Dict[str, str]]:
        """Fetch gold rates with retry logic."""
        try:
            response = requests.get(self.BASE_URL, headers=self.HEADERS, timeout=10)
            if response.status_code == 403:
                logger.error("Access denied (403) — website may be blocking automated requests")
                raise requests.HTTPError("403 Forbidden", response=response)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all text containing gold rate information
            text_content = soup.get_text()
            
            # Extract 22 KT and 24 KT gold prices using regex
            rate_22k = self._extract_rate(text_content, r"22\s*KT\s*Gold\s*\|\s*₹\s*(\d+)")
            rate_24k = self._extract_rate(text_content, r"24\s*KT\s*Gold\s*\|\s*₹\s*(\d+)")
            
            if rate_22k and rate_24k:
                return {"22k": rate_22k, "24k": rate_24k}
            else:
                logger.warning("Could not extract both gold rates")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Parsing failed: {str(e)}")
            raise
    
    def _extract_rate(self, text: str, pattern: str) -> Optional[str]:
        """Extract rate using regex pattern."""
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else None
