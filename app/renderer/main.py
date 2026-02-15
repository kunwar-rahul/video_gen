"""
Renderer service for composing videos using FFmpeg.
Handles timeline assembly, transitions, captions, and final video export.
"""

import os
import subprocess
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.common.models import Storyboard, Scene, Subtitle
from app.common.config import Config
from app.common.utils import setup_logging, log_job_event, job_cache


logger = setup_logging("Renderer")


class FFmpegRenderer:
    """Video composition and rendering using FFmpeg."""

    def __init__(self):
        self.logger = setup_logging("FFmpegRenderer")
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """Check if FFmpeg is available."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                timeout=5,
            )
            if result.returncode == 0:
                self.logger.info("FFmpeg is available")
            else:
                self.logger.warning("FFmpeg check failed")
        except FileNotFoundError:
            self.logger.error("FFmpeg not found. Install with: apt-get install ffmpeg")

    def render_video(
        self,
        job_id: str,
        storyboard: Dict[str, Any],
        output_path: str,
        quality: str = "medium",
    ) -> bool:
        """
        Render final video from storyboard.
        MVP uses a simple concat approach; can be enhanced with transitions and effects.
        """
        try:
            self.logger.info(f"Starting video render for job {job_id}")

            # Create concat file
            concat_file = f"/tmp/{job_id}_concat.txt"
            filter_file = f"/tmp/{job_id}_filter.txt"
            
            self._create_concat_file(storyboard, concat_file)
            self._create_filter_file(storyboard, filter_file)

            # Build FFmpeg command
            command = self._build_ffmpeg_command(
                concat_file,
                output_path,
                quality,
            )

            self.logger.debug(f"FFmpeg command: {' '.join(command)}")

            # Run FFmpeg
            result = subprocess.run(
                command,
                capture_output=True,
                timeout=Config.JOB_TIMEOUT,
            )

            if result.returncode == 0:
                output_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                self.logger.info(
                    f"Video rendered successfully: {output_path} ({output_size:.2f} MB)"
                )
                return True
            else:
                error_msg = result.stderr.decode() if result.stderr else "Unknown error"
                self.logger.error(f"FFmpeg error: {error_msg}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"FFmpeg timeout after {Config.JOB_TIMEOUT} seconds")
            return False
        except Exception as e:
            self.logger.error(f"Error rendering video: {str(e)}", exc_info=True)
            return False

    def _create_concat_file(self, storyboard: Dict[str, Any], output_file: str):
        """Create FFmpeg concat file from scenes."""
        try:
            with open(output_file, 'w') as f:
                for scene in storyboard.get("scenes", []):
                    # In MVP, use placeholder or generate frame
                    clip_url = scene.get("clip_url", "")
                    if clip_url:
                        f.write(f"file '{clip_url}'\n")
                        f.write(f"duration {scene.get('duration', 5)}\n")
                    else:
                        # Create placeholder frame
                        self.logger.debug(f"No clip for scene {scene.get('id')}, creating placeholder")
                        # In production, would generate frame or use default
                        f.write(f"file 'color=c=black:s=1920x1080:d={scene.get('duration', 5)}'\n")

            self.logger.debug(f"Concat file created: {output_file}")

        except Exception as e:
            self.logger.error(f"Error creating concat file: {str(e)}", exc_info=True)

    def _create_filter_file(self, storyboard: Dict[str, Any], output_file: str):
        """Create FFmpeg filter file for transitions and effects."""
        try:
            filters = []
            
            # Add caption filter if subtitles exist
            subtitles = storyboard.get("subtitles", [])
            if subtitles:
                # Simple subtitle overlay using drawtext
                filters.append("drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:fontsize=24")

            # Add transitions between scenes
            scene_count = len(storyboard.get("scenes", []))
            if scene_count > 1:
                filters.append("fade=t=in:st=0:d=0.5,fade=t=out:st=-0.5:d=0.5")

            # Apply quality-based filtering
            quality = storyboard.get("quality", "medium")
            if quality == "high":
                filters.append("scale=1920:1080,hqdn3d=1.5:1.5:6:6")
            elif quality == "low":
                filters.append("scale=1280:720")

            # Write filter file
            with open(output_file, 'w') as f:
                if filters:
                    f.write(",".join(filters))
                else:
                    f.write("[0]scale=1920:1080[out]")

            self.logger.debug(f"Filter file created: {output_file}")

        except Exception as e:
            self.logger.error(f"Error creating filter file: {str(e)}", exc_info=True)

    def _build_ffmpeg_command(
        self,
        concat_file: str,
        output_path: str,
        quality: str,
    ) -> List[str]:
        """Build FFmpeg command with appropriate parameters."""
        preset = Config.FFMPEG_PRESET
        if quality == "high":
            preset = "slow"
        elif quality == "low":
            preset = "ultrafast"

        # Get target resolution
        resolution = Config.TARGET_RESOLUTION
        width, height = map(int, resolution.split('x'))

        command = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c:v", Config.VIDEO_CODEC,
            "-preset", preset,
            "-b:v", Config.VIDEO_BITRATE,
            "-vf", f"scale={width}:{height},fps={Config.TARGET_FPS}",
            "-c:a", Config.AUDIO_CODEC,
            "-b:a", Config.AUDIO_BITRATE,
            "-y",  # Overwrite output file
            output_path,
        ]

        return command

    def add_subtitles(
        self,
        video_file: str,
        subtitle_file: str,
        output_file: str,
    ) -> bool:
        """Add burnt-in subtitles to video."""
        try:
            self.logger.info(f"Adding subtitles to {video_file}")

            command = [
                "ffmpeg",
                "-i", video_file,
                "-vf", f"subtitles={subtitle_file}",
                "-c:a", "copy",
                "-y",
                output_file,
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                timeout=Config.JOB_TIMEOUT,
            )

            if result.returncode == 0:
                self.logger.info("Subtitles added successfully")
                return True
            else:
                error_msg = result.stderr.decode() if result.stderr else "Unknown error"
                self.logger.error(f"Error adding subtitles: {error_msg}")
                return False

        except Exception as e:
            self.logger.error(f"Error adding subtitles: {str(e)}", exc_info=True)
            return False

    def extract_thumbnail(
        self,
        video_file: str,
        output_file: str,
        timestamp: float = 0.0,
        size: str = "320x180",
    ) -> bool:
        """Extract thumbnail from video at timestamp."""
        try:
            self.logger.info(f"Extracting thumbnail from {video_file} at {timestamp}s")

            command = [
                "ffmpeg",
                "-ss", str(timestamp),
                "-i", video_file,
                "-vframes", "1",
                "-vf", f"scale={size}",
                "-y",
                output_file,
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                timeout=30,
            )

            if result.returncode == 0:
                self.logger.info(f"Thumbnail extracted: {output_file}")
                return True
            else:
                error_msg = result.stderr.decode() if result.stderr else "Unknown error"
                self.logger.error(f"Error extracting thumbnail: {error_msg}")
                return False

        except Exception as e:
            self.logger.error(f"Error extracting thumbnail: {str(e)}", exc_info=True)
            return False


class RendererService:
    """Service coordinator for video rendering."""

    def __init__(self):
        self.logger = setup_logging("RendererService")
        self.renderer = FFmpegRenderer()

    def render_job(
        self,
        job_id: str,
        output_path: str,
        quality: str = "medium",
    ) -> Dict[str, Any]:
        """
        Render complete video for a job.
        """
        self.logger.info(f"Rendering job {job_id}")

        try:
            # Get storyboard from cache
            storyboard_data = job_cache.get(f"storyboard_{job_id}")
            if not storyboard_data:
                raise ValueError("Storyboard not found in cache")

            # Render video
            success = self.renderer.render_video(
                job_id,
                storyboard_data,
                output_path,
                quality,
            )

            if not success:
                raise Exception("FFmpeg rendering failed")

            # Extract thumbnail
            thumbnail_path = output_path.replace(".mp4", "_thumb.jpg")
            self.renderer.extract_thumbnail(output_path, thumbnail_path, timestamp=1.0)

            result = {
                "job_id": job_id,
                "video_path": output_path,
                "thumbnail_path": thumbnail_path,
                "success": True,
                "error": None,
            }

            log_job_event(job_id, "video_rendered", "COMPLETE")
            return result

        except Exception as e:
            self.logger.error(f"Error rendering job: {str(e)}", exc_info=True)
            log_job_event(job_id, "rendering_failed", "FAILED", {"error": str(e)})
            return {
                "job_id": job_id,
                "video_path": None,
                "thumbnail_path": None,
                "success": False,
                "error": str(e),
            }


# Global service instance
_renderer_service = RendererService()


def get_renderer_service() -> RendererService:
    """Get global renderer service instance."""
    return _renderer_service


if __name__ == "__main__":
    logger.info("Renderer service ready")
