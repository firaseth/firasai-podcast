import json
from openai import OpenAI
from agents.schemas import ShowNotes, StructuredResearch

class ScriptwriterAgent:
    def __init__(self, config):
        self.config = config
        self.client = config.get_openai_client()

    def write_script(
        self,
        topic: str,
        research: StructuredResearch | dict,
        length: str = "30 minutes",
        format_type: str = "solo",
    ) -> dict:
        """Write a complete FirasAi podcast script with supporting assets."""
        # Convert research to dictionary if it's a Pydantic model
        research_dict = research
        if hasattr(research, "model_dump"):
            research_dict = research.model_dump()

        prompt = self._build_prompt(topic, research_dict, length, format_type)

        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are the world-class scriptwriter for {self.config.PODCAST_NAME}, "
                        f"a podcast for {self.config.TARGET_AUDIENCE} covering {self.config.NICHE}. "
                        f"Your scripts are bold, data-driven, and slightly rebellious. "
                        f"Tone: {self.config.TONE}."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )

        script_text = response.choices[0].message.content
        show_notes = self._generate_show_notes(script_text, topic)

        # Convert show_notes to dictionary if it is a Pydantic object
        show_notes_dict = show_notes
        if hasattr(show_notes, "model_dump"):
            show_notes_dict = show_notes.model_dump()

        return {
            "title": self._extract_title(script_text, topic),
            "content": script_text,
            "show_notes": show_notes_dict,
            "hooks": self._generate_hooks(topic),
            "quotes": self._extract_quotes(script_text),
            "word_count": len(script_text.split()),
        }

    # ── Private helpers ────────────────────────────────────────────────────────

    def _build_prompt(self, topic, research, length, format_type) -> str:
        return f"""
Write a {length} {format_type} podcast script for {self.config.PODCAST_NAME}.

TOPIC: {topic}
RESEARCH: {json.dumps(research)}

REQUIREMENTS:
- Host: {self.config.HOST_NAME}
- Natural, conversational style
- Include [PAUSE], [LAUGH], *emphasis* cues
- No filler words (um, uh, like)
- Opens with a hook (30 seconds)
- Ends with a clear CTA
- Sign off with: "{self.config.SIGN_OFF}"

STRUCTURE:
1. Cold open (30 sec) — shocking stat or story
2. Intro (2 min) — welcome, today's topic, why it matters
3. Main content (bulk of episode)
4. Recap and insights
5. CTA and tease next episode

Write the full script now.
"""

    def _generate_show_notes(self, script: str, topic: str) -> ShowNotes:
        prompt = f"""
Generate complete show notes for this {self.config.PODCAST_NAME} episode.
Topic: {topic}
Script excerpt: {script[:3000]}...

You must return a JSON object with:
- title (str): Episode Title
- hook (str): 1-sentence episode hook/summary
- takeaways (list of str): 3-bullet key takeaways
- timestamps (list of str): List of chapters/timestamps in format "[05:12] Chapter Title"
- keywords (list of str): 5 highly relevant SEO keywords
"""
        api_key = self.config.OPENAI_API_KEY
        base_url = getattr(self.config, "OPENAI_BASE_URL", None) or ""
        is_ollama = api_key == "ollama" or "localhost" in base_url or "127.0.0.1" in base_url

        if not is_ollama:
            try:
                response = self.client.beta.chat.completions.parse(
                    model=self.config.PRIMARY_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    response_format=ShowNotes,
                )
                return response.choices[0].message.parsed
            except Exception as e:
                print(f"[ScriptwriterAgent] OpenAI parsing failed ({e}), falling back to standard JSON parsing...")

        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        return ShowNotes.model_validate(data)

    def _generate_hooks(self, topic: str) -> str:
        prompt = f"""
Generate 5 cold open hooks (30 seconds each) for a {self.config.PODCAST_NAME} episode on: {topic}
Mix: shocking stat, personal story, provocative question, contrarian take, surreal scenario.
Each should make the listener NEED to keep listening.
"""
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def _extract_quotes(self, script: str) -> dict:
        prompt = f"""
Extract 10 quotable lines from this {self.config.PODCAST_NAME} script.
Each: standalone, under 280 characters, insightful, tweetable.
Return JSON with a 'quotes' array.
Script: {script}
"""
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    def _extract_title(self, script: str, topic: str) -> str:
        return f"{self.config.PODCAST_NAME}: {topic}"
