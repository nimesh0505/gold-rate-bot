import pytest
from unittest.mock import Mock, patch, MagicMock
from app.main import main


class TestMain:
    """Test cases for main function."""
    
    @patch('app.main.setup_logger')
    @patch('app.main.Config')
    @patch('app.main.GoldRateScraper')
    @patch('app.main.EmailService')
    def test_main_success_flow(self, mock_email_service, mock_scraper, mock_config, mock_setup_logger):
        """Test main function success flow with mocked email sending."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_setup_logger.return_value = mock_logger
        
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance
        
        mock_scraper_instance = Mock()
        mock_scraper.return_value = mock_scraper_instance
        mock_scraper_instance.fetch_gold_rates.return_value = {"22k": "14903", "24k": "16110"}
        
        mock_email_service_instance = Mock()
        mock_email_service.return_value = mock_email_service_instance
        
        # Run main function
        main()
        
        # Verify all components were initialized
        mock_setup_logger.assert_called_once()
        mock_config.assert_called_once()
        mock_scraper.assert_called_once()
        mock_email_service.assert_called_once_with(mock_config_instance)
        
        # Verify scraping was called
        mock_scraper_instance.fetch_gold_rates.assert_called_once()
        
        # Verify email was sent
        mock_email_service_instance.send_success_email.assert_called_once_with("14903", "16110")
        
        # Verify logging
        mock_logger.info.assert_any_call("Fetching gold rate")
        mock_logger.info.assert_any_call("Extracted 22K=\u20b914903 24K=\u20b916110")
        mock_logger.info.assert_any_call("Email sent successfully")
    
    @patch('app.main.setup_logger')
    @patch('app.main.Config')
    @patch('app.main.GoldRateScraper')
    @patch('app.main.EmailService')
    def test_main_no_gold_rates_found(self, mock_email_service, mock_scraper, mock_config, mock_setup_logger):
        """Test main function when no gold rates are found."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_setup_logger.return_value = mock_logger
        
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance
        
        mock_scraper_instance = Mock()
        mock_scraper.return_value = mock_scraper_instance
        mock_scraper_instance.fetch_gold_rates.return_value = None
        
        mock_email_service_instance = Mock()
        mock_email_service.return_value = mock_email_service_instance
        
        # Run main function
        main()
        
        # Verify error email was sent
        mock_email_service_instance.send_error_email.assert_called_once_with("No gold rates found on the page")
        
        # Verify error logging
        mock_logger.error.assert_called_once_with("No gold rates found")
    
    @patch('app.main.setup_logger')
    @patch('app.main.Config')
    @patch('app.main.GoldRateScraper')
    @patch('app.main.EmailService')
    def test_main_scraping_exception(self, mock_email_service, mock_scraper, mock_config, mock_setup_logger):
        """Test main function when scraping raises an exception."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_setup_logger.return_value = mock_logger
        
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance
        
        mock_scraper_instance = Mock()
        mock_scraper.return_value = mock_scraper_instance
        mock_scraper_instance.fetch_gold_rates.side_effect = Exception("Connection timeout")
        
        mock_email_service_instance = Mock()
        mock_email_service.return_value = mock_email_service_instance
        
        # Run main function
        main()
        
        # Verify error email was sent
        mock_email_service_instance.send_error_email.assert_called_once_with("Error: Connection timeout")
        
        # Verify error logging
        mock_logger.error.assert_any_call("Error in main process: Connection timeout")
    
    @patch('app.main.setup_logger')
    @patch('app.main.Config')
    @patch('app.main.GoldRateScraper')
    @patch('app.main.EmailService')
    def test_main_email_service_exception(self, mock_email_service, mock_scraper, mock_config, mock_setup_logger):
        """Test main function when email service raises an exception."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_setup_logger.return_value = mock_logger
        
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance
        
        mock_scraper_instance = Mock()
        mock_scraper.return_value = mock_scraper_instance
        mock_scraper_instance.fetch_gold_rates.return_value = {"22k": "14903", "24k": "16110"}
        
        mock_email_service_instance = Mock()
        mock_email_service.return_value = mock_email_service_instance
        mock_email_service_instance.send_success_email.side_effect = Exception("SMTP error")
        
        # Run main function
        main()
        
        # Verify error email was sent
        mock_email_service_instance.send_error_email.assert_called_once_with("Error: SMTP error")
        
        # Verify error logging
        mock_logger.error.assert_called_once_with("Error in main process: SMTP error")
    
    @patch('app.main.setup_logger')
    @patch('app.main.Config')
    @patch('app.main.GoldRateScraper')
    @patch('app.main.EmailService')
    def test_main_partial_gold_rates(self, mock_email_service, mock_scraper, mock_config, mock_setup_logger):
        """Test main function when only partial gold rates are found."""
        # Setup mocks
        mock_logger = MagicMock()
        mock_setup_logger.return_value = mock_logger
        
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance
        
        mock_scraper_instance = Mock()
        mock_scraper.return_value = mock_scraper_instance
        mock_scraper_instance.fetch_gold_rates.return_value = {"22k": "14903"}  # Missing 24k
        
        mock_email_service_instance = Mock()
        mock_email_service.return_value = mock_email_service_instance
        
        # Run main function
        main()
        
        # Verify email was sent with partial data
        mock_email_service_instance.send_success_email.assert_called_once_with("14903", None)
        
        # Verify logging
        mock_logger.info.assert_any_call("Extracted 22K=\u20b914903 24K=\u20b9None")
