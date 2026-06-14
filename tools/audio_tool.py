import requests
import os

class AudioTool:
    ELEVENLABS_BASE = "https://api.elevenlabs.io/v1"

    def __init__(self, config):
        self.config = config
        self.headers = {
            "xi-api-key": config.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }

    def generate_intro(self, text: str, output_path: str = "firasai_intro.mp3") -> str | None:
        """Generate a voice intro with ElevenLabs and save to disk."""
        url = f"{self.ELEVENLABS_BASE}/text-to-speech/{self.config.ELEVENLABS_VOICE_ID}"
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.75, "similarity_boost": 0.75},
        }
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path
        print(f"[AudioTool] ElevenLabs error {response.status_code}: {response.text}")
        return None

    def generate_ad_read(self, script: str, output_path: str = "firasai_ad.mp3") -> str | None:
        """Generate a sponsor ad read with ElevenLabs."""
        return self.generate_intro(script, output_path)

    def list_voices(self) -> list:
        """Return all available ElevenLabs voices."""
        response = requests.get(
            f"{self.ELEVENLABS_BASE}/voices",
            headers={"xi-api-key": self.config.ELEVENLABS_API_KEY},
        )
        response.raise_for_status()
        return response.json().get("voices", [])

    def mix_voice_and_music(self, voice_path: str, music_path: str, output_path: str = "final_podcast.mp3", music_volume_db: int = -22) -> str | None:
        """Overlays a background music track onto the generated voice track using pydub."""
        try:
            from pydub import AudioSegment
        except ImportError:
            print("[AudioTool] pydub is not installed. Skipping music mixing. Returning pure voiceover.")
            return voice_path

        try:
            # Check if voice file exists and is populated
            if not os.path.exists(voice_path) or os.path.getsize(voice_path) == 0:
                print(f"[AudioTool] Voice file {voice_path} is missing or empty.")
                return None

            # Load voiceover
            voice = AudioSegment.from_file(voice_path)

            # Load background music. If missing, look for default royalty free or download/mock
            if not os.path.exists(music_path):
                print(f"[AudioTool] Background music {music_path} not found. Returning pure voiceover.")
                return voice_path

            music = AudioSegment.from_file(music_path)

            # Loop music if it is shorter than the voice track
            if len(music) < len(voice):
                loops = (len(voice) // len(music)) + 1
                music = music * loops

            # Trim music to exact length of voiceover
            music = music[:len(voice)]

            # Lower music volume to sit nicely as background ambience
            music = music + music_volume_db

            # Overlay voice over the music (or vice versa)
            combined = music.overlay(voice)

            # Export combined audio
            combined.export(output_path, format="mp3")
            print(f"🎵 Successfully mixed background music! Saved final master to {output_path}")
            return output_path
        except Exception as e:
            print(f"[AudioTool] Error mixing audio: {e}. Returning pure voiceover instead.")
            return voice_path
