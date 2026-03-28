import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)

class GoldRateScraper:
    """Scraper for fetching gold rates from chandukakasaraf.in."""
    
    BASE_URL = "https://chandukakasaraf.in/todays-gold-rate/"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def fetch_gold_rates(self) -> Optional[Dict[str, str]]:
        """Fetch gold rates with retry logic."""
        try:
            response = requests.get(self.BASE_URL, timeout=10)
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
