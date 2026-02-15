"""
WebSocket Server for Real-time Job Updates
"""
import os
import json
import logging
from datetime import datetime
from functools import wraps

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask_cors import CORS
import redis

from app.common.config import Config
from app.common.utils import get_logger

logger = get_logger(__name__)

# Redis connection for pub/sub
redis_client = redis.from_url(Config.REDIS_URL)


class WebSocketServer:
    """WebSocket server for real-time job updates"""

    def __init__(self, app: Flask = None, socketio: SocketIO = None):
        self.app = app or Flask(__name__)
        CORS(self.app, origins=['http://localhost:3000', 'http://localhost:3001', 'http://127.0.0.1:3000', 'http://127.0.0.1:3001'], supports_credentials=True)
        self.socketio = socketio or SocketIO(self.app, cors_allowed_origins=['http://localhost:3000', 'http://localhost:3001', 'http://127.0.0.1:3000', 'http://127.0.0.1:3001'], async_mode='threading')
        self.setup_routes()
        self.setup_event_handlers()

    def setup_routes(self):
        """Setup Flask routes"""
        @self.app.route('/health', methods=['GET'])
        def health():
            return {'status': 'healthy', 'service': 'websocket'}, 200

    def setup_event_handlers(self):
        """Setup WebSocket event handlers"""

        @self.socketio.on('connect')
        def handle_connect():
            logger.info(f'Client connected: {request.sid}')
            emit('connected', {'data': 'Connected to WebSocket server'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info(f'Client disconnected: {request.sid}')

        @self.socketio.on('subscribe_job')
        def handle_subscribe_job(data):
            job_id = data.get('jobId')
            if job_id:
                room = f'job_{job_id}'
                join_room(room)
                logger.info(f'Client {request.sid} subscribed to job {job_id}')
                emit('subscribed', {'jobId': job_id})

        @self.socketio.on('unsubscribe_job')
        def handle_unsubscribe_job(data):
            job_id = data.get('jobId')
            if job_id:
                room = f'job_{job_id}'
                leave_room(room)
                logger.info(f'Client {request.sid} unsubscribed from job {job_id}')

        @self.socketio.on('get_active_jobs')
        def handle_get_active_jobs():
            # Return number of connected clients
            emit('active_jobs', {'count': len(self.socketio.server.clients)})

    def broadcast_job_status(self, job_id: str, status: str, progress: int, message: str = None):
        """Broadcast job status update to all subscribers"""
        room = f'job_{job_id}'
        payload = {
            'jobId': job_id,
            'status': status,
            'progress': progress,
            'timestamp': datetime.utcnow().isoformat()
        }
        if message:
            payload['message'] = message

        logger.debug(f'Broadcasting job status: {payload}')
        self.socketio.emit('job_status_update', payload, to=room)

    def broadcast_job_log(self, job_id: str, level: str, message: str):
        """Broadcast job log entry to all subscribers"""
        room = f'job_{job_id}'
        payload = {
            'jobId': job_id,
            'level': level,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.debug(f'Broadcasting job log: {payload}')
        self.socketio.emit('job_log_entry', payload, to=room)

    def broadcast_job_completed(self, job_id: str, video_url: str, duration: float):
        """Broadcast job completion to all subscribers"""
        room = f'job_{job_id}'
        payload = {
            'jobId': job_id,
            'videoUrl': video_url,
            'duration': duration,
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f'Broadcasting job completed: {payload}')
        self.socketio.emit('job_completed', payload, to=room)

    def broadcast_job_failed(self, job_id: str, error_message: str):
        """Broadcast job failure to all subscribers"""
        room = f'job_{job_id}'
        payload = {
            'jobId': job_id,
            'errorMessage': error_message,
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.error(f'Broadcasting job failed: {payload}')
        self.socketio.emit('job_failed', payload, to=room)

    def broadcast_queue_update(self, queued_count: int, processing_count: int):
        """Broadcast queue status update to all clients"""
        payload = {
            'queued': queued_count,
            'processing': processing_count,
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.debug(f'Broadcasting queue update: {payload}')
        self.socketio.emit('queue_updated', payload, broadcast=True)

    def run(self, host: str = '0.0.0.0', port: int = 8085, debug: bool = False):
        """Run the WebSocket server"""
        logger.info(f'Starting WebSocket server on {host}:{port}')
        self.socketio.run(self.app, host=host, port=port, debug=debug)


# Global instance for easy access
_ws_server = None


def get_ws_server() -> WebSocketServer:
    """Get the WebSocket server instance"""
    global _ws_server
    if _ws_server is None:
        _ws_server = WebSocketServer()
    return _ws_server


def init_websocket(app: Flask):
    """Initialize WebSocket server with Flask app"""
    global _ws_server
    _ws_server = WebSocketServer(app)
    return _ws_server


if __name__ == '__main__':
    # Run standalone WebSocket server
    server = WebSocketServer()
    server.run(debug=True)
