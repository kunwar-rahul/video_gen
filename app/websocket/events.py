"""
WebSocket Event Manager - Bridges API and microservices to WebSocket broadcasts
"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Store reference to WebSocket server (set during app initialization)
_ws_server_instance = None


def set_ws_server(ws_server):
    """Set the WebSocket server instance"""
    global _ws_server_instance
    _ws_server_instance = ws_server


def get_ws_server():
    """Get the WebSocket server instance"""
    return _ws_server_instance


class WebSocketEventManager:
    """Manager for broadcasting events to connected WebSocket clients"""

    @staticmethod
    def broadcast_job_status(job_id: str, status: str, progress: int, message: str = None):
        """Broadcast job status update"""
        ws = get_ws_server()
        if ws:
            try:
                ws.broadcast_job_status(job_id, status, progress, message)
            except Exception as e:
                logger.error(f'Failed to broadcast job status: {e}', exc_info=True)

    @staticmethod
    def broadcast_job_log(job_id: str, level: str, message: str):
        """Broadcast job log entry"""
        ws = get_ws_server()
        if ws:
            try:
                ws.broadcast_job_log(job_id, level, message)
            except Exception as e:
                logger.error(f'Failed to broadcast job log: {e}', exc_info=True)

    @staticmethod
    def broadcast_job_completed(job_id: str, video_url: str, duration: float):
        """Broadcast job completion"""
        ws = get_ws_server()
        if ws:
            try:
                ws.broadcast_job_completed(job_id, video_url, duration)
            except Exception as e:
                logger.error(f'Failed to broadcast job completed: {e}', exc_info=True)

    @staticmethod
    def broadcast_job_failed(job_id: str, error_message: str):
        """Broadcast job failure"""
        ws = get_ws_server()
        if ws:
            try:
                ws.broadcast_job_failed(job_id, error_message)
            except Exception as e:
                logger.error(f'Failed to broadcast job failed: {e}', exc_info=True)

    @staticmethod
    def broadcast_queue_update(queued_count: int, processing_count: int):
        """Broadcast queue status update"""
        ws = get_ws_server()
        if ws:
            try:
                ws.broadcast_queue_update(queued_count, processing_count)
            except Exception as e:
                logger.error(f'Failed to broadcast queue update: {e}', exc_info=True)
