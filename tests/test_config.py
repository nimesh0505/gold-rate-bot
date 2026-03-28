import pytest
import os
from unittest.mock import patch
from app.config import Config


class TestConfig:
    """Test cases for Config class."""
    
    def test_config_initialization_success(self):
        """Test successful configuration initialization."""
        with patch.dict(os.environ, {
            'EMAIL_USER': 'test@gmail.com',
            'EMAIL_PASSWORD': 'app_password',
            'EMAIL_TO': 'recipient@gmail.com'
        }):
            config = Config()
            
            assert config.EMAIL_USER == 'test@gmail.com'
            assert config.EMAIL_PASSWORD == 'app_password'
            assert config.EMAIL_TO == 'recipient@gmail.com'
    
    def test_config_missing_email_user(self):
        """Test configuration when EMAIL_USER is missing."""
        with patch.dict(os.environ, {
            'EMAIL_PASSWORD': 'app_password',
            'EMAIL_TO': 'recipient@gmail.com'
        }, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables: EMAIL_USER"):
                Config()
    
    def test_config_missing_email_password(self):
        """Test configuration when EMAIL_PASSWORD is missing."""
        with patch.dict(os.environ, {
            'EMAIL_USER': 'test@gmail.com',
            'EMAIL_TO': 'recipient@gmail.com'
        }, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables: EMAIL_PASSWORD"):
                Config()
    
    def test_config_missing_email_to(self):
        """Test configuration when EMAIL_TO is missing."""
        with patch.dict(os.environ, {
            'EMAIL_USER': 'test@gmail.com',
            'EMAIL_PASSWORD': 'app_password'
        }, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables: EMAIL_TO"):
                Config()
    
    def test_config_multiple_missing_variables(self):
        """Test configuration when multiple variables are missing."""
        with patch.dict(os.environ, {
            'EMAIL_USER': 'test@gmail.com'
        }, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables: EMAIL_PASSWORD, EMAIL_TO"):
                Config()
    
    def test_config_empty_string_values(self):
        """Test configuration when environment variables are empty strings."""
        with patch.dict(os.environ, {
            'EMAIL_USER': '',
            'EMAIL_PASSWORD': 'app_password',
            'EMAIL_TO': 'recipient@gmail.com'
        }, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables: EMAIL_USER"):
                Config()
