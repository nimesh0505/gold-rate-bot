import pytest
import os
from unittest.mock import patch
from app.config import Config


class TestConfig:
    """Test cases for Config class."""
    
    def test_config_initialization_success(self):
        """Test successful configuration initialization."""
        with patch.dict(os.environ, {
            'MAILERSEND_API_TOKEN': 'test_api_token',
            'EMAIL_FROM': 'info@domain.com',
            'EMAIL_TO': 'recipient@gmail.com'
        }):
            config = Config()
            
            assert config.MAILERSEND_API_TOKEN == 'test_api_token'
            assert config.EMAIL_FROM == 'info@domain.com'
            assert config.EMAIL_TO == 'recipient@gmail.com'
            assert config.EMAIL_FROM_NAME is not None
            assert config.EMAIL_TO_NAME is not None
    
    def test_config_missing_mailersend_token(self):
        """Test configuration when MAILERSEND_API_TOKEN is missing."""
        with patch.dict(os.environ, {
            'EMAIL_FROM': 'info@domain.com',
            'EMAIL_TO': 'recipient@gmail.com'
        }, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables: MAILERSEND_API_TOKEN"):
                Config()
    
    def test_config_missing_email_from(self):
        """Test configuration when EMAIL_FROM is missing."""
        with patch.dict(os.environ, {
            'MAILERSEND_API_TOKEN': 'test_api_token',
            'EMAIL_TO': 'recipient@gmail.com'
        }, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables: EMAIL_FROM"):
                Config()
    
    def test_config_missing_email_to(self):
        """Test configuration when EMAIL_TO is missing."""
        with patch.dict(os.environ, {
            'MAILERSEND_API_TOKEN': 'test_api_token',
            'EMAIL_FROM': 'info@domain.com'
        }, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables: EMAIL_TO"):
                Config()
    
    def test_config_multiple_missing_variables(self):
        """Test configuration when multiple variables are missing."""
        with patch.dict(os.environ, {
            'MAILERSEND_API_TOKEN': 'test_api_token'
        }, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables: EMAIL_FROM, EMAIL_TO"):
                Config()
    
    def test_config_empty_string_values(self):
        """Test configuration when environment variables are empty strings."""
        with patch.dict(os.environ, {
            'MAILERSEND_API_TOKEN': '',
            'EMAIL_FROM': 'info@domain.com',
            'EMAIL_TO': 'recipient@gmail.com'
        }, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables: MAILERSEND_API_TOKEN"):
                Config()
