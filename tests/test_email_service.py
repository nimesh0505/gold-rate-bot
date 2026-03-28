import pytest
from unittest.mock import Mock, patch, MagicMock
from app.email_service import EmailService
from app.config import Config


class TestEmailService:
    """Test cases for EmailService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a mock config
        self.mock_config = Mock(spec=Config)
        self.mock_config.MAILERSEND_API_TOKEN = 'test_api_token'
        self.mock_config.EMAIL_FROM = 'info@domain.com'
        self.mock_config.EMAIL_FROM_NAME = 'Gold Rate Bot'
        self.mock_config.EMAIL_TO = 'recipient@gmail.com'
        self.mock_config.EMAIL_TO_NAME = 'Recipient'
        
        self.email_service = EmailService(self.mock_config)
    
    @patch('app.email_service.EmailBuilder')
    @patch('app.email_service.MailerSendClient')
    def test_send_success_email(self, mock_client_cls, mock_email_builder_cls):
        """Test sending success email."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        self.email_service = EmailService(self.mock_config)

        mock_builder = MagicMock()
        mock_email_builder_cls.return_value = mock_builder
        mock_builder.from_email.return_value = mock_builder
        mock_builder.to_many.return_value = mock_builder
        mock_builder.subject.return_value = mock_builder
        mock_builder.html.return_value = mock_builder
        mock_builder.text.return_value = mock_builder
        mock_builder.build.return_value = {"mock": "email"}
        
        # Test method
        self.email_service.send_success_email('14903', '16110')
        
        # Verify MailerSend calls
        mock_client_cls.assert_called_once_with(api_key='test_api_token')
        mock_email_builder_cls.assert_called_once()
        mock_builder.from_email.assert_called_once_with('info@domain.com', 'Gold Rate Bot')
        mock_builder.to_many.assert_called_once_with([{"email": "recipient@gmail.com", "name": "Recipient"}])
        mock_builder.subject.assert_called_once_with('Daily Gold Rate')
        mock_builder.build.assert_called_once()
        mock_client.emails.send.assert_called_once_with({"mock": "email"})
    
    @patch('app.email_service.EmailBuilder')
    @patch('app.email_service.MailerSendClient')
    def test_send_error_email(self, mock_client_cls, mock_email_builder_cls):
        """Test sending error email."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        self.email_service = EmailService(self.mock_config)

        mock_builder = MagicMock()
        mock_email_builder_cls.return_value = mock_builder
        mock_builder.from_email.return_value = mock_builder
        mock_builder.to_many.return_value = mock_builder
        mock_builder.subject.return_value = mock_builder
        mock_builder.html.return_value = mock_builder
        mock_builder.text.return_value = mock_builder
        mock_builder.build.return_value = {"mock": "error_email"}
        
        # Test method
        self.email_service.send_error_email('Connection timeout')
        
        # Verify MailerSend calls
        mock_client_cls.assert_called_once_with(api_key='test_api_token')
        mock_email_builder_cls.assert_called_once()
        mock_builder.from_email.assert_called_once_with('info@domain.com', 'Gold Rate Bot')
        mock_builder.to_many.assert_called_once_with([{"email": "recipient@gmail.com", "name": "Recipient"}])
        mock_builder.subject.assert_called_once_with('Gold Rate Bot Alert')
        mock_builder.build.assert_called_once()
        mock_client.emails.send.assert_called_once_with({"mock": "error_email"})
    
    @patch('app.email_service.EmailBuilder')
    @patch('app.email_service.MailerSendClient')
    def test_mailersend_exception_handling(self, mock_client_cls, mock_email_builder_cls):
        """Test handling of MailerSend exceptions."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        self.email_service = EmailService(self.mock_config)

        mock_builder = MagicMock()
        mock_email_builder_cls.return_value = mock_builder
        mock_builder.from_email.return_value = mock_builder
        mock_builder.to_many.return_value = mock_builder
        mock_builder.subject.return_value = mock_builder
        mock_builder.html.return_value = mock_builder
        mock_builder.text.return_value = mock_builder
        mock_builder.build.return_value = {"mock": "email"}
        mock_client.emails.send.side_effect = RuntimeError("MailerSend failed")
        
        # Test that exception is raised
        with pytest.raises(RuntimeError, match="MailerSend failed"):
            self.email_service.send_success_email('14903', '16110')
    
    def test_email_service_initialization(self):
        """Test EmailService initialization."""
        assert self.email_service.config == self.mock_config
