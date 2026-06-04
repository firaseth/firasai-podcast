import json
from openai import OpenAI


class ScriptwriterAgent:
    def __init__(self, config):
        self.config = config
        self.client = config.get_openai_client()

    def write_script(
        self,
        topic: str,
        research: dict,
        length: str = "30 minutes",
        format_type: str = "solo",
    ) -> dict:
        """Write a complete FirasAi podcast script with supporting assets."""
        prompt = self._build_prompt(topic, research, length, format_type)

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

        return {
            "title": self._extract_title(script_text, topic),
            "content": script_text,
            "show_notes": self._generate_show_notes(script_text, topic),
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

    def _generate_show_notes(self, script: str, topic: str) -> dict:
        prompt = f"""
Generate complete show notes for this {self.config.PODCAST_NAME} episode.
Topic: {topic}
Script excerpt: {script[:3000]}...
Return JSON: title, hook (1 sentence), takeaways (3 bullets), timestamps (list), keywords (5).
"""
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

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
