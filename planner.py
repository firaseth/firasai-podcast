import json
import requests
from openai import OpenAI


class PlannerAgent:
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def suggest_topic(self) -> dict:
        """Suggest a single trending FirasAi episode topic."""
        prompt = f"""
        Suggest one trending podcast episode topic for {self.config.PODCAST_NAME}.
        Niche: {self.config.NICHE}
        Audience: {self.config.TARGET_AUDIENCE}
        Tone: {self.config.TONE}
        Focus areas: AI tools/business, finance/markets, crypto/NFT, sports business.
        Return JSON with: title, hook, angle, talking_points (list), reason.
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    def generate_weekly_ideas(self, count: int = 5) -> dict:
        """Generate multiple episode ideas for the week."""
        prompt = f"""
        Generate {count} podcast episode ideas for {self.config.PODCAST_NAME}.
        Mix formats: 2 solo deep-dives, 1 interview, 1 reaction, 1 case study.
        Return JSON with an 'ideas' array. Each idea: title, hook, format, why_now.
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    def find_trending_topics(self) -> dict:
        """Use Perplexity to pull current trends across the niche."""
        headers = {
            "Authorization": f"Bearer {self.config.PERPLEXITY_API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"What are the top 10 trending topics in {self.config.NICHE} "
                        "right now? Include specific stories, viral moments, and emerging trends."
                    ),
                }
            ],
        }
        response = requests.post(
            "https://api.perplexity.ai/chat/completions", headers=headers, json=data
        )
        response.raise_for_status()
        return response.json()

    def create_content_calendar(self, weeks: int = 4) -> dict:
        """Create a multi-week content calendar."""
        prompt = f"""
        Create a {weeks}-week content calendar for {self.config.PODCAST_NAME}.
        Per week: 2 main episodes, 3 social clip topics, 1 newsletter, 1 community Q&A.
        Return as JSON.
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
