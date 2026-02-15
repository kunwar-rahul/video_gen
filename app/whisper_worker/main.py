"""
Whisper worker service for audio transcription, language detection, and speech processing.
"""

from typing import Dict, List, Tuple, Optional
import json

try:
    import whisper
except ImportError:
    whisper = None

try:
    from pydub import AudioSegment as PydubAudioSegment
except ImportError:
    PydubAudioSegment = None

from app.common.models import AudioSegment, Subtitle
from app.common.config import Config
from app.common.utils import setup_logging, log_job_event, job_cache


logger = setup_logging("WhisperWorker")


class WhisperProcessor:
    """Audio processing using OpenAI Whisper model."""

    def __init__(self):
        self.logger = setup_logging("WhisperProcessor")
        self.model = None
        self.device = Config.WHISPER_DEVICE
        self._load_model()

    def _load_model(self):
        """Load Whisper model."""
        if whisper is None:
            self.logger.warning("Whisper library not installed. Install with: pip install openai-whisper")
            return

        try:
            model_name = Config.WHISPER_MODEL  # tiny, base, small, medium, large
            self.logger.info(f"Loading Whisper model: {model_name} on device: {self.device}")
            self.model = whisper.load_model(model_name, device=self.device)
            self.logger.info("Whisper model loaded successfully")

        except Exception as e:
            self.logger.error(f"Error loading Whisper model: {str(e)}")
            self.model = None

    def transcribe_audio(self, audio_file: str, language: Optional[str] = None) -> Dict:
        """
        Transcribe audio file using Whisper.
        """
        if self.model is None:
            self.logger.warning("Whisper model not available")
            return {
                "text": "",
                "language": language or Config.TTS_LANGUAGE,
                "segments": [],
                "error": "Model not loaded",
            }

        try:
            self.logger.info(f"Transcribing audio: {audio_file}")
            
            # Transcribe
            result = self.model.transcribe(
                audio_file,
                language=language,
                verbose=False,
            )

            segments = []
            for segment in result.get("segments", []):
                segments.append({
                    "id": segment.get("id"),
                    "start": segment.get("start"),
                    "end": segment.get("end"),
                    "text": segment.get("text"),
                })

            output = {
                "text": result.get("text", ""),
                "language": result.get("language", language or Config.TTS_LANGUAGE),
                "segments": segments,
                "error": None,
            }

            self.logger.info(f"Transcription complete: {len(output['text'])} characters")
            return output

        except Exception as e:
            self.logger.error(f"Error transcribing audio: {str(e)}", exc_info=True)
            return {
                "text": "",
                "language": language or Config.TTS_LANGUAGE,
                "segments": [],
                "error": str(e),
            }

    def detect_language(self, audio_file: str) -> str:
        """
        Detect language of audio file.
        """
        if self.model is None:
            self.logger.warning("Whisper model not available for language detection")
            return Config.TTS_LANGUAGE

        try:
            self.logger.info(f"Detecting language for: {audio_file}")
            
            # Load audio
            import whisper as whisper_module
            audio = whisper_module.load_audio(audio_file)
            audio = whisper_module.pad_or_trim(audio)

            # Get mel spectrogram
            mel = whisper_module.log_mel_spectrogram(audio).to(self.model.device)

            # Detect language
            _, probs = self.model.detect_language(mel)
            detected_lang = max(probs, key=probs.get)

            self.logger.info(f"Detected language: {detected_lang}")
            return detected_lang

        except Exception as e:
            self.logger.error(f"Error detecting language: {str(e)}")
            return Config.TTS_LANGUAGE


class TTSProcessor:
    """Text-to-speech audio generation."""

    def __init__(self):
        self.logger = setup_logging("TTSProcessor")
        self.engine = Config.TTS_ENGINE

    def generate_speech(self, text: str, language: str, output_file: str) -> bool:
        """
        Generate speech audio from text.
        MVP implementation uses gTTS; can be extended with Azure, AWS, etc.
        """
        try:
            self.logger.info(f"Generating speech for {len(text)} characters")

            if self.engine == "gtts":
                return self._generate_with_gtts(text, language, output_file)
            else:
                self.logger.warning(f"TTS engine '{self.engine}' not implemented, using fallback")
                return self._generate_with_gtts(text, language, output_file)

        except Exception as e:
            self.logger.error(f"Error generating speech: {str(e)}", exc_info=True)
            return False

    def _generate_with_gtts(self, text: str, language: str, output_file: str) -> bool:
        """Generate speech using Google Text-to-Speech."""
        try:
            from gtts import gTTS
        except ImportError:
            self.logger.warning("gTTS not installed. Install with: pip install gtts")
            return False

        try:
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(output_file)
            self.logger.info(f"Speech generated: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error generating speech with gTTS: {str(e)}")
            return False


class WhisperWorkerService:
    """Service coordinator for audio processing tasks."""

    def __init__(self):
        self.logger = setup_logging("WhisperWorkerService")
        self.whisper_processor = WhisperProcessor()
        self.tts_processor = TTSProcessor()

    def process_audio_for_job(
        self, job_id: str, text: str, language: str
    ) -> Dict:
        """
        Process audio for a job: generate TTS and transcribe.
        """
        self.logger.info(f"Processing audio for job {job_id}")

        try:
            # Generate TTS
            audio_file = f"/tmp/{job_id}_narration.mp3"
            
            tts_success = self.tts_processor.generate_speech(text, language, audio_file)
            if not tts_success:
                self.logger.warning("TTS generation failed, continuing with text")

            # Transcribe (simulate perfect transcription of generated text)
            segments = self._create_word_level_segments(text)

            # Create audio segments and subtitles
            audio_segment = AudioSegment(
                text=text,
                audio_url=f"s3://audio/{job_id}/narration.mp3",
                duration=len(text) / 150 * 60,  # Rough estimate: 150 chars per minute
                language=language,
            )

            subtitles = self._create_subtitles(text, segments)

            result = {
                "job_id": job_id,
                "audio_segment": audio_segment.to_dict(),
                "subtitles": [s.to_dict() for s in subtitles],
                "language": language,
                "error": None,
            }

            log_job_event(job_id, "audio_processed", "COMPLETE")
            return result

        except Exception as e:
            self.logger.error(f"Error processing audio: {str(e)}", exc_info=True)
            log_job_event(job_id, "audio_processing_failed", "FAILED", {"error": str(e)})
            return {
                "job_id": job_id,
                "audio_segment": None,
                "subtitles": [],
                "language": language,
                "error": str(e),
            }

    def _create_word_level_segments(self, text: str) -> List[Dict]:
        """Create word-level segments for alignment."""
        words = text.split()
        segments = []
        
        # Rough timing: assume 150 words per minute = 0.4 seconds per word
        words_per_second = 150 / 60
        
        current_time = 0
        for word in words:
            word_duration = len(word) / (150 * 60) * words_per_second
            segments.append({
                "text": word,
                "start": current_time,
                "end": current_time + word_duration,
            })
            current_time += word_duration

        return segments

    def _create_subtitles(self, text: str, segments: List[Dict]) -> List[Subtitle]:
        """Create subtitle entries from segments."""
        subtitles = []
        
        # Group words into subtitle chunks (roughly 8 words per subtitle)
        chunk_size = 8
        words = text.split()
        
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i+chunk_size]
            chunk_text = " ".join(chunk_words)
            
            # Find timing for this chunk
            start_segment = min(i, len(segments) - 1)
            end_segment = min(i + chunk_size - 1, len(segments) - 1)
            
            if start_segment < len(segments) and end_segment < len(segments):
                start_ms = int(segments[start_segment]["start"] * 1000)
                end_ms = int(segments[end_segment]["end"] * 1000)
                
                subtitle = Subtitle(
                    text=chunk_text,
                    start_time=start_ms,
                    end_time=end_ms,
                )
                subtitles.append(subtitle)

        return subtitles


# Global service instance
_whisper_service = WhisperWorkerService()


def get_whisper_service() -> WhisperWorkerService:
    """Get global Whisper service instance."""
    return _whisper_service


if __name__ == "__main__":
    logger.info("Whisper worker service ready")
