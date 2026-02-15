"""
Common data models for the video generation service.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict, field
import json
import uuid


class JobStatus(str, Enum):
    """Job execution status."""
    PENDING = "pending"
    SCENE_PLANNING = "scene_planning"
    ASSET_RETRIEVAL = "asset_retrieval"
    TTS_GENERATION = "tts_generation"
    AUDIO_PROCESSING = "audio_processing"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Scene:
    """Represents a single scene in the video."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    duration: float = 5.0  # seconds
    keywords: List[str] = field(default_factory=list)
    shot_type: str = "general"  # close-up, aerial, slow-motion, etc.
    narration: str = ""
    clip_id: Optional[str] = None
    clip_url: Optional[str] = None
    start_time: float = 0.0
    end_time: float = 5.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VideoRequest:
    """Incoming video generation request."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str = ""
    duration_target: int = 60  # seconds
    style: str = "cinematic"  # cinematic, social, broadcast
    voice: str = "en-US-neutral"
    language: str = "en"
    scene_count: Optional[int] = None
    callback_url: Optional[str] = None
    priority: int = 5  # 1-10, higher is more important
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


@dataclass
class JobProgress:
    """Current job progress tracking."""
    job_id: str
    status: JobStatus = JobStatus.PENDING
    overall_progress: float = 0.0  # 0-100
    current_step: str = ""
    logs: List[str] = field(default_factory=list)
    estimated_time_remaining: float = 0.0  # seconds
    scenes_processed: int = 0
    total_scenes: int = 0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        return data


@dataclass
class VideoResult:
    """Final video generation result."""
    job_id: str
    video_url: str
    thumbnail_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    duration: float = 0.0
    format: str = "mp4"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['generated_at'] = self.generated_at.isoformat()
        return data


@dataclass
class PexelsClip:
    """Represents a stock clip from Pexels."""
    id: str
    url: str
    video_url: str
    duration: float
    width: int
    height: int
    user_name: str
    user_url: str
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AudioSegment:
    """Represents an audio segment with timing information."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    audio_url: Optional[str] = None
    duration: float = 0.0
    start_time: float = 0.0
    language: str = "en"
    speaker: str = "narrator"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Subtitle:
    """Represents a subtitle entry."""
    text: str
    start_time: float  # milliseconds
    end_time: float    # milliseconds
    speaker: str = "narrator"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Storyboard:
    """Complete storyboard for a video project."""
    job_id: str
    prompt: str
    scenes: List[Scene] = field(default_factory=list)
    total_duration: float = 0.0
    audio_segments: List[AudioSegment] = field(default_factory=list)
    subtitles: List[Subtitle] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['scenes'] = [s.to_dict() for s in self.scenes]
        data['audio_segments'] = [a.to_dict() for a in self.audio_segments]
        data['subtitles'] = [s.to_dict() for s in self.subtitles]
        return data
