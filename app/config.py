import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """Configuration class for environment variables."""
    
    def __init__(self):
        self.EMAIL_USER = os.getenv("EMAIL_USER")
        self.EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
        self.EMAIL_TO = os.getenv("EMAIL_TO")
        
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate required environment variables."""
        required_vars = ["EMAIL_USER", "EMAIL_PASSWORD", "EMAIL_TO"]
        missing_vars = [var for var in required_vars if not getattr(self, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
