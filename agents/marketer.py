import json
from openai import OpenAI


class MarketerAgent:
    def __init__(self, config):
        self.config = config
        self.client = config.get_openai_client()

    def create_marketing_package(self, episode: dict) -> dict:
        """Create a full marketing package for a FirasAi episode."""
        return {
            "social_posts": self._create_social_posts(episode),
            "newsletter": self._create_newsletter(episode),
            "blog_post": self._create_blog_post(episode),
            "twitter_thread": self._create_twitter_thread(episode),
            "clip_scripts": self._create_clip_scripts(episode),
        }

    def schedule_weekly_newsletter(self):
        """Placeholder — integrate with Beehiiv API to schedule the newsletter."""
        # TODO: call Beehiiv POST /publications/{id}/posts with newsletter content
        pass

    # ── Private helpers ────────────────────────────────────────────────────────

    def _create_social_posts(self, episode: dict) -> dict:
        prompt = f"""
Create social media posts for this {self.config.PODCAST_NAME} episode.
Title: {episode.get('title', '')}
Generate: 3 Twitter/X posts, 2 LinkedIn posts, 2 Instagram captions.
Tone: {self.config.TONE}
Return JSON.
"""
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    def _create_newsletter(self, episode: dict) -> dict:
        prompt = f"""
Write a {self.config.PODCAST_NAME} email newsletter for this episode.
Title: {episode.get('title', '')}
Include: 3 subject line options, opening paragraph, 3-bullet episode summary, CTA.
Return JSON.
"""
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    def _create_blog_post(self, episode: dict) -> str:
        prompt = f"""
Convert this {self.config.PODCAST_NAME} episode into a 1,500-word SEO blog post.
Title: {episode.get('title', '')}
Structure: SEO title, meta description, H2 sections with pull quotes, conclusion, 3 FAQs.
Tone: conversational, match the podcast voice.
"""
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def _create_twitter_thread(self, episode: dict) -> dict:
        prompt = f"""
Create a 10-tweet thread for this {self.config.PODCAST_NAME} episode.
Title: {episode.get('title', '')}
Rules: Tweet 1 = strong hook. Tweets 2–9 = one insight each. Tweet 10 = recap + CTA.
Each tweet: under 280 chars, no clickbait, 1 emoji max.
Return JSON with a 'tweets' array.
"""
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    def _create_clip_scripts(self, episode: dict) -> dict:
        prompt = f"""
Find 5 moments in this {self.config.PODCAST_NAME} episode that would make great 60-second clips.
For each: timestamp, hook, script, caption, hashtags.
Return JSON with a 'clips' array.
Episode title: {episode.get('title', '')}
"""
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
