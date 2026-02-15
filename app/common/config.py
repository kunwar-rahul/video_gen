"""
Configuration management for the video generation service.
"""
import os
from typing import Optional


class Config:
    """Service configuration."""

    # Storage and Asset Management
    STORAGE_URL = os.getenv("STORAGE_URL", "http://minio:9000")
    STORAGE_ACCESS_KEY = os.getenv("STORAGE_ACCESS_KEY", "minioadmin")
    STORAGE_SECRET_KEY = os.getenv("STORAGE_SECRET_KEY", "minioadmin")
    STORAGE_BUCKET = os.getenv("STORAGE_BUCKET", "video-assets")
    STORAGE_REGION = os.getenv("STORAGE_REGION", "us-east-1")

    # Pexels API
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
    PEXELS_BASE_URL = "https://api.pexels.com/videos/search"
    PEXELS_MIN_DURATION = 5  # seconds
    PEXELS_MAX_RESULTS_PER_QUERY = 5

    # Whisper Configuration
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")  # tiny, base, small, medium, large
    WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")  # cpu or cuda
    WHISPER_LANGUAGE_DETECTION = os.getenv("WHISPER_LANGUAGE_DETECTION", "true").lower() == "true"

    # TTS Configuration
    TTS_ENGINE = os.getenv("TTS_ENGINE", "gtts")  # gtts, azure, aws
    TTS_LANGUAGE = os.getenv("TTS_LANGUAGE", "en")
    TTS_VOICE = os.getenv("TTS_VOICE", "en-US-neutral")

    # FFmpeg Renderer
    FFMPEG_PRESET = os.getenv("FFMPEG_PRESET", "medium")  # ultrafast, fast, medium, slow
    VIDEO_CODEC = os.getenv("VIDEO_CODEC", "libx264")
    AUDIO_CODEC = os.getenv("AUDIO_CODEC", "aac")
    VIDEO_BITRATE = os.getenv("VIDEO_BITRATE", "5000k")
    AUDIO_BITRATE = os.getenv("AUDIO_BITRATE", "192k")
    TARGET_FPS = int(os.getenv("TARGET_FPS", "30"))
    TARGET_RESOLUTION = os.getenv("TARGET_RESOLUTION", "1920x1080")

    # Service URLs (for inter-service communication)
    ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://orchestrator:8081")
    RETRIEVER_URL = os.getenv("RETRIEVER_URL", "http://retriever:8082")
    WHISPER_URL = os.getenv("WHISPER_URL", "http://whisper:8083")
    RENDERER_URL = os.getenv("RENDERER_URL", "http://renderer:8084")

    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8080"))
    API_WORKERS = int(os.getenv("API_WORKERS", "4"))
    
    # Job Queue and Cache
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
    JOB_CACHE_ENABLED = os.getenv("JOB_CACHE_ENABLED", "true").lower() == "true"
    JOB_CACHE_TTL = int(os.getenv("JOB_CACHE_TTL", "86400"))  # 24 hours

    # Asset Caching
    ASSET_CACHE_ENABLED = os.getenv("ASSET_CACHE_ENABLED", "true").lower() == "true"
    ASSET_CACHE_SIZE_MB = int(os.getenv("ASSET_CACHE_SIZE_MB", "1000"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # json or text

    # Advanced Features
    ENABLE_STYLE_TRANSFER = os.getenv("ENABLE_STYLE_TRANSFER", "false").lower() == "true"
    ENABLE_WEBHOOKS = os.getenv("ENABLE_WEBHOOKS", "true").lower() == "true"
    WEBHOOK_TIMEOUT = int(os.getenv("WEBHOOK_TIMEOUT", "30"))

    # Job Processing
    MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "5"))
    JOB_TIMEOUT = int(os.getenv("JOB_TIMEOUT", "3600"))  # 1 hour in seconds
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))  # seconds

    # Scene Planning
    DEFAULT_SCENE_DURATION = float(os.getenv("DEFAULT_SCENE_DURATION", "5.0"))
    MIN_VIDEO_DURATION = int(os.getenv("MIN_VIDEO_DURATION", "10"))
    MAX_VIDEO_DURATION = int(os.getenv("MAX_VIDEO_DURATION", "600"))

    # Authentication
    API_KEY_REQUIRED = os.getenv("API_KEY_REQUIRED", "true").lower() == "true"
    AUTH_TOKEN_EXPIRY = int(os.getenv("AUTH_TOKEN_EXPIRY", "86400"))  # 24 hours

    # Monitoring
    METRICS_ENABLED = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    TRACING_ENABLED = os.getenv("TRACING_ENABLED", "true").lower() == "true"
    TRACE_SAMPLE_RATE = float(os.getenv("TRACE_SAMPLE_RATE", "0.1"))  # 10%

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        if not cls.PEXELS_API_KEY:
            print("Warning: PEXELS_API_KEY not set. Pexels integration will not work.")
        return True
