"""
Asset retriever service for fetching video clips from Pexels.
"""

import json
from typing import List, Dict, Any, Optional

try:
    import requests
except ImportError:
    requests = None

from app.common.models import PexelsClip, Scene
from app.common.config import Config
from app.common.utils import setup_logging, log_job_event, job_cache


logger = setup_logging("Retriever")


class PexelsRetriever:
    """Fetches video clips and images from Pexels API."""

    def __init__(self):
        self.logger = setup_logging("PexelsRetriever")
        self.api_key = Config.PEXELS_API_KEY
        self.base_url = Config.PEXELS_BASE_URL
        
        if not self.api_key:
            self.logger.warning("PEXELS_API_KEY not configured. Pexels integration disabled.")

    def search_clips(self, query: str, per_page: int = 5) -> List[PexelsClip]:
        """
        Search for video clips matching query.
        """
        if not self.api_key or requests is None:
            self.logger.warning(f"Cannot search clips without API key or requests library")
            return []

        try:
            headers = {
                "Authorization": self.api_key,
            }
            params = {
                "query": query,
                "per_page": per_page,
                "min_duration": Config.PEXELS_MIN_DURATION,
            }

            response = requests.get(
                self.base_url,
                headers=headers,
                params=params,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            clips = []

            for video_data in data.get("videos", []):
                # Extract video URL (prefer mp4 format)
                video_url = None
                for video_file in video_data.get("video_files", []):
                    if video_file.get("file_type") == "video/mp4":
                        video_url = video_file.get("link")
                        break

                if video_url:
                    clip = PexelsClip(
                        id=str(video_data.get("id")),
                        url=video_data.get("url", ""),
                        video_url=video_url,
                        duration=video_data.get("duration", 0),
                        width=video_data.get("width", 1920),
                        height=video_data.get("height", 1080),
                        user_name=video_data.get("user", {}).get("name", "Unknown"),
                        user_url=video_data.get("user", {}).get("url", ""),
                        description=query,
                    )
                    clips.append(clip)
                    self.logger.debug(f"Found clip: {clip.id} - {clip.duration}s")

            self.logger.info(f"Search query '{query}' returned {len(clips)} clips")
            return clips

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error searching Pexels: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error in search_clips: {str(e)}", exc_info=True)
            return []

    def get_best_clip(self, scenes: List[Scene]) -> Dict[str, Any]:
        """
        Select best clip for each scene.
        In MVP, use simple heuristics; can be enhanced with ML scoring.
        """
        results = {}

        for scene in scenes:
            if not scene.keywords:
                query = scene.description[:50]
            else:
                query = " ".join(scene.keywords[:3])

            clips = self.search_clips(query, per_page=Config.PEXELS_MAX_RESULTS_PER_QUERY)

            if clips:
                # Select clip with duration closest to scene duration
                best_clip = min(
                    clips,
                    key=lambda c: abs(c.duration - scene.duration)
                )
                results[scene.id] = {
                    "clip": best_clip,
                    "query": query,
                    "match_score": 1.0 - (abs(best_clip.duration - scene.duration) / 10),
                }
                self.logger.debug(
                    f"Selected clip {best_clip.id} for scene {scene.id}: "
                    f"{best_clip.duration}s (target: {scene.duration}s)"
                )
            else:
                self.logger.warning(f"No clips found for scene {scene.id}: {query}")
                results[scene.id] = {
                    "clip": None,
                    "query": query,
                    "match_score": 0.0,
                }

        return results

    def download_clip(self, clip_url: str, destination: str) -> bool:
        """
        Download clip to local storage or object store.
        In MVP, just log the intent; implement actual download in next phase.
        """
        try:
            self.logger.info(f"Downloading clip from {clip_url} to {destination}")
            # Actual download would use requests or similar
            return True
        except Exception as e:
            self.logger.error(f"Error downloading clip: {str(e)}")
            return False


class RetrieverService:
    """Service interface for asset retrieval."""

    def __init__(self):
        self.logger = setup_logging("RetrieverService")
        self.pexels = PexelsRetriever()

    def retrieve_assets_for_scenes(self, job_id: str, scenes: List[Scene]) -> Dict[str, Any]:
        """Retrieve assets for all scenes in a job."""
        self.logger.info(f"Retrieving assets for {len(scenes)} scenes in job {job_id}")

        try:
            assets = self.pexels.get_best_clip(scenes)
            
            # Cache assets
            job_cache.set(f"assets_{job_id}", assets)
            log_job_event(job_id, "assets_retrieved", "COMPLETE", {"asset_count": len(assets)})
            
            return assets

        except Exception as e:
            self.logger.error(f"Error retrieving assets: {str(e)}", exc_info=True)
            log_job_event(job_id, "asset_retrieval_failed", "FAILED", {"error": str(e)})
            raise


# Global retriever service instance
_retriever_service = RetrieverService()


def get_retriever_service() -> RetrieverService:
    """Get global retriever service instance."""
    return _retriever_service


if __name__ == "__main__":
    logger.info("Retriever service ready")
    
    # Test search
    retriever = PexelsRetriever()
    clips = retriever.search_clips("sunset over water", per_page=3)
    for clip in clips:
        print(f"  - {clip.id}: {clip.duration}s @ {clip.width}x{clip.height}")
