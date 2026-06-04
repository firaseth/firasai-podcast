import json
import requests
from openai import OpenAI


class ResearcherAgent:
    def __init__(self, config):
        self.config = config
        self.client = config.get_openai_client()

    def research_topic(self, topic: str) -> dict:
        """Deep research pipeline: Perplexity → structured output."""
        raw = self._perplexity_research(topic)
        return self._structure_research(topic, raw)

    def _perplexity_research(self, topic: str) -> dict:
        """Pull real-time data, stats, and quotes via Perplexity."""
        headers = {
            "Authorization": f"Bearer {self.config.PERPLEXITY_API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [
                {
                    "role": "user",
                    "content": f"""Research the topic: {topic}
Provide:
- 10 surprising statistics with sources
- 5 expert quotes
- 3 real-world examples
- 2 counter-arguments
- Timeline of how this topic has evolved
- Recent news (last 30 days)
- Common misconceptions
""",
                }
            ],
        }
        response = requests.post(
            "https://api.perplexity.ai/chat/completions", headers=headers, json=data
        )
        response.raise_for_status()
        return response.json()

    def _structure_research(self, topic: str, raw_data: dict) -> dict:
        """Transform raw Perplexity output into a clean, script-ready format."""
        prompt = f"""
        Structure this research into a clean format for a {self.config.PODCAST_NAME} podcast script.
        Topic: {topic}
        Raw Research: {json.dumps(raw_data)}
        Return JSON with: stats (list), quotes (list), examples (list), key_takeaways (list).
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    def fact_check(self, script: str) -> str:
        """Fact-check a script and return corrected version with sources."""
        prompt = f"""
        Fact-check this {self.config.PODCAST_NAME} podcast script. Flag any:
        - Outdated claims
        - Missing context
        - Misleading statistics
        - Unverifiable statements

        For each issue, provide the corrected version with a credible source.
        Script: {script}
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
