import json
import requests
from openai import OpenAI


class AnalystAgent:
    def __init__(self, config):
        self.config = config
        self.client = config.get_openai_client()

    def generate_weekly_report(self) -> dict:
        """Pull stats from all platforms and return AI-analysed weekly report."""
        podcast_data = self._get_buzzsprout_stats()
        social_data = self._get_social_stats()
        newsletter_data = self._get_newsletter_stats()
        return self._analyze_data(podcast_data, social_data, newsletter_data)

    # ── Data fetchers ──────────────────────────────────────────────────────────

    def _get_buzzsprout_stats(self) -> dict:
        headers = {"Authorization": f"Token token={self.config.BUZZSPROUT_API_KEY}"}
        response = requests.get(
            f"https://api.buzzsprout.com/v2/podcasts/{self.config.BUZZSPROUT_PODCAST_ID}/episodes",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    def _get_social_stats(self) -> dict:
        headers = {"Authorization": f"Bearer {self.config.BUFFER_ACCESS_TOKEN}"}
        response = requests.get(
            "https://api.bufferapp.com/1/analytics/profiles",
            headers=headers,
        )
        # Buffer analytics may return 404 on free tier — handle gracefully
        if response.ok:
            return response.json()
        return {}

    def _get_newsletter_stats(self) -> dict:
        headers = {"Authorization": f"Bearer {self.config.BEEHIIV_API_KEY}"}
        response = requests.get(
            f"https://api.beehiiv.com/v2/publications/{self.config.BEEHIIV_PUBLICATION_ID}/stats",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    # ── Analysis ───────────────────────────────────────────────────────────────

    def _analyze_data(self, podcast: dict, social: dict, newsletter: dict) -> dict:
        prompt = f"""
Analyze this week's {self.config.PODCAST_NAME} performance data:

Podcast (Buzzsprout): {json.dumps(podcast)[:2000]}
Social (Buffer): {json.dumps(social)[:1000]}
Newsletter (Beehiiv): {json.dumps(newsletter)[:1000]}

Return JSON with:
- wins (3 items)
- improvements (3 items)
- experiments (3 to try next week)
- predicted_next_week_performance
- action_items (prioritised list)
"""
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
