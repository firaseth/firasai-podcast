import requests


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
