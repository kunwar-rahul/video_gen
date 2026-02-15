"""
Job listing, filtering, and pagination utilities.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app.common.models import JobStatus

def parse_date_range(date_range: str) -> tuple[datetime, datetime]:
    """Parse date range string and return start and end dates."""
    now = datetime.utcnow()
    
    if date_range == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif date_range == "week":
        start = now - timedelta(days=7)
        end = now
    elif date_range == "month":
        start = now - timedelta(days=30)
        end = now
    else:  # "all"
        start = datetime.min
        end = now
    
    return start, end


def matches_filters(job_data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
    """Check if a job matches the specified filters."""
    # Status filter
    if "status" in filters and job_data.get("status") != filters["status"]:
        return False
    
    # Priority filter
    if "priority" in filters and job_data.get("priority") != filters["priority"]:
        return False
    
    # Date range filter
    if "date_range" in filters:
        start, end = filters["date_range"]
        created_at = job_data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        if created_at and (created_at < start or created_at > end):
            return False
    
    return True


def sort_jobs(jobs: List[Dict[str, Any]], sort_by: str, sort_order: str) -> List[Dict[str, Any]]:
    """Sort jobs by specified column and order."""
    reverse = sort_order == "desc"
    
    if sort_by == "created_at":
        return sorted(jobs, key=lambda j: j.get("created_at", ""), reverse=reverse)
    elif sort_by == "updated_at":
        return sorted(jobs, key=lambda j: j.get("updated_at", ""), reverse=reverse)
    elif sort_by == "progress":
        return sorted(jobs, key=lambda j: j.get("overall_progress", 0), reverse=reverse)
    elif sort_by == "duration_target":
        return sorted(jobs, key=lambda j: j.get("duration_target", 0), reverse=reverse)
    elif sort_by == "priority":
        return sorted(jobs, key=lambda j: j.get("priority", 0), reverse=reverse)
    
    return jobs


def get_job_summary(all_jobs: Dict[str, Any]) -> Dict[str, int]:
    """Calculate summary statistics for jobs."""
    summary = {
        "total_jobs": 0,
        "completed": 0,
        "failed": 0,
        "cancelled": 0,
        "in_progress": 0,
        "pending": 0,
    }
    
    for job_data in all_jobs.values():
        status = job_data.get("status", "pending")
        summary["total_jobs"] += 1
        
        if status == "completed":
            summary["completed"] += 1
        elif status == "failed":
            summary["failed"] += 1
        elif status == "cancelled":
            summary["cancelled"] += 1
        elif status in ["scene_planning", "asset_retrieval", "tts_generation", "audio_processing", "rendering"]:
            summary["in_progress"] += 1
        else:  # pending
            summary["pending"] += 1
    
    return summary


def build_job_dict(job_id: str, job_request: Any, job_progress: Any) -> Dict[str, Any]:
    """Build job dictionary for API response."""
    return {
        "job_id": job_id,
        "prompt": job_request.prompt[:100] if job_request else "",
        "status": job_progress.status.value if job_progress else "pending",
        "overall_progress": job_progress.overall_progress if job_progress else 0.0,
        "duration_target": job_request.duration_target if job_request else 0,
        "style": job_request.style if job_request else "",
        "voice": job_request.voice if job_request else "",
        "language": job_request.language if job_request else "",
        "priority": job_request.priority if job_request else 5,
        "created_at": job_request.created_at.isoformat() if job_request else "",
        "updated_at": job_progress.updated_at if hasattr(job_progress, 'updated_at') else job_request.updated_at.isoformat() if job_request else "",
        "estimated_time_remaining": job_progress.estimated_time_remaining if job_progress else 0.0,
    }
