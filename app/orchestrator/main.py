"""
Orchestrator service for job management, scene planning, and pipeline coordination.
"""

import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import threading

try:
    import requests
except ImportError:
    requests = None

from app.common.models import (
    VideoRequest,
    Scene,
    Storyboard,
    JobStatus,
    JobProgress,
    AudioSegment,
    Subtitle,
)
from app.common.config import Config
from app.common.utils import setup_logging, log_job_event, job_cache


logger = setup_logging("Orchestrator")


class ScenePlanner:
    """Plans video scenes from text prompts using NLP-inspired heuristics."""

    def __init__(self):
        self.logger = setup_logging("ScenePlanner")

    def plan_scenes(
        self, prompt: str, target_duration: int, scene_count: Optional[int] = None
    ) -> List[Scene]:
        """
        Break prompt into scenes.
        Uses simple heuristics: split by punctuation, estimate duration, generate keywords.
        """
        # Split prompt into sentences
        sentences = re.split(r'[.!?]+', prompt)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            sentences = [prompt]

        # Calculate default scene count
        if scene_count is None:
            scene_count = max(2, min(len(sentences), (target_duration // 5)))

        # Distribute sentences across scenes
        scenes_per_sentence = max(1, len(sentences) // scene_count)
        scene_duration = target_duration / scene_count if scene_count > 0 else target_duration

        scenes: List[Scene] = []
        for i in range(scene_count):
            # Combine sentences for this scene
            start_idx = i * scenes_per_sentence
            end_idx = start_idx + scenes_per_sentence if i < scene_count - 1 else len(sentences)
            scene_text = " ".join(sentences[start_idx:end_idx])

            # Extract keywords using simple heuristics
            keywords = self._extract_keywords(scene_text)
            shot_type = self._determine_shot_type(scene_text)

            scene = Scene(
                description=scene_text,
                duration=scene_duration,
                keywords=keywords,
                shot_type=shot_type,
                start_time=i * scene_duration,
                end_time=(i + 1) * scene_duration,
            )
            scenes.append(scene)
            self.logger.debug(f"Planned scene {i+1}: {scene.description[:50]}...")

        return scenes

    def _extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """Extract keywords from text using simple heuristics."""
        # Remove common words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "is", "are", "was", "were", "be", "been", "do", "did"
        }

        words = text.lower().split()
        keywords = [
            w.strip(',.!?;:') for w in words
            if len(w) > 3 and w.lower() not in stop_words
        ]
        # Return unique keywords, up to max
        return list(set(keywords))[:max_keywords]

    def _determine_shot_type(self, text: str) -> str:
        """Determine shot type based on text cues."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["close", "detail", "face", "hand"]):
            return "close-up"
        elif any(word in text_lower for word in ["aerial", "sky", "bird", "drone", "above"]):
            return "aerial"
        elif any(word in text_lower for word in ["slow", "smooth", "graceful"]):
            return "slow-motion"
        elif any(word in text_lower for word in ["quick", "fast", "rapid"]):
            return "fast-motion"
        else:
            return "general"


class JobOrchestrator:
    """Orchestrates the entire video generation pipeline."""

    def __init__(self):
        self.logger = setup_logging("JobOrchestrator")
        self.scene_planner = ScenePlanner()
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def orchestrate_job(self, job_request: VideoRequest, job_progress: JobProgress):
        """Main orchestration loop for a job."""
        job_id = job_request.id
        
        try:
            log_job_event(job_id, "orchestration_started", "SCENE_PLANNING")
            
            # Step 1: Scene Planning
            self._plan_scenes(job_id, job_request, job_progress)

            # Step 2: Asset Retrieval
            self._retrieve_assets(job_id, job_request, job_progress)

            # Step 3: TTS and Audio Generation
            self._generate_audio(job_id, job_request, job_progress)

            # Step 4: Rendering
            self._render_video(job_id, job_request, job_progress)

            # Mark as completed
            job_progress.status = JobStatus.COMPLETED
            job_progress.overall_progress = 100.0
            log_job_event(job_id, "orchestration_completed", "COMPLETED")
            self.logger.info(f"Job {job_id} completed successfully")

        except Exception as e:
            self.logger.error(f"Error orchestrating job {job_id}: {str(e)}", exc_info=True)
            job_progress.status = JobStatus.FAILED
            job_progress.error = str(e)
            log_job_event(job_id, "orchestration_failed", "FAILED", {"error": str(e)})

    def _plan_scenes(self, job_id: str, job_request: VideoRequest, job_progress: JobProgress):
        """Plan scenes for the job."""
        job_progress.status = JobStatus.SCENE_PLANNING
        job_progress.current_step = "Planning video scenes..."
        
        try:
            scenes = self.scene_planner.plan_scenes(
                job_request.prompt,
                job_request.duration_target,
                job_request.scene_count,
            )
            
            job_progress.total_scenes = len(scenes)
            
            # Create storyboard
            storyboard = Storyboard(
                job_id=job_id,
                prompt=job_request.prompt,
                scenes=scenes,
                total_duration=job_request.duration_target,
            )
            
            # Cache storyboard
            job_cache.set(f"storyboard_{job_id}", storyboard.to_dict())
            
            job_progress.overall_progress = 20.0
            self.logger.info(f"Scene planning completed for job {job_id}: {len(scenes)} scenes")
            log_job_event(job_id, "scenes_planned", "COMPLETE", {"scene_count": len(scenes)})

        except Exception as e:
            self.logger.error(f"Error planning scenes for {job_id}: {str(e)}", exc_info=True)
            raise

    def _retrieve_assets(self, job_id: str, job_request: VideoRequest, job_progress: JobProgress):
        """Retrieve video assets."""
        job_progress.status = JobStatus.ASSET_RETRIEVAL
        job_progress.current_step = "Retrieving stock footage..."
        
        try:
            # Get storyboard
            storyboard_data = job_cache.get(f"storyboard_{job_id}")
            if not storyboard_data:
                raise ValueError("Storyboard not found")

            # Simulate asset retrieval
            time.sleep(0.5)
            
            job_progress.overall_progress = 40.0
            self.logger.info(f"Asset retrieval completed for job {job_id}")
            log_job_event(job_id, "assets_retrieved", "COMPLETE")

        except Exception as e:
            self.logger.error(f"Error retrieving assets for {job_id}: {str(e)}", exc_info=True)
            raise

    def _generate_audio(self, job_id: str, job_request: VideoRequest, job_progress: JobProgress):
        """Generate audio and subtitles."""
        job_progress.status = JobStatus.AUDIO_PROCESSING
        job_progress.current_step = "Generating audio and subtitles..."
        
        try:
            # Simulate audio generation
            time.sleep(0.5)
            
            # Create sample audio segments and subtitles
            audio_segments = [
                AudioSegment(
                    text="Beginning of narration",
                    duration=5.0,
                    start_time=0.0,
                    language=job_request.language,
                )
            ]
            
            subtitles = [
                Subtitle(
                    text="Beginning of narration",
                    start_time=0,
                    end_time=5000,
                )
            ]
            
            # Update storyboard
            storyboard_data = job_cache.get(f"storyboard_{job_id}")
            if storyboard_data:
                storyboard_data["audio_segments"] = [a.to_dict() for a in audio_segments]
                storyboard_data["subtitles"] = [s.to_dict() for s in subtitles]
                job_cache.set(f"storyboard_{job_id}", storyboard_data)
            
            job_progress.overall_progress = 60.0
            self.logger.info(f"Audio generation completed for job {job_id}")
            log_job_event(job_id, "audio_generated", "COMPLETE")

        except Exception as e:
            self.logger.error(f"Error generating audio for {job_id}: {str(e)}", exc_info=True)
            raise

    def _render_video(self, job_id: str, job_request: VideoRequest, job_progress: JobProgress):
        """Render final video."""
        job_progress.status = JobStatus.RENDERING
        job_progress.current_step = "Rendering video..."
        
        try:
            # Simulate rendering
            time.sleep(1.0)
            
            # Create result
            result = {
                "job_id": job_id,
                "video_url": f"s3://videos/{job_id}/output.mp4",
                "thumbnail_url": f"s3://videos/{job_id}/thumbnail.jpg",
                "format": "mp4",
                "duration": job_request.duration_target,
            }
            
            job_cache.set(f"result_{job_id}", result)
            
            # Trigger webhook if provided
            if job_request.callback_url:
                self._trigger_webhook(job_request.callback_url, result)
            
            job_progress.overall_progress = 100.0
            self.logger.info(f"Video rendering completed for job {job_id}")
            log_job_event(job_id, "video_rendered", "COMPLETE")

        except Exception as e:
            self.logger.error(f"Error rendering video for {job_id}: {str(e)}", exc_info=True)
            raise

    def _trigger_webhook(self, callback_url: str, result: Dict[str, Any]):
        """Trigger callback webhook with result."""
        if not Config.ENABLE_WEBHOOKS:
            return
        
        try:
            if requests is None:
                self.logger.warning("requests library not available for webhooks")
                return
            
            response = requests.post(
                callback_url,
                json=result,
                timeout=Config.WEBHOOK_TIMEOUT,
            )
            response.raise_for_status()
            self.logger.info(f"Webhook triggered: {callback_url}")

        except Exception as e:
            self.logger.error(f"Error triggering webhook {callback_url}: {str(e)}")


# Global orchestrator instance
_orchestrator = JobOrchestrator()


def get_orchestrator() -> JobOrchestrator:
    """Get global orchestrator instance."""
    return _orchestrator


if __name__ == "__main__":
    logger.info("Orchestrator service ready")
