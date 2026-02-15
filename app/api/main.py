"""
REST API and MCP Server for the video generation service.
Exposes endpoints for job submission, status tracking, and result retrieval.
"""

import json
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError:
    print("Flask is required. Install with: pip install flask")
    Flask = None

from app.common.models import (
    VideoRequest,
    JobStatus,
    JobProgress,
    VideoResult,
    Storyboard,
)
from app.common.config import Config
from app.common.utils import setup_logging, log_job_event, job_cache
from app.api.jobs_service import (
    parse_date_range,
    matches_filters,
    sort_jobs,
    get_job_summary,
    build_job_dict,
)

try:
    from app.websocket.events import WebSocketEventManager
except ImportError:
    WebSocketEventManager = None


logger = setup_logging("API")


class VideoGenerationAPI:
    """REST and MCP API server for video generation."""

    def __init__(self):
        if Flask is None:
            raise ImportError("Flask is required for API server")
        
        self.app = Flask(__name__)
        CORS(self.app, resources={r"/mcp/*": {"origins": "*"}}, supports_credentials=True)
        self.jobs: Dict[str, VideoRequest] = {}
        self.job_progress: Dict[str, JobProgress] = {}
        self._setup_routes()

    def _setup_routes(self):
        """Register API routes."""
        
        @self.app.route("/health", methods=["GET"])
        def health():
            """Health check endpoint."""
            return jsonify({"status": "healthy", "service": "api"}), 200

        @self.app.route("/mcp/generate", methods=["POST"])
        def generate():
            """Generate video from prompt."""
            try:
                data = request.get_json()
                
                # Validate required fields
                if not data.get("prompt"):
                    return jsonify({"error": "Missing required field: prompt"}), 400

                # Create video request
                job_request = VideoRequest(
                    id=str(uuid.uuid4()),
                    prompt=data.get("prompt", ""),
                    duration_target=data.get("duration_target", 60),
                    style=data.get("style", "cinematic"),
                    voice=data.get("voice", "en-US-neutral"),
                    language=data.get("language", "en"),
                    scene_count=data.get("scene_count"),
                    callback_url=data.get("callback_url"),
                    priority=data.get("priority", 5),
                )

                # Store job
                self.jobs[job_request.id] = job_request
                
                # Initialize progress
                self.job_progress[job_request.id] = JobProgress(
                    job_id=job_request.id,
                    status=JobStatus.PENDING,
                    total_scenes=job_request.scene_count or 0,
                )

                # Log job submission
                log_job_event(
                    job_request.id,
                    "job_submitted",
                    "PENDING",
                    {"prompt": data.get("prompt")[:100]},
                )

                # Broadcast job creation event
                if WebSocketEventManager:
                    WebSocketEventManager.broadcast_job_status(
                        job_request.id,
                        JobStatus.PENDING.value,
                        0,
                        "Job queued for processing"
                    )

                logger.info(f"Job created: {job_request.id}")
                return jsonify({
                    "job_id": job_request.id,
                    "status": "accepted",
                    "message": "Job queued for processing",
                }), 202

            except Exception as e:
                logger.error(f"Error in /generate: {str(e)}", exc_info=True)
                return jsonify({"error": str(e)}), 500
        @self.app.route("/mcp/jobs", methods=["GET"])
        def list_jobs():
            """List all jobs with filtering and pagination."""
            try:
                # Get query parameters
                status_filter = request.args.get("status")
                date_range = request.args.get("date_range", "all")
                priority = request.args.get("priority", type=int)
                limit = request.args.get("limit", 50, type=int)
                offset = request.args.get("offset", 0, type=int)
                sort_by = request.args.get("sort_by", "created_at")
                sort_order = request.args.get("sort_order", "desc")

                # Validate parameters
                if limit > 100:
                    limit = 100  # Cap at 100

                if offset < 0:
                    offset = 0

                # Build filters dict
                filters = {}
                if status_filter:
                    filters["status"] = status_filter
                if priority:
                    filters["priority"] = priority
                if date_range != "all":
                    filters["date_range"] = parse_date_range(date_range)

                # Filter and sort jobs
                filtered_jobs = []
                for job_id, job_req in self.jobs.items():
                    job_prog = self.job_progress.get(job_id)
                    if matches_filters({"status": job_prog.status.value if job_prog else "pending", "priority": job_req.priority}, filters):
                        filtered_jobs.append(build_job_dict(job_id, job_req, job_prog))

                # Sort jobs
                filtered_jobs = sort_jobs(filtered_jobs, sort_by, sort_order)

                # Calculate pagination
                total = len(filtered_jobs)
                pages = (total + limit - 1) // limit if limit > 0 else 1
                current_page = (offset // limit) + 1 if limit > 0 else 1

                # Get paginated results
                jobs_page = filtered_jobs[offset:offset + limit]

                # Get summary statistics
                summary = get_job_summary(self.jobs)

                return jsonify({
                    "jobs": jobs_page,
                    "pagination": {
                        "total": total,
                        "limit": limit,
                        "offset": offset,
                        "page": current_page,
                        "pages": pages,
                    },
                    "summary": summary,
                }), 200

            except Exception as e:
                logger.error(f"Error in /jobs: {str(e)}", exc_info=True)
                return jsonify({"error": str(e)}), 500
        @self.app.route("/mcp/status/<job_id>", methods=["GET"])
        def status(job_id: str):
            """Get job status and progress."""
            try:
                if job_id not in self.job_progress:
                    return jsonify({"error": "Job not found"}), 404

                progress = self.job_progress[job_id]
                return jsonify(progress.to_dict()), 200

            except Exception as e:
                logger.error(f"Error in /status: {str(e)}", exc_info=True)
                return jsonify({"error": str(e)}), 500

        @self.app.route("/mcp/result/<job_id>", methods=["GET"])
        def result(job_id: str):
            """Get job result."""
            try:
                if job_id not in self.jobs:
                    return jsonify({"error": "Job not found"}), 404

                # Check cache first
                cached_result = job_cache.get(f"result_{job_id}")
                if cached_result:
                    return jsonify(cached_result), 200

                progress = self.job_progress.get(job_id)
                if not progress or progress.status != JobStatus.COMPLETED:
                    return jsonify({
                        "error": "Job not completed",
                        "status": progress.status.value if progress else "unknown",
                    }), 202

                # Return cached or temporary result
                result_data = {
                    "job_id": job_id,
                    "status": "completed",
                    "video_url": f"s3://videos/{job_id}/output.mp4",
                    "thumbnail_url": f"s3://videos/{job_id}/thumbnail.jpg",
                }
                job_cache.set(f"result_{job_id}", result_data)
                return jsonify(result_data), 200

            except Exception as e:
                logger.error(f"Error in /result: {str(e)}", exc_info=True)
                return jsonify({"error": str(e)}), 500

        @self.app.route("/mcp/cancel/<job_id>", methods=["POST"])
        def cancel(job_id: str):
            """Cancel a job."""
            try:
                if job_id not in self.jobs:
                    return jsonify({"error": "Job not found"}), 404

                progress = self.job_progress[job_id]
                if progress.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                    return jsonify({
                        "error": f"Cannot cancel job with status: {progress.status.value}"
                    }), 400

                progress.status = JobStatus.CANCELLED
                log_job_event(job_id, "job_cancelled", "CANCELLED")
                
                return jsonify({
                    "job_id": job_id,
                    "status": "cancelled",
                }), 200

            except Exception as e:
                logger.error(f"Error in /cancel: {str(e)}", exc_info=True)
                return jsonify({"error": str(e)}), 500

        @self.app.route("/mcp/prefetch", methods=["POST"])
        def prefetch():
            """Pre-warm assets for a prompt."""
            try:
                data = request.get_json()
                if not data.get("prompt"):
                    return jsonify({"error": "Missing required field: prompt"}), 400

                # Create a prefetch job
                prefetch_request = VideoRequest(
                    id=f"prefetch_{uuid.uuid4()}",
                    prompt=data.get("prompt", ""),
                    priority=10,  # High priority
                )

                self.jobs[prefetch_request.id] = prefetch_request
                log_job_event(prefetch_request.id, "prefetch_initiated", "PENDING")
                
                return jsonify({
                    "prefetch_id": prefetch_request.id,
                    "status": "prefetch_queued",
                }), 202

            except Exception as e:
                logger.error(f"Error in /prefetch: {str(e)}", exc_info=True)
                return jsonify({"error": str(e)}), 500

        @self.app.route("/mcp/storyboard/<job_id>", methods=["GET"])
        def get_storyboard(job_id: str):
            """Get intermediate storyboard for a job."""
            try:
                if job_id not in self.jobs:
                    return jsonify({"error": "Job not found"}), 404

                # Check cache first
                storyboard_data = job_cache.get(f"storyboard_{job_id}")
                if storyboard_data:
                    return jsonify(storyboard_data), 200

                return jsonify({"error": "Storyboard not yet available"}), 202

            except Exception as e:
                logger.error(f"Error in /storyboard: {str(e)}", exc_info=True)
                return jsonify({"error": str(e)}), 500

        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({"error": "Endpoint not found"}), 404

        @self.app.errorhandler(500)
        def internal_error(error):
            logger.error(f"Internal server error: {str(error)}")
            return jsonify({"error": "Internal server error"}), 500

    def run(self, host: str = Config.API_HOST, port: int = Config.API_PORT):
        """Start the API server."""
        logger.info(f"Starting API server on {host}:{port}")
        self.app.run(host=host, port=port, debug=False, threaded=True)


def create_app():
    """Factory function to create API app."""
    api = VideoGenerationAPI()
    return api.app


if __name__ == "__main__":
    Config.validate()
    api = VideoGenerationAPI()
    api.run()
