import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── API Keys ──────────────────────────────────────────────────────────────
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    NOTION_API_KEY = os.getenv("NOTION_API_KEY")
    BUZZSPROUT_API_KEY = os.getenv("BUZZSPROUT_API_KEY")
    BUZZSPROUT_PODCAST_ID = os.getenv("BUZZSPROUT_PODCAST_ID")
    BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")
    BEEHIIV_API_KEY = os.getenv("BEEHIIV_API_KEY")
    BEEHIIV_PUBLICATION_ID = os.getenv("BEEHIIV_PUBLICATION_ID")
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

    # ── Podcast Identity ──────────────────────────────────────────────────────
    PODCAST_NAME = "FirasAi"
    HOST_NAME = "Firas"
    NICHE = "AI, Business, Finance, Crypto, NFT, Sports"
    TARGET_AUDIENCE = "Entrepreneurs, investors, and tech enthusiasts"
    TONE = "bold, insightful, data-driven, slightly rebellious, accessible"
    TAGLINE = "Where AI Meets Money, Markets, and the Future"
    SIGN_OFF = "I'll see you in the future."

    # ── Voice ─────────────────────────────────────────────────────────────────
    ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "your_cloned_voice_id")

    # ── Notion Database IDs ───────────────────────────────────────────────────
    NOTION_EPISODES_DB = os.getenv("NOTION_EPISODES_DB")
    NOTION_GUESTS_DB = os.getenv("NOTION_GUESTS_DB")
    NOTION_CALENDAR_DB = os.getenv("NOTION_CALENDAR_DB")
    NOTION_CLIPS_DB = os.getenv("NOTION_CLIPS_DB")

    # ── Models ────────────────────────────────────────────────────────────────
    PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "gpt-4")
    FAST_MODEL = os.getenv("FAST_MODEL", "gpt-3.5-turbo")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229")

    def get_openai_client(self):
        from openai import OpenAI
        
        api_key = self.OPENAI_API_KEY
        base_url = os.getenv("OPENAI_BASE_URL")
        
        if api_key == "ollama" or (base_url and "localhost" in base_url):
            return OpenAI(
                base_url=base_url or "http://localhost:11434/v1",
                api_key=api_key or "ollama"
            )
        
        return OpenAI(api_key=api_key or "dummy_key_for_initialization")

