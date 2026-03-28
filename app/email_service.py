import logging
from datetime import date
from mailersend import MailerSendClient, EmailBuilder

logger = logging.getLogger(__name__)

SOURCE_URL = "https://chandukakasaraf.in/todays-gold-rate/"

def _today_label() -> str:
    return date.today().strftime("%-d %b %Y")

def _success_html(rate_22k: str, rate_24k: str, today: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
  *{{margin:0;padding:0;box-sizing:border-box;}}
  body{{font-family:'Inter',Arial,sans-serif;background:#f5f0e8;color:#2c2c2c;}}
  .wrapper{{max-width:560px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.10);}}
  .header{{background:linear-gradient(135deg,#b8860b 0%,#ffd700 60%,#b8860b 100%);padding:36px 32px 28px;text-align:center;}}
  .header .logo{{font-size:28px;font-weight:700;color:#fff;letter-spacing:1px;text-shadow:0 2px 6px rgba(0,0,0,0.18);}}
  .header .subtitle{{color:rgba(255,255,255,0.88);font-size:13px;margin-top:4px;letter-spacing:0.5px;}}
  .date-badge{{display:inline-block;background:rgba(255,255,255,0.22);border:1px solid rgba(255,255,255,0.4);border-radius:20px;padding:5px 16px;color:#fff;font-size:12px;font-weight:600;margin-top:12px;letter-spacing:0.5px;}}
  .body{{padding:36px 32px;}}
  .intro{{font-size:15px;color:#555;margin-bottom:28px;line-height:1.6;}}
  .rates{{display:flex;gap:32px;margin-bottom:32px;}}
  .rate-card{{flex:1;border-radius:12px;padding:24px 20px;text-align:center;border:1.5px solid #f0e0b0;background:linear-gradient(145deg,#fffdf5,#fff9e6);}}
  .rate-card .karat{{font-size:12px;font-weight:700;letter-spacing:1.5px;color:#b8860b;text-transform:uppercase;margin-bottom:8px;}}
  .rate-card .price{{font-size:28px;font-weight:700;color:#1a1a1a;}}
  .rate-card .currency{{font-size:18px;color:#b8860b;margin-right:2px;}}
  .rate-card .unit{{font-size:11px;color:#999;margin-top:6px;}}
  .divider{{height:1px;background:#f0e0b0;margin:0 0 28px 0;}}
  .source-section{{background:#fdfaf2;border-radius:10px;padding:16px 20px;margin-bottom:28px;border:1px solid #f0e0b0;}}
  .source-section .label{{font-size:11px;font-weight:700;color:#b8860b;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;}}
  .source-section a{{font-size:13px;color:#2563eb;text-decoration:none;word-break:break-all;}}
  .footer{{background:#faf8f3;padding:24px 32px;text-align:center;border-top:1px solid #f0e0b0;}}
  .footer p{{font-size:12px;color:#aaa;line-height:1.8;}}
  .footer a{{color:#b8860b;text-decoration:none;}}
  .tag{{display:inline-block;background:#fef9e7;border:1px solid #ffd700;border-radius:12px;padding:3px 10px;font-size:11px;font-weight:600;color:#b8860b;margin-top:8px;}}
</style>
</head>
<body>
<div class="wrapper">
    <div class="header">
    <div class="logo">&#x1F947; Nemo's Gold Bot</div>
    <div class="subtitle">Daily Gold Rate Report</div>
    <div class="date-badge">&#x1F4C5; {today}</div>
  </div>
  <div class="body">
    <p class="intro">Here are today's gold rates. Prices are per gram and sourced directly from <a href="{SOURCE_URL}" style="color:#b8860b;text-decoration:none;">Chandukaka Saraf</a>.</p>
    <div class="rates">
      <div class="rate-card">
        <div class="karat">22K Gold</div>
        <div class="price"><span class="currency">&#x20B9;</span>{rate_22k}</div>
        <div class="unit">per gram &nbsp;·&nbsp; 91.6% purity</div>
      </div>
      <div class="rate-card">
        <div class="karat">24K Gold</div>
        <div class="price"><span class="currency">&#x20B9;</span>{rate_24k}</div>
        <div class="unit">per gram &nbsp;·&nbsp; 99.9% purity</div>
      </div>
    </div>
    <div class="divider"></div>
    <div class="source-section">
      <div class="label">&#x1F517; Source</div>
      <a href="{SOURCE_URL}">{SOURCE_URL}</a>
    </div>
    <div>
      <span class="tag">#investment</span>
    </div>
  </div>
  <div class="footer">
    <p>You are receiving this because you subscribed to daily gold rate alerts.<br/>
    <a href="{SOURCE_URL}">Chandukaka Saraf</a> &nbsp;·&nbsp; Powered by Gold Rate Bot</p>
  </div>
</div>
</body>
</html>"""


def _success_text(rate_22k: str, rate_24k: str, today: str) -> str:
    return f"""Daily Gold Rate — {today}

22K Gold : ₹{rate_22k} per gram (91.6% purity)
24K Gold : ₹{rate_24k} per gram (99.9% purity)

Source: {SOURCE_URL}
"""


def _error_html(error_message: str, today: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
  *{{margin:0;padding:0;box-sizing:border-box;}}
  body{{font-family:'Inter',Arial,sans-serif;background:#f5f0e8;color:#2c2c2c;}}
  .wrapper{{max-width:560px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.10);}}
  .header{{background:linear-gradient(135deg,#b8860b 0%,#ffd700 60%,#b8860b 100%);padding:36px 32px 28px;text-align:center;}}
  .header .logo{{font-size:28px;font-weight:700;color:#fff;letter-spacing:1px;text-shadow:0 2px 6px rgba(0,0,0,0.18);}}
  .header .subtitle{{color:rgba(255,255,255,0.88);font-size:13px;margin-top:4px;}}
  .date-badge{{display:inline-block;background:rgba(255,255,255,0.22);border:1px solid rgba(255,255,255,0.4);border-radius:20px;padding:5px 16px;color:#fff;font-size:12px;font-weight:600;margin-top:12px;}}
  .body{{padding:36px 32px;}}
  .alert-box{{background:#fff5f5;border-left:4px solid #e53e3e;border-radius:8px;padding:20px 24px;margin-bottom:24px;}}
  .alert-box .alert-title{{font-size:15px;font-weight:700;color:#c53030;margin-bottom:8px;}}
  .alert-box .alert-msg{{font-size:13px;color:#555;font-family:monospace;word-break:break-all;}}
  .source-section{{background:#fdfaf2;border-radius:10px;padding:16px 20px;border:1px solid #f0e0b0;}}
  .source-section .label{{font-size:11px;font-weight:700;color:#b8860b;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;}}
  .source-section a{{font-size:13px;color:#2563eb;text-decoration:none;}}
  .footer{{background:#faf8f3;padding:24px 32px;text-align:center;border-top:1px solid #f0e0b0;}}
  .footer p{{font-size:12px;color:#aaa;line-height:1.8;}}
  .footer a{{color:#b8860b;text-decoration:none;}}
</style>
</head>
<body>
<div class="wrapper">
  <div class="header">
    <div class="logo">&#x1F947; Nemo's Gold Bot</div>
    <div class="subtitle">Gold Rate Alert</div>
    <div class="date-badge">&#x1F4C5; {today}</div>
  </div>
  <div class="body">
    <div class="alert-box">
      <div class="alert-title">&#x26A0;&#xFE0F; Could not fetch today's gold rate</div>
      <div class="alert-msg">{error_message}</div>
    </div>
    <div class="source-section">
      <div class="label">&#x1F517; Source</div>
      <a href="{SOURCE_URL}">{SOURCE_URL}</a>
    </div>
  </div>
  <div class="footer">
    <p>Gold Rate Bot &nbsp;·&nbsp; <a href="{SOURCE_URL}">Chandukaka Saraf</a></p>
  </div>
</div>
</body>
</html>"""


def _error_text(error_message: str, today: str) -> str:
    return f"""Gold Rate Alert — {today}

Could not fetch today's gold rate.
Error: {error_message}

Source: {SOURCE_URL}
"""


class EmailService:
    """Service for sending email notifications."""

    def __init__(self, config):
        self.config = config
        self.client = MailerSendClient(api_key=self.config.MAILERSEND_API_TOKEN)

    def send_success_email(self, rate_22k: str, rate_24k: str) -> None:
        """Send email with successful gold rate fetch."""
        today = _today_label()
        subject = f"Daily Gold Rate — {today}"
        self._send_email(
            subject=subject,
            html=_success_html(rate_22k, rate_24k, today),
            text=_success_text(rate_22k, rate_24k, today),
        )

    def send_error_email(self, error_message: str) -> None:
        """Send email alert for failed gold rate fetch."""
        today = _today_label()
        subject = f"Gold Rate Alert — {today}"
        self._send_email(
            subject=subject,
            html=_error_html(error_message, today),
            text=_error_text(error_message, today),
        )

    def _send_email(self, subject: str, html: str, text: str) -> None:
        """Send email using MailerSend."""
        try:
            email = (
                EmailBuilder()
                .from_email(self.config.EMAIL_FROM, self.config.EMAIL_FROM_NAME)
                .to_many([{"email": self.config.EMAIL_TO, "name": self.config.EMAIL_TO_NAME}])
                .subject(subject)
                .html(html)
                .text(text)
                .tag("investment")
                .build()
            )
            self.client.emails.send(email)
            logger.info("Email sent successfully")
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise
