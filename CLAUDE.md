# CLAUDE.md — AI Agent Context

This file gives AI assistants (Claude, Cursor, Copilot, etc.) the full context
needed to work effectively on this codebase without re-exploring it from scratch.

---

## What This Project Does

**Nemo's Gold Bot** is a personal automation bot that:

1. Scrapes daily 22K and 24K gold rates from [chandukakasaraf.in](https://chandukakasaraf.in/todays-gold-rate/)
2. Sends a beautifully formatted HTML email report via [MailerSend](https://mailersend.com)
3. Runs automatically every day at **10:30 AM IST (5:00 AM UTC)** via GitHub Actions

It is personal-use software — not a multi-tenant SaaS. There is one sender and
one recipient. Simplicity is a deliberate design choice; do not over-engineer.

---

## Project Structure

```
gold-rate-bot/
├── app/
│   ├── __init__.py
│   ├── main.py            # Entry point: orchestrates scrape → email
│   ├── scraper.py         # BeautifulSoup scraper with tenacity retry
│   ├── email_service.py   # MailerSend HTML email builder
│   ├── config.py          # Env var loader and validator
│   └── logger.py          # Structured stdout logger
├── tests/
│   ├── test_main.py
│   ├── test_scraper.py
│   ├── test_email_service.py
│   ├── test_config.py
│   └── test_logger.py
├── .github/workflows/
│   ├── daily.yml          # Cron job: runs bot daily at 5 AM UTC
│   └── test.yml           # CI: runs on every push/PR to main
├── .env.example           # Template — copy to .env and fill in values
├── requirements.txt
├── Dockerfile
└── pytest.ini
```

---

## Architecture

```
main.py
  └── Config()             # Load + validate env vars
  └── GoldRateScraper()    # HTTP GET → BeautifulSoup → regex extract
  └── EmailService(config) # MailerSendClient → EmailBuilder → send
```

### Data flow

```
chandukakasaraf.in  →  scraper.py  →  main.py  →  email_service.py  →  inbox
```

- If scraping succeeds → `send_success_email(rate_22k, rate_24k)`
- If scraping fails or returns None → `send_error_email(error_message)`
- Both paths always send an email (success or alert)

---

## Key Implementation Details

### Scraper (`app/scraper.py`)
- Uses `tenacity` with `stop_after_attempt(3)` and `wait_exponential(min=4, max=10)`
- Parses `response.content` (bytes) via BeautifulSoup `html.parser`
- Extracts rates with regex: `r"22\s*KT\s*Gold\s*\|\s*₹\s*(\d+)"`
- Returns `{"22k": str, "24k": str}` or `None` if either rate is missing
- The `₹` character (U+20B9) is used literally in the regex — do not use `\u20b9` escape in the pattern string

### Email Service (`app/email_service.py`)
- Uses `MailerSendClient` + `EmailBuilder` from the `mailersend` Python SDK
- Every email gets tagged with `"investment"` for MailerSend analytics
- Subject includes today's date: `"Daily Gold Rate — 28 Mar 2026"`
- Sends both HTML and plain-text parts
- HTML template is inline in the module (no template files) — gold gradient header, two rate cards side by side, source link
- `_success_html()`, `_success_text()`, `_error_html()`, `_error_text()` are module-level functions (not class methods) so they can be tested and previewed independently

### Config (`app/config.py`)
- Required env vars: `MAILERSEND_API_TOKEN`, `EMAIL_FROM`, `EMAIL_TO`
- Optional env vars with defaults: `EMAIL_FROM_NAME`, `EMAIL_TO_NAME`
- Raises `ValueError` on startup if any required var is missing

### Logger (`app/logger.py`)
- Named logger `"gold_rate_bot"` — not root logger
- Guards against duplicate handlers with `if not logger.handlers:`
- Format: `YYYY-MM-DD HH:MM:SS LEVEL message`

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `MAILERSEND_API_TOKEN` | Yes | MailerSend API token (sending access only is fine) |
| `EMAIL_FROM` | Yes | Verified sender address (must be from a verified MailerSend domain) |
| `EMAIL_TO` | Yes | Recipient email address |
| `EMAIL_FROM_NAME` | No | Sender display name (default: `Gold Rate Bot`) |
| `EMAIL_TO_NAME` | No | Recipient display name (default: `Recipient`) |

Copy `.env.example` to `.env` and fill in values for local runs.

---

## Running Locally

All Python commands must be run inside Docker:

```bash
# Run the bot end-to-end
docker compose run --rm app python -m app.main

# Run all tests with coverage
docker compose run --rm app pytest --cov=app --cov-fail-under=100

# Preview the HTML email locally (no email sent)
python3 -c "
src = open('app/email_service.py').read().replace('from mailersend import MailerSendClient, EmailBuilder', '')
ns = {}; exec(src, ns)
open('/tmp/preview.html', 'w').write(ns['_success_html']('14903', '16110', '28 Mar 2026'))
" && open /tmp/preview.html
```

---

## Testing Standards

- **100% coverage is enforced** — CI fails if coverage drops below 100%
- All tests are unit tests with mocks — no network calls, no real emails sent
- `MailerSendClient` and `EmailBuilder` are always patched in email tests
- Logger tests must clear the `"gold_rate_bot"` logger handlers before mocking
  `StreamHandler`, and restore them in a `finally` block (the logger is a
  singleton and carries state across tests)
- `if __name__ == "__main__":` in `main.py` is marked `# pragma: no cover`

### Running specific tests

```bash
docker compose run --rm app pytest tests/test_email_service.py -v
docker compose run --rm app pytest tests/test_scraper.py -v
```

---

## GitHub Actions

### `test.yml` — runs on every push and PR to `main`
- Installs dependencies, runs full pytest suite with 100% coverage gate

### `daily.yml` — runs daily at 5:00 AM UTC (10:30 AM IST)
- Runs tests first, then executes `python -m app.main`
- Requires these GitHub Secrets:
  - `MAILERSEND_API_TOKEN`
  - `EMAIL_FROM`
  - `EMAIL_FROM_NAME`
  - `EMAIL_TO`
  - `EMAIL_TO_NAME`

---

## Common Tasks for AI Agents

### Change the email schedule
Edit the cron expression in `.github/workflows/daily.yml`.
UTC = IST − 5:30. So 10:30 AM IST = `0 5 * * *`.

### Update the email template
Edit `_success_html()` or `_error_html()` in `app/email_service.py`.
After editing, preview locally before sending:
```bash
python3 -c "..." && open /tmp/preview.html  # see Running Locally above
```

### Change the scrape source
Update `BASE_URL` and both regex patterns in `app/scraper.py`.
Run `test_scraper.py` to confirm the new patterns work.

### Add a new environment variable
1. Add to `app/config.py` (`os.getenv(...)`)
2. Add to required or optional list in `_validate_config()` if required
3. Add to `.env.example`
4. Add to GitHub Secrets section in `README.md`
5. Add to the `env:` block in `.github/workflows/daily.yml`

### Add a recipient
The current design sends to one recipient. To add more, update
`EMAIL_TO` to a comma-separated list and update `_send_email()` in
`email_service.py` to split and build the `to_many()` list.

---

## What NOT to Do

- Do not use `smtplib` or Gmail SMTP — this project uses MailerSend SDK
- Do not add a web server, database, or queue — this is a simple cron script
- Do not skip the `docker compose run` wrapper for Python commands (workspace rule)
- Do not commit `.env` — it is in `.gitignore`
- Do not reduce test coverage below 100% — the CI gate will fail
- Do not mock at too high a level in email tests — mock `MailerSendClient`
  and `EmailBuilder` at the module level, not the `send_success_email` method
