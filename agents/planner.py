import json
import requests
from openai import OpenAI
from agents.schemas import TopicSuggestion, WeeklyIdeas

class PlannerAgent:
    def __init__(self, config):
        self.config = config
        self.client = config.get_openai_client()

    def _get_structured_completion(self, prompt: str, schema_class):
        """Helper to get a structured model completion, with robust fallback for local models/Ollama."""
        api_key = self.config.OPENAI_API_KEY
        base_url = getattr(self.config, "OPENAI_BASE_URL", None) or ""
        
        is_ollama = api_key == "ollama" or "localhost" in base_url or "127.0.0.1" in base_url
        
        if not is_ollama:
            try:
                # Use OpenAI's robust native Beta Structured Outputs
                response = self.client.beta.chat.completions.parse(
                    model=self.config.PRIMARY_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    response_format=schema_class,
                )
                return response.choices[0].message.parsed
            except Exception as e:
                print(f"[PlannerAgent] OpenAI parsing failed ({e}), falling back to standard JSON parsing...")
        
        # Fallback for Ollama / local LLMs
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        return schema_class.model_validate(data)

    def suggest_topic(self) -> TopicSuggestion:
        """Suggest a single trending FirasAi episode topic."""
        prompt = f"""
        Suggest one trending podcast episode topic for {self.config.PODCAST_NAME}.
        Niche: {self.config.NICHE}
        Audience: {self.config.TARGET_AUDIENCE}
        Tone: {self.config.TONE}
        Focus areas: AI tools/business, finance/markets, crypto/NFT, sports business.
        
        You must return a JSON object with the following fields:
        - title (str): trending podcast title
        - hook (str): strong cold open hook
        - angle (str): unique angle
        - talking_points (list of str): 3-5 key points
        - reason (str): why it's trending or valuable right now
        """
        parsed = self._get_structured_completion(prompt, TopicSuggestion)
        return parsed

    def generate_weekly_ideas(self, count: int = 5) -> WeeklyIdeas:
        """Generate multiple episode ideas for the week."""
        prompt = f"""
        Generate {count} podcast episode ideas for {self.config.PODCAST_NAME}.
        Mix formats: 2 solo deep-dives, 1 interview, 1 reaction, 1 case study.
        
        You must return a JSON object with an 'ideas' array. Each item in the array must contain:
        - title (str)
        - hook (str)
        - format (str)
        - why_now (str)
        """
        parsed = self._get_structured_completion(prompt, WeeklyIdeas)
        return parsed

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
