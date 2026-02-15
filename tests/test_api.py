"""
Basic tests for the video generation service.
Run with: pytest tests/test_api.py -v
"""

import pytest
import json
from app.common.models import (
    VideoRequest, Scene, Storyboard, JobStatus, JobProgress
)
from app.orchestrator.main import ScenePlanner
from app.retriever.main import PexelsRetriever


class TestModels:
    """Test data models."""

    def test_video_request_creation(self):
        """Test VideoRequest model creation."""
        req = VideoRequest(
            prompt="Test prompt",
            duration_target=60,
            style="cinematic"
        )
        assert req.prompt == "Test prompt"
        assert req.duration_target == 60
        assert req.style == "cinematic"
        assert req.id is not None

    def test_scene_creation(self):
        """Test Scene model creation."""
        scene = Scene(
            description="Test scene",
            duration=5.0,
            keywords=["test", "scene"],
            shot_type="general"
        )
        assert scene.description == "Test scene"
        assert scene.duration == 5.0
        assert len(scene.keywords) == 2

    def test_job_status_enum(self):
        """Test JobStatus enum."""
        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"

    def test_storyboard_creation(self):
        """Test Storyboard model creation."""
        scenes = [
            Scene(description="Scene 1", duration=5),
            Scene(description="Scene 2", duration=5),
        ]
        storyboard = Storyboard(
            job_id="test_job",
            prompt="Test prompt",
            scenes=scenes,
            total_duration=10
        )
        assert len(storyboard.scenes) == 2
        assert storyboard.total_duration == 10


class TestScenePlanner:
    """Test scene planning functionality."""

    def test_scene_planner_initialization(self):
        """Test ScenePlanner initialization."""
        planner = ScenePlanner()
        assert planner is not None

    def test_scene_planning_basic(self):
        """Test basic scene planning."""
        planner = ScenePlanner()
        prompt = "First scene. Second scene. Third scene."
        scenes = planner.plan_scenes(prompt, target_duration=60, scene_count=3)
        
        assert len(scenes) == 3
        assert all(isinstance(s, Scene) for s in scenes)
        assert all(s.duration > 0 for s in scenes)

    def test_scene_planning_keyword_extraction(self):
        """Test keyword extraction from prompt."""
        planner = ScenePlanner()
        text = "Beautiful sunset over the ocean with waves crashing"
        keywords = planner._extract_keywords(text)
        
        assert len(keywords) > 0
        assert any(kw in keywords for kw in ["sunset", "ocean", "waves"])

    def test_scene_planning_shot_type(self):
        """Test shot type determination."""
        planner = ScenePlanner()
        
        # Test close-up detection
        shot = planner._determine_shot_type("Close-up of a face")
        assert shot == "close-up"
        
        # Test aerial detection
        shot = planner._determine_shot_type("Aerial view from a drone")
        assert shot == "aerial"
        
        # Test default
        shot = planner._determine_shot_type("Generic scene")
        assert shot == "general"

    def test_scene_duration_distribution(self):
        """Test that scenes are distributed evenly."""
        planner = ScenePlanner()
        prompt = "Scene one. Scene two. Scene three. Scene four."
        target_duration = 120
        
        scenes = planner.plan_scenes(prompt, target_duration=target_duration, scene_count=4)
        
        # Each scene should be ~30 seconds
        total = sum(s.duration for s in scenes)
        assert abs(total - target_duration) < 0.1  # Allow small rounding error
        
        # Scenes should be evenly distributed
        durations = [s.duration for s in scenes]
        assert all(abs(d - durations[0]) < 0.1 for d in durations)


class TestPexelsRetriever:
    """Test Pexels retriever functionality."""

    def test_pexels_retriever_initialization(self):
        """Test PexelsRetriever initialization."""
        retriever = PexelsRetriever()
        assert retriever is not None
        # Should warn if no API key
        if not retriever.api_key:
            assert retriever.api_key == ""

    def test_keyword_extraction_from_query(self):
        """Test that retriever can extract meaningful keywords."""
        retriever = PexelsRetriever()
        
        # Note: Actual search would require Pexels API key
        # This tests the structure, not actual API calls


class TestJobProgress:
    """Test job progress tracking."""

    def test_job_progress_initialization(self):
        """Test JobProgress initialization."""
        progress = JobProgress(
            job_id="test_job",
            status=JobStatus.PENDING
        )
        assert progress.job_id == "test_job"
        assert progress.status == JobStatus.PENDING
        assert progress.overall_progress == 0.0

    def test_job_progress_status_transitions(self):
        """Test valid status transitions."""
        progress = JobProgress(job_id="test_job")
        
        # Valid transitions
        progress.status = JobStatus.SCENE_PLANNING
        assert progress.status == JobStatus.SCENE_PLANNING
        
        progress.status = JobStatus.COMPLETED
        assert progress.status == JobStatus.COMPLETED

    def test_job_progress_to_dict(self):
        """Test conversion to dictionary."""
        progress = JobProgress(
            job_id="test_job",
            status=JobStatus.RENDERING,
            overall_progress=50.0
        )
        data = progress.to_dict()
        
        assert data["job_id"] == "test_job"
        assert data["status"] == "rendering"
        assert data["overall_progress"] == 50.0


class TestIntegration:
    """Integration tests."""

    def test_end_to_end_scene_planning(self):
        """Test end-to-end scene planning."""
        planner = ScenePlanner()
        prompt = """
        A beautiful sunrise over the mountains. 
        The camera pans across the valley below.
        Birds start to sing as the light grows.
        A family emerges from a cabin, ready for their adventure.
        """
        
        scenes = planner.plan_scenes(prompt, target_duration=60, scene_count=4)
        
        assert len(scenes) > 0
        assert all(s.keywords for s in scenes)
        assert all(s.shot_type for s in scenes)
        
        # Verify total duration
        total = sum(s.duration for s in scenes)
        assert abs(total - 60) < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
