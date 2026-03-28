import pytest
import requests
from unittest.mock import patch, Mock
from app.scraper import GoldRateScraper
from bs4 import BeautifulSoup


class TestGoldRateScraper:
    """Test cases for GoldRateScraper class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scraper = GoldRateScraper()
    
    @patch('app.scraper.requests.get')
    def test_fetch_gold_rates_success(self, mock_get):
        """Test successful gold rate extraction."""
        # Mock HTML response
        mock_response = Mock()
        mock_response.content = """
        <html>
            <body>
                <p>22 KT Gold | \u20b914903 PER 1 GM</p>
                <p>24 KT Gold | \u20b916110 PER 1 GM</p>
            </body>
        </html>
        """.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch_gold_rates()
        
        assert result is not None
        assert result["22k"] == "14903"
        assert result["24k"] == "16110"
        mock_get.assert_called_once_with(self.scraper.BASE_URL, timeout=10)
    
    @patch('app.scraper.requests.get')
    def test_fetch_gold_rates_with_whitespace_variations(self, mock_get):
        """Test gold rate extraction with different whitespace patterns."""
        mock_response = Mock()
        mock_response.content = """
        <html>
            <body>
                <p>22   KT  Gold | \u20b9  15200  PER 1 GM</p>
                <p>24 KT Gold|\u20b916500 PER 1 GM</p>
            </body>
        </html>
        """.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch_gold_rates()
        
        assert result is not None
        assert result["22k"] == "15200"
        assert result["24k"] == "16500"
    
    @patch('app.scraper.requests.get')
    def test_fetch_gold_rates_partial_data(self, mock_get):
        """Test when only one gold rate is found."""
        mock_response = Mock()
        mock_response.content = """
        <html>
            <body>
                <p>22 KT Gold | \u20b914903 PER 1 GM</p>
                <p>Some other text</p>
            </body>
        </html>
        """.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch_gold_rates()
        
        assert result is None  # Returns None when both rates are not found
    
    @patch('app.scraper.requests.get')
    def test_fetch_gold_rates_no_data(self, mock_get):
        """Test when no gold rate data is found."""
        mock_response = Mock()
        mock_response.content = b"""
        <html>
            <body>
                <p>No gold rates here</p>
            </body>
        </html>
        """
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch_gold_rates()
        
        assert result is None
    
    @patch('app.scraper.requests.get')
    def test_fetch_gold_rates_request_exception(self, mock_get):
        """Test handling of request exceptions."""
        mock_get.side_effect = requests.RequestException("Connection error")
        
        with pytest.raises(requests.RequestException):
            self.scraper.fetch_gold_rates()
    
    @patch('app.scraper.requests.get')
    def test_fetch_gold_rates_timeout(self, mock_get):
        """Test handling of timeout."""
        mock_get.side_effect = requests.Timeout("Request timeout")
        
        with pytest.raises(requests.Timeout):
            self.scraper.fetch_gold_rates()
    
    @patch('app.scraper.requests.get')
    def test_fetch_gold_rates_retry_logic(self, mock_get):
        """Test that retry logic works on failures."""
        # First two attempts fail, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.raise_for_status.side_effect = requests.RequestException("Server error")
        
        mock_response_success = Mock()
        mock_response_success.content = b"""
        <html>
            <body>
                <p>22 KT Gold | ₹14903 PER 1 GM</p>
                <p>24 KT Gold | ₹16110 PER 1 GM</p>
            </body>
        </html>
        """
        mock_response_success.raise_for_status.return_value = None
        
        mock_get.side_effect = [mock_response_fail, mock_response_fail, mock_response_success]
        
        result = self.scraper.fetch_gold_rates()
        
        assert result is not None
        assert result["22k"] == "14903"
        assert result["24k"] == "16110"
        assert mock_get.call_count == 3
    
    def test_extract_rate_valid_pattern(self):
        """Test _extract_rate with valid pattern."""
        text = "22 KT Gold | \u20b914903 PER 1 GM"
        pattern = r"22\s*KT\s*Gold\s*\|\s*\\u20b9(\d+)"
        
        result = self.scraper._extract_rate(text, pattern)
        
        assert result == "14903"
    
    def test_extract_rate_no_match(self):
        """Test _extract_rate with no matching pattern."""
        text = "No gold rate here"
        pattern = r"22\s*KT\s*Gold\s*\|\s*\\u20b9(\d+)"
        
        result = self.scraper._extract_rate(text, pattern)
        
        assert result is None
    
    def test_extract_rate_case_insensitive(self):
        """Test _extract_rate with case insensitive matching."""
        text = "22 kt gold | \u20b914903 PER 1 GM"
        pattern = r"22\s*KT\s*Gold\s*\|\s*\\u20b9(\d+)"
        
        result = self.scraper._extract_rate(text, pattern)
        
        assert result == "14903"
    
    @patch('app.scraper.requests.get')
    def test_real_website_scraping(self, mock_get):
        """Test actual website scraping (mocked but realistic response)."""
        # Create a realistic HTML response similar to the actual website
        mock_response = Mock()
        mock_response.content = """
        <!DOCTYPE html>
        <html>
        <head><title>Today's Gold Rate</title></head>
        <body>
            <div class="container">
                <h1>Today's Gold Rates</h1>
                <div class="rate-card">
                    <p>22 KT Gold | \u20b914850 PER 1 GM</p>
                    <p>24 KT Gold | \u20b916050 PER 1 GM</p>
                </div>
                <p>Last updated: Today at 9:00 AM</p>
            </div>
        </body>
        </html>
        """.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch_gold_rates()
        
        assert result is not None
        assert result["22k"] == "14850"
        assert result["24k"] == "16050"
