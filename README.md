# Gold Rate Bot

A production-ready Python bot that scrapes daily gold rates from chandukakasaraf.in and sends email notifications with comprehensive testing, CI/CD, and deployment automation.

## Features

- **Retry-safe scraping** with exponential backoff (3 attempts)
- **Email alerts** for success and failure cases via MailerSend
- **Docker support** for easy containerized deployment
- **GitHub Actions scheduler** running daily at 4:00 AM UTC
- **Structured logging** with timestamps and log levels
- **Environment-based configuration** management
- **100% test coverage** with comprehensive test suite
- **CI/CD pipeline** with automated testing and deployment
- **Coverage reporting** with HTML and terminal output

## Project Structure

```
gold-rate-bot/
├── app/                          # Main application code
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Main application entry point
│   ├── scraper.py               # Web scraping logic with retry
│   ├── email_service.py         # MailerSend email service
│   ├── config.py                # Environment configuration
│   └── logger.py                # Structured logging setup
├── tests/                        # Comprehensive test suite
│   ├── __init__.py              # Test package initialization
│   ├── test_scraper.py          # Web scraping tests
│   ├── test_email_service.py    # Email service tests (mocked)
│   ├── test_config.py           # Configuration tests
│   ├── test_logger.py           # Logging tests
│   └── test_main.py             # Main application flow tests
├── .github/                      # GitHub workflows
│   └── workflows/
│       ├── daily.yml            # Daily scheduler workflow
│       └── test.yml             # Test and coverage workflow
├── requirements.txt              # Python dependencies
├── Dockerfile                   # Docker configuration
├── .env.example                 # Environment variables template
├── pytest.ini                   # Pytest configuration
├── Makefile                     # Development commands
└── README.md                    # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- MailerSend account with a verified sender domain
- Docker (optional, for containerized deployment)

### 1. Clone and Setup

```bash
git clone <your-repository-url>
cd gold-rate-bot
```

### 2. Install Dependencies

```bash
# Option 1: Using pip
pip install -r requirements.txt

# Option 2: Using Makefile
make install
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env  # or use your preferred editor
```

Add your MailerSend credentials:
```env
MAILERSEND_API_TOKEN=your_mailersend_api_token
EMAIL_FROM=info@domain.com
EMAIL_TO=recipient@domain.com
EMAIL_FROM_NAME=Gold Rate Bot
EMAIL_TO_NAME=Recipient
```

### 4. Run the Bot

```bash
# Option 1: Direct execution
python -m app.main

# Option 2: Using Makefile
make test  # Run tests first
python -m app.main  # Then run the bot
```

## Docker Deployment

### Build and Run with Docker

```bash
# Build the Docker image
docker build -t gold-rate-bot .

# Run with environment file
docker run --env-file .env gold-rate-bot

# Run in detached mode
docker run -d --env-file .env --name gold-rate-bot gold-rate-bot
```

### Docker Compose (Optional)

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  gold-rate-bot:
    build: .
    env_file:
      - .env
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## MailerSend Setup

1. Create a MailerSend account and verify a sender domain.
2. Generate an API token with permission to send emails.
3. Use a sender address from your verified domain.
4. Update your `.env` file with:
   ```env
   MAILERSEND_API_TOKEN=your_mailersend_api_token
   EMAIL_FROM=info@domain.com
   EMAIL_TO=recipient@domain.com
   EMAIL_FROM_NAME=Gold Rate Bot
   EMAIL_TO_NAME=Recipient
   ```

## Testing

### Running Tests Locally

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing

# Using Makefile
make test          # Run tests
make coverage      # Run with coverage report
make test-verbose  # Verbose output
make clean         # Clean cache files
```

### Test Coverage Requirements

- **Target Coverage**: 100%
- **Coverage Reports**: HTML and terminal
- **Branch Coverage**: Enabled
- **Fail Threshold**: 100% (CI will fail if coverage drops)

### Test Categories

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **Mocked Tests**: Email sending is mocked to avoid spam
4. **Realistic Tests**: Scraping tests use actual website patterns

## CI/CD Pipeline

### GitHub Actions Workflows

#### 1. Test Workflow (`.github/workflows/test.yml`)
- Triggers on PRs to main branch
- Triggers on pushes to main branch
- Runs full test suite with coverage
- Uploads coverage reports to Codecov
- Fails if coverage < 100%

#### 2. Daily Bot Workflow (`.github/workflows/daily.yml`)
- Runs daily at 4:00 AM UTC
- Manual trigger available
- Runs tests before production execution
- Sends gold rate emails on success
- Sends error alerts on failure

### Branch Protection Rules (Recommended)

1. **Require Pull Request Reviews**
2. **Require Status Checks to Pass**
   - `Test Suite (test)`
   - Coverage must be 100%
3. **Require Up to Date Branches**
4. **Include Administrators**

## GitHub Secrets Configuration

### Required Secrets

Go to your repository → Settings → Secrets and variables → Actions

Add the following secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `MAILERSEND_API_TOKEN` | MailerSend API token | `ms_...` |
| `EMAIL_FROM` | Verified sender address | `info@domain.com` |
| `EMAIL_TO` | Recipient email address | `recipient@gmail.com` |
| `EMAIL_FROM_NAME` | Sender display name | `Gold Rate Bot` |
| `EMAIL_TO_NAME` | Recipient display name | `Recipient` |

### Setting Up Secrets:

1. Navigate to repository settings
2. Click "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add each secret from the table above

## Monitoring and Debugging

### Log Analysis

The bot provides structured logging:
```
2026-03-07 09:00:01 INFO Fetching gold rate
2026-03-07 09:00:02 INFO Extracted 22K=₹14903 24K=₹16110
2026-03-07 09:00:03 INFO Email sent successfully
```

### Error Handling

- **Network Failures**: Automatic retry with exponential backoff (3 attempts)
- **Parsing Errors**: Alert email sent with error details
- **Email Failures**: Logged with detailed error messages
- **Configuration Errors**: Clear error messages for missing variables

### Monitoring Locations

1. **GitHub Actions Logs**: Check workflow runs for execution status
2. **Email Notifications**: Monitor daily rates or error alerts
3. **Coverage Reports**: HTML reports in `htmlcov/` directory
4. **Docker Logs**: `docker logs gold-rate-bot`

## Development Workflow

### Making Changes

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make Changes and Test**
   ```bash
   # Write code
   make test  # Run tests
   make coverage  # Check coverage
   ```

3. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin feature/new-feature
   ```

4. **Create Pull Request**
   - Tests will run automatically
   - Coverage must be 100%
   - Code review required

5. **Merge to Main**
   - Triggers production workflow
   - Bot runs daily with new changes

### Local Development Tips

```bash
# Install development dependencies
pip install -r requirements.txt

# Run specific test file
pytest tests/test_scraper.py -v

# Run specific test function
pytest tests/test_scraper.py::TestGoldRateScraper::test_fetch_gold_rates_success -v

# Run with coverage for specific file
pytest --cov=app.scraper tests/test_scraper.py

# Clean up cache files
make clean
```

## Performance and Reliability

### Retry Logic

The scraper implements robust retry logic:
- **Maximum Attempts**: 3 retries
- **Backoff Strategy**: Exponential backoff
- **Base Delay**: 1 second
- **Maximum Delay**: 10 seconds
- **Timeout**: 10 seconds per request

### Error Recovery

- **Network Timeouts**: Automatic retry with longer timeouts
- **Parsing Failures**: Email alerts with error details
- **Email Provider Failures**: Detailed logging and error reporting
- **Configuration Issues**: Clear validation messages

## Deployment Options

### 1. GitHub Actions (Recommended)
- Free hosting
- Automated scheduling
- Built-in CI/CD
- Integrated monitoring

### 2. Docker Container
- Portable deployment
- Environment isolation
- Easy scaling
- Local testing

### 3. Local Machine
- Simple setup
- Full control
- Manual scheduling
- Direct monitoring

### 4. Cloud Services
- AWS Lambda (serverless)
- Google Cloud Functions
- Azure Functions
- Heroku

## Troubleshooting

### Common Issues

#### 1. MailerSend Authentication Failed
**Problem**: API authentication or authorization error
**Solution**: 
- Verify `MAILERSEND_API_TOKEN`
- Confirm your sender domain and `EMAIL_FROM` are verified
- Check token permissions in MailerSend dashboard

#### 2. No Gold Rates Found
**Problem**: `No gold rates found on the page`
**Solution**:
- Check website accessibility
- Verify HTML structure hasn't changed
- Review scraper regex patterns

#### 3. Test Coverage Below 100%
**Problem**: Coverage < 100% in CI
**Solution**:
- Run `make coverage` locally
- Review uncovered lines
- Add tests for uncovered code

#### 4. Docker Build Fails
**Problem**: Build errors during Docker build
**Solution**:
- Check Python version compatibility
- Verify requirements.txt format
- Review Dockerfile syntax

### Debug Mode

Enable debug logging by modifying `app/logger.py`:
```python
logger.setLevel(logging.DEBUG)  # Change from INFO to DEBUG
```

### Getting Help

1. **Check Logs**: Review GitHub Actions logs
2. **Run Locally**: Test with `python -m app.main`
3. **Check Coverage**: Ensure 100% test coverage
4. **Review Documentation**: Read this README thoroughly

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure 100% test coverage
6. Submit a pull request

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing issues for solutions
- Review documentation thoroughly

---

**Happy Gold Rate Monitoring!** 

This bot will automatically send you daily gold rate updates and alert you if there are any issues. With 100% test coverage and robust error handling, you can rely on it for accurate and timely gold rate information.
