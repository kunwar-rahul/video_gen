#!/usr/bin/env python3
"""
Standalone WebSocket Server Launcher
Runs on port 8085 to handle real-time job updates
"""
import os
import sys
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.common.config import Config
from app.common.utils import get_logger
from app.websocket.main import WebSocketServer

logger = get_logger(__name__)


def main():
    """Start the WebSocket server"""
    logger.info("=" * 60)
    logger.info("Video Generation - WebSocket Server")
    logger.info("=" * 60)

    try:
        # Create and run WebSocket server
        ws_server = WebSocketServer()

        logger.info(f"WebSocket Server Configuration:")
        logger.info(f"  - Host: 0.0.0.0")
        logger.info(f"  - Port: 8085")
        logger.info(f"  - CORS: Enabled (all origins)")
        logger.info(f"  - Redis: {Config.REDIS_URL}")
        logger.info("=" * 60)

        # Run server
        ws_server.run(host='0.0.0.0', port=8085, debug=False)

    except Exception as e:
        logger.error(f"Failed to start WebSocket server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
