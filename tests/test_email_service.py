import pytest
from datetime import date
from unittest.mock import Mock, patch, MagicMock, call
from app.email_service import EmailService, _today_label, _success_html, _error_html
from app.config import Config


class TestEmailService:
    """Test cases for EmailService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_config = Mock(spec=Config)
        self.mock_config.MAILERSEND_API_TOKEN = 'test_api_token'
        self.mock_config.EMAIL_FROM = 'info@domain.com'
        self.mock_config.EMAIL_FROM_NAME = 'Gold Rate Bot'
        self.mock_config.EMAIL_TO = 'recipient@gmail.com'
        self.mock_config.EMAIL_TO_NAME = 'Recipient'

        self.email_service = EmailService(self.mock_config)

    def _make_builder_mock(self, mock_email_builder_cls, built_value):
        mock_builder = MagicMock()
        mock_email_builder_cls.return_value = mock_builder
        for method in ('from_email', 'to_many', 'subject', 'html', 'text', 'tag'):
            getattr(mock_builder, method).return_value = mock_builder
        mock_builder.build.return_value = built_value
        return mock_builder

    @patch('app.email_service.EmailBuilder')
    @patch('app.email_service.MailerSendClient')
    def test_send_success_email(self, mock_client_cls, mock_email_builder_cls):
        """Test sending success email uses correct subject, tag and MailerSend calls."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        self.email_service = EmailService(self.mock_config)

        mock_builder = self._make_builder_mock(mock_email_builder_cls, {"mock": "email"})

        with patch('app.email_service.date') as mock_date:
            mock_date.today.return_value = date(2026, 3, 28)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            self.email_service.send_success_email('14903', '16110')

        mock_client_cls.assert_called_once_with(api_key='test_api_token')
        mock_email_builder_cls.assert_called_once()
        mock_builder.from_email.assert_called_once_with('info@domain.com', 'Gold Rate Bot')
        mock_builder.to_many.assert_called_once_with([{"email": "recipient@gmail.com", "name": "Recipient"}])
        mock_builder.subject.assert_called_once_with('Daily Gold Rate \u2014 28 Mar 2026')
        mock_builder.tag.assert_called_once_with('investment')
        mock_builder.build.assert_called_once()
        mock_client.emails.send.assert_called_once_with({"mock": "email"})

    @patch('app.email_service.EmailBuilder')
    @patch('app.email_service.MailerSendClient')
    def test_send_error_email(self, mock_client_cls, mock_email_builder_cls):
        """Test sending error email uses correct subject and tag."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        self.email_service = EmailService(self.mock_config)

        mock_builder = self._make_builder_mock(mock_email_builder_cls, {"mock": "error_email"})

        with patch('app.email_service.date') as mock_date:
            mock_date.today.return_value = date(2026, 3, 28)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            self.email_service.send_error_email('Connection timeout')

        mock_builder.subject.assert_called_once_with('Gold Rate Alert \u2014 28 Mar 2026')
        mock_builder.tag.assert_called_once_with('investment')
        mock_client.emails.send.assert_called_once_with({"mock": "error_email"})

    @patch('app.email_service.EmailBuilder')
    @patch('app.email_service.MailerSendClient')
    def test_mailersend_exception_handling(self, mock_client_cls, mock_email_builder_cls):
        """Test that MailerSend send failures propagate."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        self.email_service = EmailService(self.mock_config)

        self._make_builder_mock(mock_email_builder_cls, {"mock": "email"})
        mock_client.emails.send.side_effect = RuntimeError("MailerSend failed")

        with pytest.raises(RuntimeError, match="MailerSend failed"):
            self.email_service.send_success_email('14903', '16110')

    def test_email_service_initialization(self):
        """Test EmailService initialization."""
        assert self.email_service.config == self.mock_config

    def test_success_html_contains_rates(self):
        """Test HTML template includes both rates."""
        html = _success_html('14903', '16110', '28 Mar 2026')
        assert '14903' in html
        assert '16110' in html
        assert '28 Mar 2026' in html
        assert 'investment' in html

    def test_error_html_contains_message(self):
        """Test error HTML template includes the error message."""
        html = _error_html('Connection timeout', '28 Mar 2026')
        assert 'Connection timeout' in html
        assert '28 Mar 2026' in html

    def test_today_label_format(self):
        """Test date label contains year."""
        label = _today_label()
        assert str(date.today().year) in label
