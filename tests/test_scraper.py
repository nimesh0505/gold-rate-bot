import pytest
import requests
from unittest.mock import patch, Mock
from app.scraper import GoldRateScraper, _is_retryable
from bs4 import BeautifulSoup


def _html(rate_22k: str, rate_24k: str) -> str:
    """Build mock HTML matching the real chandukakasaraf.in format (no pipe separator)."""
    return (
        f"<html><body>"
        f"<p>22 KT Gold\u20b9{rate_22k} PER 1 GM</p>"
        f"<p>24 KT Gold\u20b9{rate_24k} PER 1 GM</p>"
        f"</body></html>"
    )


class TestGoldRateScraper:
    """Test cases for GoldRateScraper class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scraper = GoldRateScraper()

    def _mock_response(self, html: str, status_code: int = 200):
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.text = html
        mock_response.raise_for_status.return_value = None
        return mock_response

    @patch('app.scraper.requests.get')
    def test_fetch_gold_rates_success(self, mock_get):
        """Test successful gold rate extraction."""
        mock_get.return_value = self._mock_response(_html('14903', '16110'))

        result = self.scraper.fetch_gold_rates()

        assert result is not None
        assert result["22k"] == "14903"
        assert result["24k"] == "16110"
        mock_get.assert_called_once_with(
            self.scraper.BASE_URL, headers=self.scraper.HEADERS, timeout=10
        )

    @patch('app.scraper.requests.get')
    def test_fetch_gold_rates_with_whitespace_variations(self, mock_get):
        """Test extraction with extra spaces around KT and no separator."""
        html = (
            "<html><body>"
            "<p>22   KT  Gold  \u20b9  15200 PER 1 GM</p>"
            "<p>24  KT  Gold  \u20b9  16500 PER 1 GM</p>"
            "</body></html>"
        )
        mock_get.return_value = self._mock_response(html)

        result = self.scraper.fetch_gold_rates()

        assert result is not None
        assert result["22k"] == "15200"
        assert result["24k"] == "16500"

    @patch('app.scraper.requests.get')
    def test_fetch_gold_rates_partial_data(self, mock_get):
        """Test when only one gold rate is found."""
        html = (
            "<html><body>"
            "<p>22 KT Gold\u20b914903 PER 1 GM</p>"
            "<p>Some other text</p>"
            "</body></html>"
        )
        mock_get.return_value = self._mock_response(html)

        result = self.scraper.fetch_gold_rates()

        assert result is None

    @patch('app.scraper.requests.get')
    def test_fetch_gold_rates_no_data(self, mock_get):
        """Test when no gold rate data is found."""
        mock_get.return_value = self._mock_response(
            "<html><body><p>No gold rates here</p></body></html>"
        )

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
        mock_fail = Mock()
        mock_fail.status_code = 500
        mock_fail.raise_for_status.side_effect = requests.RequestException("Server error")

        mock_get.side_effect = [mock_fail, mock_fail,
                                self._mock_response(_html('14903', '16110'))]

        result = self.scraper.fetch_gold_rates()

        assert result is not None
        assert result["22k"] == "14903"
        assert result["24k"] == "16110"
        assert mock_get.call_count == 3

    def test_extract_rate_valid_pattern(self):
        """Test _extract_rate with real page format (no pipe)."""
        text = "22 KT Gold\u20b914903 PER 1 GM"
        pattern = r"22\s*KT\s*Gold\s*\u20b9\s*(\d+)"

        result = self.scraper._extract_rate(text, pattern)

        assert result == "14903"

    def test_extract_rate_no_match(self):
        """Test _extract_rate with no matching pattern."""
        text = "No gold rate here"
        pattern = r"22\s*KT\s*Gold\s*\u20b9\s*(\d+)"

        result = self.scraper._extract_rate(text, pattern)

        assert result is None

    def test_extract_rate_case_insensitive(self):
        """Test _extract_rate with case insensitive matching."""
        text = "22 kt gold\u20b914903 PER 1 GM"
        pattern = r"22\s*KT\s*Gold\s*\u20b9\s*(\d+)"

        result = self.scraper._extract_rate(text, pattern)

        assert result == "14903"

    @patch('app.scraper.requests.get')
    def test_fetch_gold_rates_403_forbidden(self, mock_get):
        """Test that 403 response raises HTTPError immediately without retrying."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        with pytest.raises(requests.HTTPError, match="403 Forbidden"):
            self.scraper.fetch_gold_rates()

        assert mock_get.call_count == 1

    def test_is_retryable_returns_false_for_403(self):
        """Test _is_retryable returns False for 403 HTTPError."""
        mock_response = Mock()
        mock_response.status_code = 403
        exc = requests.HTTPError("403 Forbidden", response=mock_response)
        assert _is_retryable(exc) is False

    def test_is_retryable_returns_true_for_other_http_errors(self):
        """Test _is_retryable returns True for non-403 HTTP errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        exc = requests.HTTPError("500 Server Error", response=mock_response)
        assert _is_retryable(exc) is True

    def test_is_retryable_returns_true_for_non_http_errors(self):
        """Test _is_retryable returns True for non-HTTPError exceptions."""
        assert _is_retryable(requests.ConnectionError("timeout")) is True
        assert _is_retryable(ValueError("bad value")) is True

    def test_is_retryable_returns_true_for_http_error_without_response(self):
        """Test _is_retryable returns True when HTTPError has no response."""
        exc = requests.HTTPError("error")
        assert _is_retryable(exc) is True

    @patch('app.scraper.requests.get')
    def test_fetch_gold_rates_parsing_exception(self, mock_get):
        """Test handling of unexpected parsing errors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.text = "<html></html>"
        mock_get.return_value = mock_response

        with patch('app.scraper.BeautifulSoup', side_effect=Exception("Parse error")):
            with pytest.raises(Exception, match="Parse error"):
                self.scraper.fetch_gold_rates()

    @patch('app.scraper.requests.get')
    def test_real_website_scraping(self, mock_get):
        """Test scraping with realistic HTML matching the actual site structure."""
        html = (
            "<!DOCTYPE html><html><head><title>Today's Gold Rate</title></head>"
            "<body>"
            "<p>Updated On: 2026-03-28 09:36:26"
            "18 KT Gold\u20b911165 PER 1 GM"
            "22 KT Gold\u20b913506 PER 1 GM"
            "24 KT Gold\u20b914600 PER 1 GM"
            "Platinum-950\u20b97420 PER 1 GM</p>"
            "</body></html>"
        )
        mock_get.return_value = self._mock_response(html)

        result = self.scraper.fetch_gold_rates()

        assert result is not None
        assert result["22k"] == "13506"
        assert result["24k"] == "14600"
