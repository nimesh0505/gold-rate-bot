import pytest
from unittest.mock import Mock, patch, MagicMock
import smtplib
from app.email_service import EmailService
from app.config import Config


class TestEmailService:
    """Test cases for EmailService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a mock config
        self.mock_config = Mock(spec=Config)
        self.mock_config.EMAIL_USER = 'test@gmail.com'
        self.mock_config.EMAIL_PASSWORD = 'app_password'
        self.mock_config.EMAIL_TO = 'recipient@gmail.com'
        
        self.email_service = EmailService(self.mock_config)
    
    @patch('app.email_service.smtplib.SMTP')
    def test_send_success_email(self, mock_smtp):
        """Test sending success email."""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Test method
        self.email_service.send_success_email('14903', '16110')
        
        # Verify SMTP calls
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@gmail.com', 'app_password')
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
        
        # Verify email content
        call_args = mock_server.send_message.call_args[0][0]
        assert call_args['From'] == 'test@gmail.com'
        assert call_args['To'] == 'recipient@gmail.com'
        assert call_args['Subject'] == 'Daily Gold Rate'
        assert '22K Gold: \u20b914903' in call_args.get_payload()
        assert '24K Gold: \u20b916110' in call_args.get_payload()
    
    @patch('app.email_service.smtplib.SMTP')
    def test_send_error_email(self, mock_smtp):
        """Test sending error email."""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Test method
        self.email_service.send_error_email('Connection timeout')
        
        # Verify SMTP calls
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@gmail.com', 'app_password')
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
        
        # Verify email content
        call_args = mock_server.send_message.call_args[0][0]
        assert call_args['From'] == 'test@gmail.com'
        assert call_args['To'] == 'recipient@gmail.com'
        assert call_args['Subject'] == 'Gold Rate Bot Alert'
        assert 'Connection timeout' in call_args.get_payload()
    
    @patch('app.email_service.smtplib.SMTP')
    def test_smtp_exception_handling(self, mock_smtp):
        """Test handling of SMTP exceptions."""
        # Mock SMTP to raise exception
        mock_smtp.side_effect = smtplib.SMTPException("SMTP connection failed")
        
        # Test that exception is raised
        with pytest.raises(smtplib.SMTPException, match="SMTP connection failed"):
            self.email_service.send_success_email('14903', '16110')
    
    @patch('app.email_service.smtplib.SMTP')
    def test_login_failure(self, mock_smtp):
        """Test handling of login failure."""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Mock login to raise exception
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")
        
        # Test that exception is raised
        with pytest.raises(smtplib.SMTPAuthenticationError):
            self.email_service.send_success_email('14903', '16110')
        
        # Verify cleanup
        mock_server.quit.assert_called_once()
    
    @patch('app.email_service.smtplib.SMTP')
    def test_send_message_failure(self, mock_smtp):
        """Test handling of send_message failure."""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Mock send_message to raise exception
        mock_server.send_message.side_effect = smtplib.SMTPException("Send failed")
        
        # Test that exception is raised
        with pytest.raises(smtplib.SMTPException, match="Send failed"):
            self.email_service.send_success_email('14903', '16110')
        
        # Verify cleanup
        mock_server.quit.assert_called_once()
    
    def test_email_service_initialization(self):
        """Test EmailService initialization."""
        assert self.email_service.config == self.mock_config
        assert self.email_service.smtp_server == 'smtp.gmail.com'
        assert self.email_service.smtp_port == 587
