# 🎙 ️ FirasAi Complete Bundle — Part 5
## Section 7: AI Agent Code (Python)

This file contains all the Python code for the FirasAi AI agent. Each section is a separate file you'll create in your project folder.

---

## File 1: config.py

**Location:** `agent/config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # API Keys
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

    # FirasAi Podcast Info
    PODCAST_NAME = "FirasAi"
    HOST_NAME = "Firas"
    NICHE = "AI, Business, Finance, Crypto, NFT, Sports"
    TARGET_AUDIENCE = "Entrepreneurs, investors, and tech enthusiasts"
    TONE = "bold, insightful, data-driven, slightly rebellious, accessible"
    TAGLINE = "Where AI Meets Money, Markets, and the Future"

    # Voice IDs
    ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "your_cloned_voice_id")

    # Database IDs
    NOTION_EPISODES_DB = os.getenv("NOTION_EPISODES_DB")
    NOTION_GUESTS_DB = os.getenv("NOTION_GUESTS_DB")
    NOTION_CALENDAR_DB = os.getenv("NOTION_CALENDAR_DB")
    NOTION_CLIPS_DB = os.getenv("NOTION_CLIPS_DB")

    # Models
    PRIMARY_MODEL = "gpt-4"
    FAST_MODEL = "gpt-3.5-turbo"
    CLAUDE_MODEL = "claude-3-opus-20240229"
```

---

## File 2: main.py

**Location:** `agent/main.py`

```python
import schedule
import time
from config import Config
from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.scriptwriter import ScriptwriterAgent
from agents.editor import EditorAgent
from agents.marketer import MarketerAgent
from agents.analyst import AnalystAgent
from tools.notion_tool import NotionTool
from tools.audio_tool import AudioTool


class FirasAiAgent:
    def __init__(self):
        self.config = Config()
        self.planner = PlannerAgent(self.config)
        self.researcher = ResearcherAgent(self.config)
        self.scriptwriter = ScriptwriterAgent(self.config)
        self.editor = EditorAgent(self.config)
        self.marketer = MarketerAgent(self.config)
        self.analyst = AnalystAgent(self.config)
        self.notion = NotionTool(self.config)
        self.audio = AudioTool(self.config)
        print("🎙 ️ FirasAi Agent initialized")

    def create_episode(self, topic=None):
        """Full episode creation pipeline"""
        print("🎙 ️ Starting FirasAi episode creation...")

        if not topic:
            topic = self.planner.suggest_topic()
            print(f"💡 Suggested topic: {topic}")

        research = self.researcher.research_topic(topic)
        print(f"🔍 Research complete")

        script = self.scriptwriter.write_script(topic, research)
        print(f"📝 Script written: {script['word_count']} words")

        episode_id = self.notion.create_episode({
            "title": script["title"],
            "status": "Scripted",
            "script": script["content"],
            "research": research,
            "show_notes": script["show_notes"]
        })
        print(f"💾 Saved to Notion: {episode_id}")

        return episode_id

    def run_weekly_workflow(self):
        """Automated weekly tasks"""
        print("📅 Running FirasAi weekly workflow...")

        ideas = self.planner.generate_weekly_ideas(count=5)
        for idea in ideas.get("ideas", []):
            self.notion.create_episode_idea(idea)

        report = self.analyst.generate_weekly_report()
        self.notion.create_report(report)

        self.marketer.schedule_weekly_newsletter()

        print("✅ Weekly workflow complete")

    def check_responses(self):
        """Check for guest responses"""
        print("📧 Checking guest responses...")
        responses = self.notion.check_guest_responses()
        for response in responses.get("results", []):
            self.notion.update_guest_status(response)

    def start(self):
        """Start the agent with scheduled tasks"""
        print("🤖 FirasAi Agent Started")

        schedule.every().monday.at("09:00").do(self.run_weekly_workflow)
        schedule.every().day.at("10:00").do(self.check_responses)
        schedule.every().friday.at("17:00").do(self.marketer.schedule_weekly_newsletter)
        schedule.every().sunday.at("20:00").do(self.analyst.generate_weekly_report)

        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    agent = FirasAiAgent()
    agent.start()
```

---

## File 3: agents/planner.py

**Location:** `agent/agents/planner.py`

```python
import json
import requests
from openai import OpenAI


class PlannerAgent:
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def suggest_topic(self):
        """Suggest a single FirasAi episode topic"""
        prompt = f"""
        Suggest one trending podcast episode topic for {self.config.PODCAST_NAME}.
        Niche: {self.config.NICHE}
        Audience: {self.config.TARGET_AUDIENCE}
        Tone: {self.config.TONE}
        Focus areas: AI tools/business, finance/markets, crypto/NFT, sports business.
        Return JSON with title, hook, angle, talking_points, reason.
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def generate_weekly_ideas(self, count=5):
        """Generate multiple episode ideas for the week"""
        prompt = f"""
        Generate {count} podcast episode ideas for {self.config.PODCAST_NAME}.
        Mix formats: 2 solo deep-dives, 1 interview, 1 reaction, 1 case study.
        Return JSON with ideas array.
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def find_trending_topics(self):
        """Use Perplexity to find current trends"""
        headers = {
            "Authorization": f"Bearer {self.config.PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [{
                "role": "user",
                "content": f"What are the top 10 trending topics in {self.config.NICHE} right now? Include specific stories, viral moments, and emerging trends."
            }]
        }
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=data
        )
        return response.json()

    def create_content_calendar(self, weeks=4):
        """Create a multi-week content calendar"""
        prompt = f"""
        Create a {weeks}-week content calendar for {self.config.PODCAST_NAME}.
        Include: 2 episodes per week, 3 social posts per week, 1 newsletter per week.
        Return as JSON.
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
```

---

## File 4: agents/researcher.py

**Location:** `agent/agents/researcher.py`

```python
import json
import requests
from openai import OpenAI


class ResearcherAgent:
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def research_topic(self, topic):
        """Deep research on a topic"""
        perplexity_data = self._perplexity_research(topic)
        structured = self._structure_research(topic, perplexity_data)
        return structured

    def _perplexity_research(self, topic):
        """Get real-time data from Perplexity"""
        headers = {
            "Authorization": f"Bearer {self.config.PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [{
                "role": "user",
                "content": f"""Research the topic: {topic}
                Provide:
                - 10 surprising statistics with sources
                - 5 expert quotes
                - 3 real-world examples
                - 2 counter-arguments
                - Timeline of how this has evolved
                - Recent news (last 30 days)
                - Common misconceptions
                """
            }]
        }
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=data
        )
        return response.json()

    def _structure_research(self, topic, raw_data):
        """Structure research into usable format"""
        prompt = f"""
        Structure this research into a clean format for a FirasAi podcast script.
        Topic: {topic}
        Raw Research: {raw_data}
        Return JSON with stats, quotes, examples, key_takeaways.
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def fact_check(self, script):
        """Fact-check a script"""
        prompt = f"""
        Fact-check this FirasAi podcast script. Flag any:
        - Outdated claims
        - Missing context
        - Misleading statistics
        - Unverifiable statements

        For each issue, provide the corrected version with a credible source.
        Script: {script}
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
```

---

## File 5: agents/scriptwriter.py

**Location:** `agent/agents/scriptwriter.py`

```python
import json
from openai import OpenAI


class ScriptwriterAgent:
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def write_script(self, topic, research, length="30 minutes", format_type="solo"):
        """Write a complete FirasAi podcast script"""
        prompt = self._build_prompt(topic, research, length, format_type)

        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[
                {"role": "system", "content": f"You are the world-class scriptwriter for {self.config.PODCAST_NAME}, a podcast for {self.config.TARGET_AUDIENCE}
covering {self.config.NICHE}. Your scripts are bold, data-driven, and slightly rebellious. Tone: {self.config.TONE}."},
                {"role": "user", "content": prompt}
            ]
        )

        script_text = response.choices[0].message.content

        show_notes = self._generate_show_notes(script_text, topic)
        hooks = self._generate_hooks(topic)
        quotes = self._extract_quotes(script_text)

        return {
            "title": self._extract_title(script_text, topic),
            "content": script_text,
            "show_notes": show_notes,
            "hooks": hooks,
            "quotes": quotes,
            "word_count": len(script_text.split())
        }

    def _build_prompt(self, topic, research, length, format_type):
        return f"""
        Write a {length} {format_type} podcast script for {self.config.PODCAST_NAME}.
        TOPIC: {topic}
        RESEARCH: {research}
        REQUIREMENTS:
        - Host: {self.config.HOST_NAME}
        - Natural, conversational style
        - Include [PAUSE], [LAUGH], *emphasis* cues
        - No filler words (um, uh, like)
        - Opens with a hook (30 seconds)
        - Ends with a clear CTA
        - Sign off with: "I'll see you in the future."
        STRUCTURE:
        1. Cold open (30 sec) - shocking stat or story
        2. Intro (2 min) - welcome, today's topic, why it matters
        3. Main content (bulk of episode)
        4. Recap and insights
        5. CTA and tease next episode
        Write the full script now.
        """

    def _generate_show_notes(self, script, topic):
        prompt = f"""
        Generate complete show notes for this FirasAi episode.
        Topic: {topic}
        Script: {script[:3000]}...
        Include: Episode title, 1-sentence hook, 3-bullet takeaways, timestamps, 5 keywords.
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def _generate_hooks(self, topic):
        prompt = f"""
        Generate 5 cold open hooks (30 seconds each) for a FirasAi episode on: {topic}
        Mix types: shocking stat, personal story, provocative question, contrarian take, surreal scenario.
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def _extract_quotes(self, script):
        prompt = f"""
        Extract 10 quotable lines from this FirasAi script.
        Each should be: Standalone, Under 280 characters, Insightful, Tweetable.
        Script: {script}
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def _extract_title(self, script, topic):
        return f"FirasAi: {topic}"
```

---

## File 6: agents/marketer.py

**Location:** `agent/agents/marketer.py`

```python
import json
from openai import OpenAI


class MarketerAgent:
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def create_marketing_package(self, episode):
        """Create complete marketing package for FirasAi"""
        return {
            "social_posts": self._create_social_posts(episode),
            "newsletter": self._create_newsletter(episode),
            "blog_post": self._create_blog_post(episode),
            "thread": self._create_twitter_thread(episode),
            "clips_scripts": self._create_clip_scripts(episode)
        }

    def _create_social_posts(self, episode):
        prompt = f"""
        Create social media posts for this FirasAi episode.
        Title: {episode.get('title', '')}
        Generate 3 Twitter posts, 2 LinkedIn posts, 2 Instagram captions.
        Tone: {self.config.TONE}
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def _create_newsletter(self, episode):
        prompt = f"""
        Write a FirasAi newsletter for this episode.
        Title: {episode.get('title', '')}
        Include: 3 subject lines, opening, summary, CTA.
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def _create_blog_post(self, episode):
        prompt = f"""
        Convert this FirasAi podcast episode into a 1,500-word SEO blog post.
        Title: {episode.get('title', '')}
        Structure: SEO title, meta, H2 sections, pull quotes, conclusion, 3 FAQs.
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def _create_twitter_thread(self, episode):
        prompt = f"""
        Create a 10-tweet thread for FirasAi episode.
        Title: {episode.get('title', '')}
        Return JSON array of tweets.
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def _create_clip_scripts(self, episode):
        prompt = f"""
        Find 5 moments in this FirasAi script that would make great 60-second clips.
        For each: timestamp, hook, script, caption, hashtags.
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def schedule_weekly_newsletter(self):
        """Schedule this week's newsletter"""
        pass
```

---

## File 7: agents/editor.py

**Location:** `agent/agents/editor.py`

```python
import json
import requests
from openai import OpenAI


class EditorAgent:
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def find_viral_moments(self, transcript):
        """Analyze FirasAi transcript for viral moments"""
        prompt = f"""
        Analyze this FirasAi podcast transcript and find 10 moments perfect for short-form clips.
        For each: start_time, end_time, transcript, virality_score, why_it_works, suggested_hook, platform.
        Transcript: {transcript}
        Return as JSON array.
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def remove_filler(self, transcript):
        """Remove filler words from transcript"""
        prompt = f"""
        Remove all filler words from this FirasAi transcript.
        Make it sound natural.
        Transcript: {transcript}
        """
        response = self.client.chat.completions.create(
            model=self.config.FAST_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def generate_chapters(self, transcript, duration):
        """Generate timestamped chapters"""
        prompt = f"""
        Create timestamped chapters for this FirasAi transcript.
        Duration: {duration} minutes
        Format: [00:00] Chapter title
        Aim for 4-7 chapters.
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def transcribe_audio(self, audio_url):
        """Transcribe audio with Whisper"""
        audio_file = requests.get(audio_url)
        with open("/tmp/audio.mp3", "wb") as f:
            f.write(audio_file.content)
        with open("/tmp/audio.mp3", "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        return transcript
```

---

## File 8: agents/analyst.py

**Location:** `agent/agents/analyst.py`

```python
import json
import requests
from openai import OpenAI


class AnalystAgent:
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def generate_weekly_report(self):
        """Generate comprehensive weekly analytics report for FirasAi"""
        buzzsprout_data = self._get_buzzsprout_stats()
        social_data = self._get_social_stats()
        newsletter_data = self._get_newsletter_stats()
        analysis = self._analyze_data(buzzsprout_data, social_data, newsletter_data)
        return analysis

    def _get_buzzsprout_stats(self):
        headers = {"Authorization": f"Token token={self.config.BUZZSPROUT_API_KEY}"}
        response = requests.get(
            f"https://api.buzzsprout.com/v2/podcasts/{self.config.BUZZSPROUT_PODCAST_ID}/episodes",
            headers=headers
        )
        return response.json()

    def _get_social_stats(self):
        headers = {"Authorization": f"Bearer {self.config.BUFFER_ACCESS_TOKEN}"}
        response = requests.get(
            "https://api.bufferapp.com/1/analytics/profiles",
            headers=headers
        )
        return response.json()

    def _get_newsletter_stats(self):
        headers = {"Authorization": f"Bearer {self.config.BEEHIIV_API_KEY}"}
        response = requests.get(
            f"https://api.beehiiv.com/v2/publications/{self.config.BEEHIIV_PUBLICATION_ID}/stats",
            headers=headers
        )
        return response.json()

    def _analyze_data(self, podcast, social, newsletter):
        prompt = f"""
        Analyze this week's FirasAi podcast performance and provide insights.
        Provide: 3 wins, 3 improvements, 3 experiments, predicted performance, action items.
        Format as JSON.
        """
        response = self.client.chat.completions.create(
            model=self.config.PRIMARY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
```

---

## File 9: tools/notion_tool.py

**Location:** `agent/tools/notion_tool.py`

```python
import requests


class NotionTool:
    def __init__(self, config):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

    def create_episode(self, data):
        """Create FirasAi episode in Notion"""
        url = "https://api.notion.com/v1/pages"
        payload = {
            "parent": {"database_id": self.config.NOTION_EPISODES_DB},
            "properties": {
                "Title": {"title": [{"text": {"content": data["title"]}}]},
                "Status": {"select": {"name": data.get("status", "💡 Idea")}},
                "Script": {"rich_text": [{"text": {"content": data.get("script", "")[:2000]}}]}
            }
        }
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()

    def get_episode(self, episode_id):
        """Get episode by ID"""
        url = f"https://api.notion.com/v1/pages/{episode_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def update_episode(self, episode_id, data):
        """Update FirasAi episode"""
        url = f"https://api.notion.com/v1/pages/{episode_id}"
        properties = {}
        if "status" in data:
            properties["Status"] = {"select": {"name": data["status"]}}
        if "title" in data:
            properties["Title"] = {"title": [{"text": {"content": data["title"]}}]}
        payload = {"properties": properties}
        response = requests.patch(url, headers=self.headers, json=payload)
        return response.json()

    def create_episode_idea(self, idea):
        """Create FirasAi episode idea"""
        return self.create_episode({
            "title": idea.get("title", "Untitled"),
            "status": "💡 Idea"
        })

    def check_guest_responses(self):
        """Check for guest responses"""
        url = f"https://api.notion.com/v1/databases/{self.config.NOTION_GUESTS_DB}/query"
        response = requests.post(url, headers=self.headers)
        return response.json()

    def update_guest_status(self, guest):
        """Update guest status"""
        pass

    def create_report(self, report):
        """Create weekly report in Notion"""
        pass
```

---

## File 10: tools/audio_tool.py

**Location:** `agent/tools/audio_tool.py`

```python
import requests


class AudioTool:
    def __init__(self, config):
        self.config = config

    def generate_intro(self, text):
        """Generate FirasAi intro with ElevenLabs"""
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.config.ELEVENLABS_VOICE_ID}"
        headers = {
            "xi-api-key": self.config.ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75
            }
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            with open("firasai_intro.mp3", "wb") as f:
                f.write(response.content)
            return "firasai_intro.mp3"
        return None
```

---

## File 11: requirements.txt

**Location:** `agent/requirements.txt`

```txt
openai==1.12.0
anthropic==0.18.1
requests==2.31.0
python-dotenv==1.0.1
schedule==1.2.1
notion-client==2.0.0
elevenlabs==0.2.0
pydub==0.25.1
```

---

## File 12: .env.example

**Location:** `agent/.env.example`

```bash
# FirasAi Agent Environment Variables

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=...
NOTION_API_KEY=secret_...
BUZZSPROUT_API_KEY=...
BUZZSPROUT_PODCAST_ID=...
BUFFER_ACCESS_TOKEN=...
BEEHIIV_API_KEY=...
BEEHIIV_PUBLICATION_ID=...
PERPLEXITY_API_KEY=pplx-...
SLACK_WEBHOOK_URL=https://hooks.slack.com/...

# Voice
ELEVENLABS_VOICE_ID=voice_id_here

# Notion Database IDs
NOTION_EPISODES_DB=database_id_here
NOTION_GUESTS_DB=database_id_here
NOTION_CALENDAR_DB=database_id_here
NOTION_CLIPS_DB=database_id_here
```

---

## File 13: Dockerfile

**Location:** `agent/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

---

## File 14: docker-compose.yml

**Location:** `agent/docker-compose.yml`

```yaml
version: '3.8'
services:
  firasai-agent:
    build: .
    env_file: .env
    restart: unless-stopped
    volumes:
      - ./data:/app/data
```

---

## File 15: agents/__init__.py

**Location:** `agent/agents/__init__.py`

```python
# This file makes the agents directory a Python package
# Leave this file empty
```

---

## File 16: tools/__init__.py

**Location:** `agent/tools/__init__.py`

```python
# This file makes the tools directory a Python package
# Leave this file empty
```

---

## Setup Instructions

### Local Setup (Windows)

1. Install Python 3.11+ from python.org
2. Create project folder: C:\FirasAi\agent\
3. Create all the files above in the right structure
4. Open Command Prompt or PowerShell
5. Navigate to the agent folder: `cd C:\FirasAi\agent`
6. Create virtual environment: `python -m venv venv`
7. Activate it: `venv\Scripts\activate`
8. Install dependencies: `pip install -r requirements.txt`
9. Copy `.env.example` to `.env` and fill in your API keys
10. Run the agent: `python main.py`

### Docker Setup

1. Install Docker Desktop for Windows
2. Create all files in the agent folder
3. Update `.env` with your API keys
4. Open Command Prompt in the agent folder
5. Build: `docker-compose build`
6. Run: `docker-compose up -d`
7. Check logs: `docker-compose logs -f`

### GitHub Upload

1. Create new repo: github.com/firaseth/firasai-agent
2. Upload all these files maintaining the folder structure
3. Add a README explaining the project
4. Commit and push

---

## File Structure Summary

```
agent/
├── main.py
├── config.py
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── README.md
├── agents/
│   ├── __init__.py
│   ├── planner.py
│   ├── researcher.py
│   ├── scriptwriter.py
│   ├── editor.py
│   ├── marketer.py
│   └── analyst.py
└── tools/
    ├── __init__.py
    ├── notion_tool.py
    └── audio_tool.py
```

---

## Pro Tips

### Tip 1: Start Simple
Don't try to use every agent at once. Start with:
- Planner to generate ideas
- Scriptwriter to create content
- NotionTool to save episodes

### Tip 2: Test Each Component
Test each file individually before running the full system.

### Tip 3: Use Environment Variables
Never hardcode API keys. Always use .env file.

### Tip 4: Add Error Handling
Wrap API calls in try/except blocks to handle failures gracefully.

### Tip 5: Monitor Usage
Track your API usage to avoid surprise bills.

### Tip 6: Version Control
Use Git to track changes to your code.

---

## Next Steps After Setup

1. Get all API keys
2. Set up Notion databases
3. Test each agent individually
4. Run the full pipeline
5. Deploy to cloud (AWS, Google Cloud, or DigitalOcean)
6. Set up monitoring and alerts
7. Scale as your podcast grows
```