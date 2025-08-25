"""
Logging Configuration for Policy Navigator Agent
Comprehensive logging setup with file rotation and structured logging
"""

import logging
import logging.handlers
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "user_query"):
            log_data["user_query"] = record.user_query
        if hasattr(record, "response_time"):
            log_data["response_time"] = record.response_time
        if hasattr(record, "component"):
            log_data["component"] = record.component
        
        return json.dumps(log_data)

def setup_logging(log_level: str = "INFO", log_dir: str = "./logs") -> None:
    """
    Set up comprehensive logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
    """
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with simple formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for general logs with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_path / "policy_navigator.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Structured JSON log handler for analysis
    json_handler = logging.handlers.RotatingFileHandler(
        log_path / "policy_navigator_structured.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=3
    )
    json_handler.setLevel(logging.INFO)
    json_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(json_handler)
    
    # Error-specific log file
    error_handler = logging.handlers.RotatingFileHandler(
        log_path / "policy_navigator_errors.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    
    logging.info(f"Logging configured with level {log_level}, logs stored in {log_path}")

class PolicyNavigatorLogger:
    """Enhanced logger for Policy Navigator Agent with custom fields"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_query(self, query: str, component: str, level: str = "INFO"):
        """Log user query with component information"""
        extra = {"user_query": query, "component": component}
        getattr(self.logger, level.lower())(f"Processing query: {query}", extra=extra)
    
    def log_response(self, query: str, response: str, response_time: float, component: str):
        """Log agent response with timing information"""
        extra = {
            "user_query": query,
            "response_time": response_time,
            "component": component,
            "response_length": len(response)
        }
        self.logger.info(f"Generated response in {response_time:.2f}s", extra=extra)
    
    def log_error(self, error: Exception, component: str, context: Dict[str, Any] = None):
        """Log error with component and context information"""
        extra = {"component": component}
        if context:
            extra.update(context)
        
        self.logger.error(f"Error in {component}: {str(error)}", extra=extra, exc_info=True)
    
    def log_api_call(self, api_name: str, endpoint: str, status_code: int, response_time: float):
        """Log external API calls"""
        extra = {
            "component": "api_call",
            "api_name": api_name,
            "endpoint": endpoint,
            "status_code": status_code,
            "response_time": response_time
        }
        self.logger.info(f"API call to {api_name}: {status_code}", extra=extra)
    
    def log_data_operation(self, operation: str, count: int, component: str):
        """Log data operations like ingestion, indexing"""
        extra = {
            "component": component,
            "operation": operation,
            "count": count
        }
        self.logger.info(f"Data operation {operation}: {count} items", extra=extra)

def get_logger(name: str) -> PolicyNavigatorLogger:
    """Get a Policy Navigator logger instance"""
    return PolicyNavigatorLogger(name)

# Performance monitoring decorator
def log_performance(component: str):
    """Decorator to log function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            logger = get_logger(func.__module__)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.logger.debug(
                    f"Function {func.__name__} completed in {elapsed:.2f}s",
                    extra={"component": component, "function": func.__name__, "response_time": elapsed}
                )
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.log_error(e, component, {"function": func.__name__, "elapsed": elapsed})
                raise
                
        return wrapper
    return decorator

if __name__ == "__main__":
    # Test logging setup
    setup_logging("DEBUG")
    
    logger = get_logger("test")
    
    # Test different log types
    logger.log_query("Test query", "test_component")
    logger.log_response("Test query", "Test response", 1.5, "test_component")
    logger.log_api_call("TestAPI", "/test/endpoint", 200, 0.5)
    logger.log_data_operation("ingestion", 10, "data_manager")
    
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.log_error(e, "test_component", {"test_context": "value"})
    
    print("Logging test completed. Check ./logs/ directory for log files.")