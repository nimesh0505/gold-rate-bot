import logging
from typing import Optional
from .scraper import GoldRateScraper
from .email_service import EmailService
from .config import Config
from .logger import setup_logger

def main() -> None:
    """Main function to fetch and email gold rates."""
    logger = setup_logger()
    config = Config()
    scraper = GoldRateScraper()
    email_service = EmailService(config)
    
    try:
        logger.info("Fetching gold rate")
        gold_rates = scraper.fetch_gold_rates()
        
        if gold_rates:
            rate_22k = gold_rates.get("22k")
            rate_24k = gold_rates.get("24k")
            logger.info(f"Extracted 22K=₹{rate_22k} 24K=₹{rate_24k}")
            
            email_service.send_success_email(rate_22k, rate_24k)
            logger.info("Email sent successfully")
        else:
            logger.error("No gold rates found")
            email_service.send_error_email("No gold rates found on the page")
            
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        email_service.send_error_email(f"Error: {str(e)}")

if __name__ == "__main__":  # pragma: no cover
    main()
