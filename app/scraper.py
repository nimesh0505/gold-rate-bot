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

            logger.info(f"Response: status={response.status_code}, encoding={response.encoding}, "
                       f"content-type={response.headers.get('content-type', 'unknown')}")
            
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all text containing gold rate information
            text_content = soup.get_text()
            
            # Log snippet around where we expect to find rates for debugging
            self._log_rate_context(text_content)

            # Real page format: "22 KT Gold₹13506 PER 1 GM" (no pipe separator)
            pattern_22k = r"22\s*KT\s*Gold\s*₹\s*(\d+)"
            pattern_24k = r"24\s*KT\s*Gold\s*₹\s*(\d+)"
            
            rate_22k = self._extract_rate(text_content, pattern_22k)
            rate_24k = self._extract_rate(text_content, pattern_24k)
            
            logger.info(f"Extraction results: 22K={rate_22k}, 24K={rate_24k}")
            
            if rate_22k and rate_24k:
                return {"22k": rate_22k, "24k": rate_24k}
            else:
                logger.error(f"Regex patterns used: 22K='{pattern_22k}', 24K='{pattern_24k}'")
                logger.error("Could not extract both gold rates — check log context above")
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

    def _log_rate_context(self, text: str) -> None:
        """Log text snippet around gold rate mentions for debugging."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        
        # Find lines mentioning gold or KT
        relevant_lines = [
            line for line in lines
            if any(keyword in line.upper() for keyword in ['GOLD', 'KT', '₹', 'RATE'])
        ]
        
        if relevant_lines:
            logger.info(f"Found {len(relevant_lines)} lines with gold/rate keywords")
            # Log first 5 relevant lines to avoid flooding
            for i, line in enumerate(relevant_lines[:5]):
                # Truncate long lines
                display_line = line if len(line) <= 200 else line[:200] + "..."
                logger.info(f"  Line {i+1}: {repr(display_line)}")
        else:
            logger.warning("No lines found containing gold rate keywords")
            logger.warning(f"First 500 chars of page text: {repr(text[:500])}")
