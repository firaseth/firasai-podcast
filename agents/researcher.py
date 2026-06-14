import json
import requests
from openai import OpenAI
from agents.schemas import StructuredResearch

class ResearcherAgent:
    def __init__(self, config):
        self.config = config
        self.client = config.get_openai_client()

    def research_topic(self, topic: str) -> StructuredResearch:
        """Deep research pipeline: Perplexity → structured output."""
        raw = self._perplexity_research(topic)
        return self._structure_research(topic, raw)

    def _perplexity_research(self, topic: str) -> dict:
        """Pull real-time data, stats, and quotes via Perplexity, with a robust OpenAI fallback."""
        api_key = self.config.PERPLEXITY_API_KEY
        
        # Check if the key is missing or set to the placeholder
        is_missing_key = (
            not api_key or 
            api_key == "database_id_here" or 
            api_key == "pplx-..." or 
            "perplexity" in api_key.lower() or 
            api_key.startswith("your_")
        )

        if is_missing_key:
            print("[ResearcherAgent] Perplexity API key not configured. Using OpenAI fallback for trend research.")
            return self._openai_research_fallback(topic)

        headers = {
            "Authorization": f"Bearer {api_key}",
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
        try:
            response = requests.post(
                "https://api.perplexity.ai/chat/completions", headers=headers, json=data, timeout=15
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[ResearcherAgent] Perplexity query failed ({e}). Falling back to OpenAI for research...")
            return self._openai_research_fallback(topic)

    def _openai_research_fallback(self, topic: str) -> dict:
        """Fallback to OpenAI to generate high-quality research if Perplexity is unavailable."""
        prompt = f"""
        Conduct deep-dive research on the topic: {topic}
        Provide highly realistic, up-to-date facts, estimates, statistics, and timelines.
        
        Include:
        - 10 surprising statistics with credible sources
        - 5 expert quotes
        - 3 real-world examples
        - 2 counter-arguments
        - Timeline of how this topic has evolved
        - Recent news
        - Common misconceptions
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        # Return structured in choices structure resembling Perplexity completions API
        return {"choices": [{"message": {"content": content}}]}

    def _structure_research(self, topic: str, raw_data: dict) -> StructuredResearch:
        """Transform raw Perplexity output into a clean, script-ready format."""
        # Extract text content from the API choices response
        raw_text = ""
        try:
            raw_text = raw_data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raw_text = str(raw_data)

        prompt = f"""
        Structure this research into a clean format for a {self.config.PODCAST_NAME} podcast script.
        Topic: {topic}
        Raw Research: {raw_text}
        
        You must return a JSON object with:
        - stats (list of str): surprising statistics with sources
        - quotes (list of str): expert quotes
        - examples (list of str): real-world examples
        - key_takeaways (list of str): core takeaways or insights
        """
        api_key = self.config.OPENAI_API_KEY
        base_url = getattr(self.config, "OPENAI_BASE_URL", None) or ""
        is_ollama = api_key == "ollama" or "localhost" in base_url or "127.0.0.1" in base_url

        if not is_ollama:
            try:
                response = self.client.beta.chat.completions.parse(
                    model=self.config.PRIMARY_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    response_format=StructuredResearch,
                )
                return response.choices[0].message.parsed
            except Exception as e:
                print(f"[ResearcherAgent] OpenAI parsing failed ({e}), falling back to standard JSON parsing...")

        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        return StructuredResearch.model_validate(data)

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
