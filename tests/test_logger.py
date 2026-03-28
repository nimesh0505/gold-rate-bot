import pytest
import logging
from unittest.mock import patch, MagicMock
from app.logger import setup_logger


class TestLogger:
    """Test cases for logger setup."""
    
    def test_setup_logger_creates_logger(self):
        """Test that setup_logger creates a logger with correct configuration."""
        logger = setup_logger()
        
        # Verify logger name
        assert logger.name == "gold_rate_bot"
        
        # Verify log level
        assert logger.level == logging.INFO
        
        # Verify handler is created
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)
    
    def test_setup_logger_formatter(self):
        """Test that logger has correct formatter."""
        logger = setup_logger()
        handler = logger.handlers[0]
        
        # Verify formatter
        assert isinstance(handler.formatter, logging.Formatter)
        assert handler.formatter._fmt == '%(asctime)s %(levelname)s %(message)s'
        assert handler.formatter.datefmt == '%Y-%m-%d %H:%M:%S'
    
    def test_setup_logger_idempotent(self):
        """Test that calling setup_logger multiple times doesn't add duplicate handlers."""
        logger1 = setup_logger()
        initial_handler_count = len(logger1.handlers)
        
        logger2 = setup_logger()
        
        # Should be the same logger instance
        assert logger1 is logger2
        # Should not add duplicate handlers
        assert len(logger2.handlers) == initial_handler_count
    
    @patch('app.logger.logging.StreamHandler')
    def test_setup_logger_with_mock_handler(self, mock_stream_handler):
        """Test setup_logger with mocked handler."""
        mock_handler = MagicMock()
        mock_stream_handler.return_value = mock_handler
        
        logger = setup_logger()
        
        # Verify StreamHandler was created
        mock_stream_handler.assert_called_once()
        
        # Verify handler was added to logger
        assert mock_handler in logger.handlers
        
        # Verify formatter was set
        mock_handler.setFormatter.assert_called_once()
    
    def test_logger_info_level(self):
        """Test that logger can log info messages."""
        logger = setup_logger()
        
        with patch.object(logger.handlers[0], 'emit') as mock_emit:
            logger.info("Test info message")
            
            # Verify emit was called
            mock_emit.assert_called_once()
            
            # Verify log record
            log_record = mock_emit.call_args[0][0]
            assert log_record.levelname == "INFO"
            assert log_record.getMessage() == "Test info message"
    
    def test_logger_error_level(self):
        """Test that logger can log error messages."""
        logger = setup_logger()
        
        with patch.object(logger.handlers[0], 'emit') as mock_emit:
            logger.error("Test error message")
            
            # Verify emit was called
            mock_emit.assert_called_once()
            
            # Verify log record
            log_record = mock_emit.call_args[0][0]
            assert log_record.levelname == "ERROR"
            assert log_record.getMessage() == "Test error message"
    
    def test_logger_timestamp_format(self):
        """Test that log messages include correct timestamp format."""
        logger = setup_logger()
        
        with patch.object(logger.handlers[0], 'emit') as mock_emit:
            logger.info("Test message")
            
            # Get the formatted message
            log_record = mock_emit.call_args[0][0]
            formatted_message = logger.handlers[0].formatter.format(log_record)
            
            # Verify timestamp format (YYYY-MM-DD HH:MM:SS)
            import re
            timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
            assert re.match(timestamp_pattern + ' INFO Test message', formatted_message)
