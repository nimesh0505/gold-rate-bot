import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self, config):
        self.config = config
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
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
        """Send email using Gmail SMTP."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.EMAIL_USER
            msg['To'] = self.config.EMAIL_TO
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.config.EMAIL_USER, self.config.EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            logger.info("Email sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise
