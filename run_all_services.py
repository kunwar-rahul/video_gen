#!/usr/bin/env python3
"""
Combined Development Server Launcher
Runs both the Flask API (8080) and WebSocket server (8085) in parallel
"""
import os
import sys
import threading
import logging
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from app.common.config import Config
from app.common.utils import get_logger

logger = get_logger(__name__)


def start_api_server():
    """Start the Flask API server on port 8080"""
    logger.info("Starting API server...")
    try:
        from app.api.main import create_app
        app = create_app()
        app.run(
            host='0.0.0.0',
            port=8080,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"API server failed: {e}", exc_info=True)


def start_websocket_server():
    """Start the WebSocket server on port 8085"""
    logger.info("Starting WebSocket server...")
    try:
        # Wait a bit for API server to start
        time.sleep(2)
        from app.websocket.main import WebSocketServer
        ws_server = WebSocketServer()
        ws_server.run(host='0.0.0.0', port=8085, debug=False)
    except Exception as e:
        logger.error(f"WebSocket server failed: {e}", exc_info=True)


def main():
    """Start both servers in separate threads"""
    logger.info("=" * 70)
    logger.info("Video Generation - Development Server")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Starting services:")
    logger.info("")

    # Start API server in a thread
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    time.sleep(1)

    # Start WebSocket server in a thread
    ws_thread = threading.Thread(target=start_websocket_server, daemon=True)
    ws_thread.start()

    logger.info("")
    logger.info("=" * 70)
    logger.info("Services started successfully!")
    logger.info("")
    logger.info("API Server:       http://localhost:8080")
    logger.info("  - Health Check: http://localhost:8080/health")
    logger.info("  - API Docs:     http://localhost:8080/docs (if available)")
    logger.info("")
    logger.info("WebSocket Server: ws://localhost:8085")
    logger.info("  - Real-time job updates")
    logger.info("  - Job status tracking")
    logger.info("  - Job logs streaming")
    logger.info("")
    logger.info("Frontend (React): http://localhost:3000")
    logger.info("  - Run: cd ui && npm run dev")
    logger.info("")
    logger.info("=" * 70)
    logger.info("Press Ctrl+C to stop all services")
    logger.info("=" * 70)
    logger.info("")

    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Shutting down services...")
        logger.info("Goodbye!")


if __name__ == '__main__':
    main()
