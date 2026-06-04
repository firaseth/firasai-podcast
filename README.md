# 🎙️ FirasAi Podcast — AI-Powered Media Business Blueprint

> *Where AI Meets Money, Markets, and the Future*

A complete, production-ready system for launching and running an **autonomous AI-powered podcast business** — covering AI, business, finance, crypto, NFTs, and sports.

---

## 🗂️ Repository Structure

```
firasai-podcast/
├── 01-Overview-Stack-Build.md     # Sections 1–3: Overview, tech stack & 12-phase build guide
├── 02-Prompts-Library.md          # Section 4: 40+ ready-to-use AI prompts
├── 03-Notion-Template.md          # Section 5: Full Notion workspace setup
├── 04-Make-Blueprints.md          # Section 6: Make.com automation blueprints
├── 05-AI-Agent-Code.md            # Section 7: Python agent reference (narrative)
├── FirasAi-Complete-Bundle.md     # Master bundle — all sections in one file
├── agent/                         # ✅ Runnable Python agent (source files)
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── planner.py
│   │   ├── researcher.py
│   │   ├── scriptwriter.py
│   │   ├── editor.py
│   │   ├── marketer.py
│   │   └── analyst.py
│   └── tools/
│       ├── __init__.py
│       ├── notion_tool.py
│       └── audio_tool.py
├── .gitignore
├── CONTRIBUTING.md
└── LICENSE
```

---

## 🚀 What You're Building

You're not just starting a podcast — you're building a **fully autonomous AI-powered media business** that runs on autopilot.

| Pillar | What AI Does |
|---|---|
| 📋 Planning | Suggests topics, builds content calendars, finds trending angles |
| 🔍 Research | Pulls live data, stats, quotes, and fact-checks scripts |
| ✍️ Scripting | Writes 30-min scripts, show notes, cold opens, and hooks |
| 🎙️ Production | Transcribes audio, removes filler words, finds viral clips |
| 📣 Marketing | Creates social posts, newsletters, blog posts, and threads |
| 📊 Analytics | Generates weekly performance reports and growth insights |

---

## 📚 Documentation Guide

| File | What's Inside |
|---|---|
| [01-Overview-Stack-Build.md](./01-Overview-Stack-Build.md) | Full tech stack with costs, 12-phase build guide |
| [02-Prompts-Library.md](./02-Prompts-Library.md) | 40+ prompts: planning, scripting, outreach, social, analytics |
| [03-Notion-Template.md](./03-Notion-Template.md) | Command center, episode DB, guest pipeline, content calendar |
| [04-Make-Blueprints.md](./04-Make-Blueprints.md) | Make.com automation blueprints for the full publish pipeline |
| [05-AI-Agent-Code.md](./05-AI-Agent-Code.md) | Annotated walkthrough of the Python agent architecture |
| [FirasAi-Complete-Bundle.md](./FirasAi-Complete-Bundle.md) | All sections merged — good for reading end-to-end |

---

## ⚡ Quick Start (Python Agent)

### 1. Clone the repo
```bash
git clone https://github.com/firaseth/firasai-podcast.git
cd firasai-podcast/agent
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

### 5. Run the agent
```bash
python main.py
```

---

## 🐳 Docker Setup

```bash
cd agent
docker-compose build
docker-compose up -d
docker-compose logs -f
```

---

## 🔑 Required API Keys

| Service | Purpose | Get It |
|---|---|---|
| OpenAI | GPT-4 scripting & planning | [platform.openai.com](https://platform.openai.com) |
| Anthropic | Claude for long-form writing | [console.anthropic.com](https://console.anthropic.com) |
| ElevenLabs | AI voice & cloning | [elevenlabs.io](https://elevenlabs.io) |
| Notion | Content database | [notion.so/my-integrations](https://notion.so/my-integrations) |
| Perplexity | Real-time research | [perplexity.ai](https://perplexity.ai) |
| Buzzsprout | Podcast hosting & analytics | [buzzsprout.com](https://buzzsprout.com) |
| Beehiiv | Newsletter platform | [beehiiv.com](https://beehiiv.com) |
| Buffer | Social scheduling | [buffer.com/developers](https://buffer.com/developers) |

---

## 💰 Monthly Cost Breakdown

| Tier | Monthly Cost | Best For |
|---|---|---|
| Starter | ~$135/mo | Getting started, validating the show |
| Pro | ~$250/mo | Growing to 10k+ downloads |
| Enterprise | ~$500/mo | Full automation, multiple shows |

---

## 🏗️ Tech Stack Overview

**Content & AI:** ChatGPT · Claude · Perplexity AI · Notion AI  
**Audio:** Riverside.fm · Descript · Adobe Podcast Enhance · Auphonic  
**Voice:** ElevenLabs · Play.ht  
**Distribution:** Buzzsprout · Transistor · Captivate  
**Repurposing:** Opus Clip · Headliner · Castmagic  
**Automation:** Make.com · n8n  
**Newsletter:** Beehiiv · Substack  

---

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on how to contribute prompts, agent improvements, or automation blueprints.

---

## 📄 License

MIT — free to use, modify, and distribute. See [LICENSE](./LICENSE).

---

## 👤 Author

**Firas** — [@firaseth](https://github.com/firaseth)

> *"I'll see you in the future."*
