import json
import requests
from openai import OpenAI
from agents.schemas import WeeklyReport

class AnalystAgent:
    def __init__(self, config):
        self.config = config
        self.client = config.get_openai_client()

    def generate_weekly_report(self) -> WeeklyReport:
        """Pull stats from all platforms and return AI-analysed weekly report."""
        podcast_data = self._get_buzzsprout_stats()
        social_data = self._get_social_stats()
        newsletter_data = self._get_newsletter_stats()
        return self._analyze_data(podcast_data, social_data, newsletter_data)

    # ── Data fetchers ──────────────────────────────────────────────────────────

    def _get_buzzsprout_stats(self) -> dict:
        headers = {"Authorization": f"Token token={self.config.BUZZSPROUT_API_KEY}"}
        try:
            response = requests.get(
                f"https://api.buzzsprout.com/v2/podcasts/{self.config.BUZZSPROUT_PODCAST_ID}/episodes",
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[AnalystAgent] Error getting Buzzsprout stats: {e}")
            return {}

    def _get_social_stats(self) -> dict:
        headers = {"Authorization": f"Bearer {self.config.BUFFER_ACCESS_TOKEN}"}
        try:
            response = requests.get(
                "https://api.bufferapp.com/1/analytics/profiles",
                headers=headers,
            )
            # Buffer analytics may return 404 on free tier — handle gracefully
            if response.ok:
                return response.json()
        except Exception as e:
            print(f"[AnalystAgent] Error getting Buffer stats: {e}")
        return {}

    def _get_newsletter_stats(self) -> dict:
        headers = {"Authorization": f"Bearer {self.config.BEEHIIV_API_KEY}"}
        try:
            response = requests.get(
                f"https://api.beehiiv.com/v2/publications/{self.config.BEEHIIV_PUBLICATION_ID}/stats",
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[AnalystAgent] Error getting Beehiiv stats: {e}")
            return {}

    # ── Analysis ───────────────────────────────────────────────────────────────

    def _analyze_data(self, podcast: dict, social: dict, newsletter: dict) -> WeeklyReport:
        prompt = f"""
Analyze this week's {self.config.PODCAST_NAME} performance data:

Podcast (Buzzsprout): {json.dumps(podcast)[:2000]}
Social (Buffer): {json.dumps(social)[:1000]}
Newsletter (Beehiiv): {json.dumps(newsletter)[:1000]}

You must return a JSON object with:
- wins (list of 3 items): performance wins or milestones from this week
- improvements (list of 3 items): areas or metrics that need improvement
- experiments (list of 3 items): new experiments to try next week
- predicted_next_week_performance (str): narrative forecasting of next week's performance
- action_items (list of str): prioritized list of actionable next steps
"""
        api_key = self.config.OPENAI_API_KEY
        base_url = getattr(self.config, "OPENAI_BASE_URL", None) or ""
        is_ollama = api_key == "ollama" or "localhost" in base_url or "127.0.0.1" in base_url

        if not is_ollama:
            try:
                response = self.client.beta.chat.completions.parse(
                    model=self.config.PRIMARY_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    response_format=WeeklyReport,
                )
                return response.choices[0].message.parsed
            except Exception as e:
                print(f"[AnalystAgent] OpenAI parsing failed ({e}), falling back to standard JSON parsing...")

        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        return WeeklyReport.model_validate(data)
