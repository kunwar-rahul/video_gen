"""
Common utilities for logging, storage, and job management.
"""
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from .config import Config


class JSONFormatter(logging.Formatter):
    """JSON log formatter."""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


def setup_logging(name: str, level: str = Config.LOG_LEVEL):
    """Configure logging for a service."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if Config.LOG_FORMAT == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_logger(name: str, level: str = Config.LOG_LEVEL):
    """Get or create a logger for a service. Alias for setup_logging."""
    return setup_logging(name, level)


class JobCache:
    """In-memory job cache with TTL support."""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._logger = setup_logging("JobCache")

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Store value in cache."""
        self._cache[key] = {
            "value": value,
            "created_at": datetime.utcnow(),
            "ttl": ttl or Config.JOB_CACHE_TTL,
        }
        self._logger.debug(f"Cache set: {key}")

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        if key not in self._cache:
            self._logger.debug(f"Cache miss: {key}")
            return None

        entry = self._cache[key]
        elapsed = (datetime.utcnow() - entry["created_at"]).total_seconds()

        if elapsed > entry["ttl"]:
            del self._cache[key]
            self._logger.debug(f"Cache expired: {key}")
            return None

        self._logger.debug(f"Cache hit: {key}")
        return entry["value"]

    def delete(self, key: str):
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
            self._logger.debug(f"Cache deleted: {key}")

    def clear(self):
        """Clear entire cache."""
        self._cache.clear()
        self._logger.debug("Cache cleared")


# Global cache instance
job_cache = JobCache()


def log_job_event(job_id: str, event: str, status: str, details: Optional[Dict] = None):
    """Log a structured job event."""
    logger = setup_logging("JobEvent")
    log_data = {
        "job_id": job_id,
        "event": event,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if details:
        log_data.update(details)
    logger.info(json.dumps(log_data))


def calculate_progress(current_step: int, total_steps: int) -> float:
    """Calculate overall progress as percentage."""
    return (current_step / total_steps) * 100 if total_steps > 0 else 0
