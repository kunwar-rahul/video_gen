"""
Local development server - runs all services in a single process without Docker.
This is useful for development and testing without Docker installation.

Run with: python local_dev.py
"""

import sys
import os
import threading
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.common.config import Config
from app.common.utils import setup_logging

logger = setup_logging("LocalDev")


def run_api_server():
    """Run API server in thread."""
    try:
        from app.api.main import VideoGenerationAPI
        logger.info("Starting API server...")
        api = VideoGenerationAPI()
        api.run(host="0.0.0.0", port=8080)
    except Exception as e:
        logger.error(f"API server failed: {e}", exc_info=True)


def run_status_monitor():
    """Monitor and display service status."""
    try:
        import requests
        while True:
            time.sleep(5)
            try:
                response = requests.get("http://localhost:8080/health", timeout=2)
                if response.status_code == 200:
                    logger.info("✓ API server is healthy")
            except:
                pass
    except Exception as e:
        logger.error(f"Monitor failed: {e}")


def main():
    """Run services locally."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║  Text-to-Video Generation Service - Local Development    ║
╚═══════════════════════════════════════════════════════════╝

Configuration:
""")
    
    print(f"  API Host:        {Config.API_HOST}:{Config.API_PORT}")
    print(f"  Storage:         {Config.STORAGE_URL}")
    print(f"  Redis:           {Config.REDIS_URL}")
    print(f"  Log Level:       {Config.LOG_LEVEL}")
    print(f"  Pexels API Key:  {'✓ Set' if Config.PEXELS_API_KEY else '✗ Not set'}")
    print(f"\nStarting services...\n")
    
    # Validate config
    Config.validate()
    
    # Start API server in main thread (blocking)
    # Other services would be threaded, but keeping simple for MVP
    logger.info("=" * 60)
    logger.info("Local Development Server Ready")
    logger.info("=" * 60)
    logger.info(f"API available at: http://localhost:{Config.API_PORT}")
    logger.info(f"Health check:     http://localhost:{Config.API_PORT}/health")
    logger.info("")
    logger.info("Test with:")
    logger.info(f"  curl http://localhost:{Config.API_PORT}/health")
    logger.info("")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    # Run API server (blocking)
    try:
        from flask_cors import CORS
        from app.api.main import VideoGenerationAPI
        
        api = VideoGenerationAPI()
        CORS(api.app)
        api.app.config['JSON_SORT_KEYS'] = False
        
        logger.info("Running on http://0.0.0.0:8080")
        api.app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
