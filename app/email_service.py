import logging
from mailersend import MailerSendClient, EmailBuilder

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self, config):
        self.config = config
        self.client = MailerSendClient(api_key=self.config.MAILERSEND_API_TOKEN)
    
    def send_success_email(self, rate_22k: str, rate_24k: str) -> None:
        """Send email with successful gold rate fetch."""
        subject = "Daily Gold Rate"
        body = f"""Today's Gold Rate

22K Gold: ₹{rate_22k}
24K Gold: ₹{rate_24k}

Source:
https://chandukakasaraf.in/todays-gold-rate/
"""
        self._send_email(subject, body)
    
    def send_error_email(self, error_message: str) -> None:
        """Send email alert for failed gold rate fetch."""
        subject = "Gold Rate Bot Alert"
        body = f"""The gold rate could not be fetched today.

Error: {error_message}

Source:
https://chandukakasaraf.in/todays-gold-rate/
"""
        self._send_email(subject, body)
    
    def _send_email(self, subject: str, body: str) -> None:
        """Send email using MailerSend."""
        try:
            email = (
                EmailBuilder()
                .from_email(self.config.EMAIL_FROM, self.config.EMAIL_FROM_NAME)
                .to_many([{"email": self.config.EMAIL_TO, "name": self.config.EMAIL_TO_NAME}])
                .subject(subject)
                .html(body.replace("\n", "<br/>"))
                .text(body)
                .build()
            )

            self.client.emails.send(email)
            logger.info("Email sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise
