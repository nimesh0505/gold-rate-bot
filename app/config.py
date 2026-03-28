import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for environment variables."""
    
    def __init__(self):
        self.MAILERSEND_API_TOKEN = os.getenv("MAILERSEND_API_TOKEN")
        self.EMAIL_FROM = os.getenv("EMAIL_FROM")
        self.EMAIL_TO = os.getenv("EMAIL_TO")
        self.EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Gold Rate Bot")
        self.EMAIL_TO_NAME = os.getenv("EMAIL_TO_NAME", "Recipient")
        
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate required environment variables."""
        required_vars = ["MAILERSEND_API_TOKEN", "EMAIL_FROM", "EMAIL_TO"]
        missing_vars = [var for var in required_vars if not getattr(self, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
