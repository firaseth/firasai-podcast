import json
import requests
from openai import OpenAI


class EditorAgent:
    def __init__(self, config):
        self.config = config
        self.client = config.get_openai_client()

    def find_viral_moments(self, transcript: str) -> dict:
        """Analyze a transcript and surface the 10 best short-form clip moments."""
        prompt = f"""
Analyze this {self.config.PODCAST_NAME} podcast transcript and find 10 moments perfect for short-form clips (30–90 seconds).

For each moment, provide:
- start_time, end_time
- transcript snippet
- virality_score (1–10)
- why_it_works
- suggested_hook
- best_platform (TikTok / Reels / YouTube Shorts / Twitter)

Transcript: {transcript}
Return as JSON with a 'moments' array.
"""
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    def remove_filler(self, transcript: str) -> str:
        """Strip filler words while keeping the text natural."""
        prompt = f"""
Remove all filler words (um, uh, like, you know, sort of, basically) from this transcript.
Keep it sounding natural and conversational.
Transcript: {transcript}
"""
        response = self.client.chat.completions.create(
            model=self.config.FAST_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def generate_chapters(self, transcript: str, duration: int) -> str:
        """Generate timestamped chapter markers."""
        prompt = f"""
Create timestamped chapters for this {self.config.PODCAST_NAME} transcript.
Episode duration: {duration} minutes
Format: [MM:SS] Chapter title
Aim for 4–7 chapters.
Transcript: {transcript}
"""
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def transcribe_audio(self, audio_url: str):
        """Download audio and transcribe with Whisper. Returns verbose JSON."""
        import tempfile
        import os
        audio_bytes = requests.get(audio_url).content
        tmp_path = os.path.join(tempfile.gettempdir(), "firasai_audio.mp3")
        with open(tmp_path, "wb") as f:
            f.write(audio_bytes)

        with open(tmp_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )
        return transcript
