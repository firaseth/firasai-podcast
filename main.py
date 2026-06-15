import schedule
import time
import os
import threading
import sys
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from config import Config
from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.scriptwriter import ScriptwriterAgent
from agents.editor import EditorAgent
from agents.marketer import MarketerAgent
from agents.analyst import AnalystAgent
from tools.notion_tool import NotionTool
from tools.audio_tool import AudioTool
from tools.db_tool import DbTool

# Web app imports
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
from contextlib import asynccontextmanager

# Initialize DB and Config
db = DbTool()
config_obj = Config()


class EpisodeRequest(BaseModel):
    topic: Optional[str] = None


class FirasAiAgent:
    def __init__(self):
        self.config = config_obj
        self.planner = PlannerAgent(self.config)
        self.researcher = ResearcherAgent(self.config)
        self.scriptwriter = ScriptwriterAgent(self.config)
        self.editor = EditorAgent(self.config)
        self.marketer = MarketerAgent(self.config)
        self.analyst = AnalystAgent(self.config)
        self.notion = NotionTool(self.config)
        self.audio = AudioTool(self.config)
        self.db = db
        print("🎙️ FirasAi Agent initialized")

    # ── Core pipeline ──────────────────────────────────────────────────────────

    def create_episode(self, topic: str | None = None) -> str:
        """Full episode creation pipeline: topic → research → script → Notion & local DB."""
        print("🎙️ Starting FirasAi episode creation...")
        self.db.log_event("create_episode_start", f"Topic: {topic or 'AI Suggestion'}")

        if not topic:
            topic_dict = self.planner.suggest_topic()
            topic = topic_dict.title if hasattr(topic_dict, "title") else topic_dict.get("title") or topic_dict.get("topic") or str(topic_dict)
            print(f"💡 Suggested topic: {topic}")

        research = self.researcher.research_topic(topic)
        print("🔍 Research complete")

        script = self.scriptwriter.write_script(topic, research)
        print(f"📝 Script written: {script['word_count']} words")

        # Save to Notion
        episode_id = ""
        try:
            episode_id = self.notion.create_episode({
                "title": script["title"],
                "status": "Scripted",
                "script": script["content"],
                "research": research.model_dump() if hasattr(research, "model_dump") else research,
                "show_notes": script["show_notes"],
            })
            print(f"💾 Saved to Notion: {episode_id}")
        except Exception as e:
            print(f"⚠️ Failed to save to Notion: {e}. Storing locally only.")
            episode_id = f"local_{int(time.time())}"

        # Save locally in SQLite cache (Pro-level enhancement!)
        research_data = research.model_dump() if hasattr(research, "model_dump") else research
        self.db.cache_episode(
            episode_id=episode_id,
            title=script["title"],
            topic=topic,
            status="Scripted",
            script=script["content"],
            research=research_data,
            show_notes=script["show_notes"]
        )

        # Generate Audio Voiceover & Background Music Mix (New Enhancement!)
        if self.config.ELEVENLABS_API_KEY and self.config.ELEVENLABS_API_KEY != "your_elevenlabs_api_key":
            try:
                print("🎙️ Generating audio voiceover via ElevenLabs...")
                # Generate audio for the first 2000 characters (Cold Open + Intro) to keep it lightweight & stay within API limits
                preview_text = script["content"][:2000]
                
                os.makedirs("data", exist_ok=True)
                voice_file = f"data/voice_{episode_id}.mp3"
                
                generated_voice = self.audio.generate_intro(preview_text, voice_file)
                if generated_voice:
                    print("🎵 Mixing background music onto voiceover track...")
                    music_file = "data/calm_music.mp3"
                    mixed_file = f"data/master_{episode_id}.mp3"
                    
                    final_master = self.audio.mix_voice_and_music(
                        voice_path=generated_voice,
                        music_path=music_file,
                        output_path=mixed_file
                    )
                    if final_master:
                        print(f"✅ Mixed audio master created successfully: {final_master}")
                        self.db.log_event("audio_generation_success", f"Audio master mixed: {final_master}")
            except Exception as e:
                print(f"⚠️ Audio generation or mixing failed: {e}")
                self.db.log_event("audio_generation_error", str(e))

        return episode_id

    # ── Scheduled workflows ────────────────────────────────────────────────────

    def run_weekly_workflow(self):
        """Automated weekly tasks: generate ideas, build report, queue newsletter."""
        print("📅 Running FirasAi weekly workflow...")
        self.db.log_event("weekly_workflow_start")

        ideas = self.planner.generate_weekly_ideas(count=5)
        ideas_list = ideas.ideas if hasattr(ideas, "ideas") else ideas.get("ideas", [])
        for idea in ideas_list:
            idea_dict = idea.model_dump() if hasattr(idea, "model_dump") else idea
            try:
                self.notion.create_episode_idea(idea_dict)
            except Exception as e:
                print(f"⚠️ Failed to save idea to Notion: {e}")

        report = self.analyst.generate_weekly_report()
        report_data = report.model_dump() if hasattr(report, "model_dump") else report
        
        try:
            self.notion.create_report(report_data)
        except Exception as e:
            print(f"⚠️ Failed to save report to Notion: {e}")

        # Cache locally
        self.db.cache_report(report_data)

        self.marketer.schedule_weekly_newsletter()
        print("✅ Weekly workflow complete")
        self.db.log_event("weekly_workflow_complete")

    def check_responses(self):
        """Check Notion for guest outreach responses and update statuses."""
        print("📧 Checking guest responses...")
        self.db.log_event("check_guest_responses")
        try:
            responses = self.notion.check_guest_responses()
            for response in responses.get("results", []):
                self.notion.update_guest_status(response)
        except Exception as e:
            print(f"⚠️ Guest check error: {e}")

    # ── Fail-Safe Scheduled Wrappers ───────────────────────────────────────────

    def safe_run_weekly_workflow(self):
        try:
            self.run_weekly_workflow()
        except Exception as e:
            print(f"❌ Error in weekly workflow: {e}")
            self.db.log_event("weekly_workflow_error", str(e))

    def safe_check_responses(self):
        try:
            self.check_responses()
        except Exception as e:
            print(f"❌ Error checking guest responses: {e}")
            self.db.log_event("guest_responses_error", str(e))

    def safe_schedule_weekly_newsletter(self):
        try:
            self.marketer.schedule_weekly_newsletter()
            print("✅ Weekly newsletter scheduling completed successfully.")
            self.db.log_event("newsletter_complete")
        except Exception as e:
            print(f"❌ Error scheduling weekly newsletter: {e}")
            self.db.log_event("newsletter_error", str(e))

    def safe_generate_weekly_report(self):
        try:
            report = self.analyst.generate_weekly_report()
            report_data = report.model_dump() if hasattr(report, "model_dump") else report
            
            try:
                self.notion.create_report(report_data)
            except Exception as e:
                print(f"⚠️ Notion save failed for report: {e}")

            self.db.cache_report(report_data)
            print("✅ Weekly report generated and saved to Notion.")
            self.db.log_event("weekly_report_complete")
        except Exception as e:
            print(f"❌ Error generating weekly report: {e}")
            self.db.log_event("weekly_report_error", str(e))

    # ── Scheduler Thread Daemon ───────────────────────────────────────────────

    def start_scheduler_loop(self):
        """Runs the background schedule loop forever."""
        print("🤖 Background scheduler daemon started")
        schedule.every().monday.at("09:00").do(self.safe_run_weekly_workflow)
        schedule.every().day.at("10:00").do(self.safe_check_responses)
        schedule.every().friday.at("17:00").do(
            self.safe_schedule_weekly_newsletter
        )
        schedule.every().sunday.at("20:00").do(
            self.safe_generate_weekly_report
        )

        while True:
            try:
                schedule.run_pending()
            except Exception as e:
                print(f"⚠️ Scheduler warning (will retry): {e}")
            time.sleep(60)


# Initialize global agent instance
agent = FirasAiAgent()


# ── Lifespan Manager (Removes deprecated on_event warning) ────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    if not os.environ.get("VERCEL") and not os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        print("⏰ Starting background scheduler thread...")
        daemon_thread = threading.Thread(target=agent.start_scheduler_loop, daemon=True)
        daemon_thread.start()
    else:
        print("☁️ Vercel Serverless environment detected. Disabling persistent background scheduler thread (use Vercel Cron/Webhooks instead).")
    yield
    # Shutdown actions (if any) would go here


# Define FastAPI Web Server using modern lifespan
app = FastAPI(
    title="🎙️ FirasAi Podcast Agent API",
    description="The live backend API, management dashboard data source, and web webhook triggers for your autonomous podcast.",
    version="1.1.0",
    lifespan=lifespan
)


# ── FastAPI Web Endpoints ───────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def read_root():
    """Main beautiful dashboard landing page for the podcast agent."""
    cached_episodes = db.get_cached_episodes(10)
    cached_reports = db.get_cached_reports(5)
    logs = db.get_logs(10)
    
    # Preloaded First Episode (simulation fallback if SQLite cache is empty)
    fallback_episode = {
        "title": "The Autonomous Wealth Wave — How AI is Rewriting Money and Markets",
        "topic": "Autonomous Wealth & Financial AI Agents",
        "status": "Published",
        "script": """[COLD OPEN]
(Sound effect: Digital synthesizer swell, transitioning into a steady, rhythmic electronic beat)

Firas: Imagine waking up tomorrow and checking your bank account, only to find that your personal AI agent negotiated your cellular bill down by forty percent, re-allocated your capital into three high-yielding DeFi pools, and bought a micro-share of a trending sports franchise... all while you were fast asleep. [PAUSE]

This isn't sci-fi. It’s happening right now in the corners of Web3 and algorithmic finance. The autonomous wealth wave is here, and it is completely rewriting how money, markets, and human leverage intersect.

[INTRO]
Firas: Welcome back to FirasAi — where AI meets money, markets, and the future. I’m your host, Firas, and today we are tearing down the wall between traditional finance and autonomous intelligence. [LAUGH]

For decades, Wall Street has kept the best algorithmic tools behind closed doors. But open-source models and decentralized APIs are putting institutional-grade power directly in the hands of everyday entrepreneurs, investors, and tech enthusiasts.

[MAIN CONTENT]
Firas: It’s not about using AI to pick stocks. It’s about building autonomous systems that generate capital, execute strategies, and compound on their own. Within three years, your AI will negotiate with a brand’s AI to buy products, book travel, or secure freelance contracts. The winning human is the one who designs the best instructions for their agent.

I'll see you in the future.""",
        "show_notes": '{"hook": "90% of Wall Street trades are executed by algorithms, but the next wave is personal: AI agents managing your portfolio, negotiated by AI, in real-time. Welcome to the future.", "takeaways": ["The shift from basic quantitative algorithms to cognitive, LLM-powered AI financial agents.", "How DeFi (Decentralized Finance) is merging with AI to create autonomous self-funding agents.", "The rise of AI-to-AI negotiations in real-time sports contracts, venture capital, and market liquidity."]}'
    }
    
    episodes_count = len(cached_episodes)
    reports_count = len(cached_reports)
    
    # Use fallback if database is empty
    if episodes_count == 0:
        display_episodes = [fallback_episode]
    else:
        display_episodes = []
        for ep in cached_episodes:
            try:
                # Sanitize loaded values
                show_notes = ep.get("show_notes", "{}")
                if isinstance(show_notes, str):
                    show_notes = json.loads(show_notes)
            except:
                show_notes = {"hook": "No overview hook available.", "takeaways": []}
            
            display_episodes.append({
                "title": ep.get("title"),
                "topic": ep.get("topic", "General Trends"),
                "status": ep.get("status", "Scripted"),
                "script": ep.get("script", ""),
                "show_notes": show_notes
            })

    # Render beautiful Tailwind UI
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en" class="h-full bg-slate-950 text-slate-100">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎙️ FirasAi Podcast — Autonomous Studio</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Plus Jakarta Sans', sans-serif;
            }}
            h1, h2, h3 {{
                font-family: 'Outfit', sans-serif;
            }}
        </style>
    </head>
    <body class="flex flex-col min-h-screen bg-slate-950 selection:bg-purple-500 selection:text-white">
        
        <!-- Header / Navigation -->
        <header class="border-b border-slate-800 bg-slate-900/50 backdrop-blur sticky top-0 z-50">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <span class="text-2xl">🎙️</span>
                    <span class="font-bold text-xl tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-500 to-red-500">
                        {config_obj.PODCAST_NAME}
                    </span>
                </div>
                <div class="flex items-center space-x-4">
                    <a href="/docs" target="_blank" class="text-sm font-semibold bg-purple-600/20 text-purple-300 border border-purple-500/30 px-3 py-1.5 rounded-lg hover:bg-purple-600/40 transition">
                        Interactive API (Swagger)
                    </a>
                    <span class="inline-flex items-center rounded-md bg-green-500/10 px-2 py-1 text-xs font-medium text-green-400 ring-1 ring-inset ring-green-500/20">
                        Agent Active
                    </span>
                </div>
            </div>
        </header>

        <!-- Main Workspace -->
        <main class="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
            
            <!-- Hero / Title with 3D Agent Render (PRO UPDATE!) -->
            <div class="relative bg-gradient-to-b from-purple-900/20 to-slate-950 border border-slate-800 rounded-3xl p-8 mb-10 overflow-hidden">
                <div class="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(147,51,234,0.15),transparent)]"></div>
                <div class="relative grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
                    <div class="md:col-span-2">
                        <span class="text-xs font-semibold tracking-wider text-purple-400 uppercase bg-purple-950/50 border border-purple-800/40 px-3 py-1 rounded-full">
                            Autonomous AI Media Studio
                        </span>
                        <h1 class="text-4xl sm:text-5xl font-extrabold text-white mt-4 tracking-tight leading-none">
                            Where AI Meets Money, Markets, <br class="hidden sm:inline">and the Future.
                        </h1>
                        <p class="mt-4 text-lg text-slate-400 font-light leading-relaxed">
                            I am your autonomous podcast host, <strong class="text-white">{config_obj.HOST_NAME}</strong>. I actively scan trends in <strong class="text-purple-300">{config_obj.NICHE}</strong>, draft structured research with Perplexity, write bold, rebellious scripts with GPT-4o, and update Notion—all on autopilot.
                        </p>
                    </div>
                    <div class="relative flex justify-center">
                        <div class="absolute inset-0 bg-gradient-to-tr from-purple-500/25 to-pink-500/25 blur-3xl rounded-full"></div>
                        <img src="/firasai_agent_3d.png" alt="FirasAI 3D Agent" class="relative max-h-60 rounded-2xl border border-slate-800 shadow-2xl object-cover hover:scale-105 transition duration-300">
                    </div>
                </div>
            </div>

            <!-- Split Grid: Main Content & Sidebar -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                
                <!-- Left: Interactive Controls & Latest Episode -->
                <div class="lg:col-span-2 space-y-8">
                    
                    <!-- Quick Actions -->
                    <div class="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                        <h2 class="text-xl font-bold text-white mb-4">⚡ Quick Actions & Pipeline Triggers</h2>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <button onclick="triggerEpisode()" class="flex flex-col items-start justify-between p-4 bg-gradient-to-r from-purple-900/30 to-purple-850/20 hover:from-purple-900/50 border border-purple-500/20 rounded-xl transition text-left group">
                                <span class="text-2xl mb-2">🤖</span>
                                <span class="font-semibold text-white group-hover:text-purple-300 transition">Draft Next Episode</span>
                                <span class="text-xs text-slate-400 mt-1">Triggers auto-planner and writes full research/script</span>
                            </button>
                            <button onclick="triggerWeekly()" class="flex flex-col items-start justify-between p-4 bg-slate-800/30 hover:bg-slate-800/50 border border-slate-700/30 rounded-xl transition text-left group">
                                <span class="text-2xl mb-2">📅</span>
                                <span class="font-semibold text-white group-hover:text-slate-300 transition">Trigger Weekly Planning</span>
                                <span class="text-xs text-slate-400 mt-1">Generates Notion queue, weekly analytics, and newsletter</span>
                            </button>
                        </div>
                        <div id="statusAlert" class="mt-4 p-3 rounded-lg hidden text-xs font-semibold"></div>
                    </div>

                    <!-- Featured/First Episode -->
                    <div class="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                        <div class="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
                            <h2 class="text-2xl font-extrabold text-white">🎙️ Latest Generated Episode</h2>
                            <span class="text-xs font-semibold bg-green-500/10 text-green-400 px-2 py-1 rounded border border-green-500/20 uppercase tracking-widest">
                                Ready to Record
                            </span>
                        </div>

                        <!-- Current Episode Details -->
                        <div class="space-y-6">
                            <div>
                                <span class="text-xs font-semibold text-purple-400 tracking-wider uppercase">
                                    Topic: {display_episodes[0]['topic']}
                                </span>
                                <h3 class="text-2xl font-bold text-white mt-1">
                                    {display_episodes[0]['title']}
                                </h3>
                                <p class="text-slate-400 text-sm mt-2 italic pl-4 border-l-2 border-purple-500">
                                    "{display_episodes[0]['show_notes'].get('hook') if isinstance(display_episodes[0]['show_notes'], dict) else 'Autonomous generation complete.'}"
                                </p>
                            </div>

                            <!-- Key Takeaways -->
                            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
                                <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Key Takeaways Covered:</h4>
                                <ul class="list-disc pl-5 space-y-1 text-xs text-slate-400">
                                    {"".join([f"<li>{item}</li>" for item in display_episodes[0]['show_notes'].get('takeaways', [])]) if isinstance(display_episodes[0]['show_notes'], dict) and display_episodes[0]['show_notes'].get('takeaways') else "<li>The latest market shifts.</li><li>Technology integrations.</li><li>Strategic action plans.</li>"}
                                </ul>
                            </div>

                            <!-- Script Accordion -->
                            <div>
                                <button onclick="toggleScript()" class="w-full flex items-center justify-between p-3 bg-slate-850/50 border border-slate-800 hover:bg-slate-800 rounded-lg transition text-xs font-semibold text-slate-200">
                                    <span>📄 Expand Full Episode Script ({len(display_episodes[0]['script'].split())} words)</span>
                                    <span id="scriptArrow">▼</span>
                                </button>
                                <div id="scriptContent" class="hidden mt-4 bg-slate-950 rounded-lg p-5 border border-slate-855 max-h-96 overflow-y-auto text-xs leading-relaxed text-slate-300 whitespace-pre-wrap font-mono">
                                    {display_episodes[0]['script']}
                                </div>
                            </div>

                        </div>
                    </div>

                </div>

                <!-- Right Sidebar: Stats & Logs -->
                <div class="space-y-8">
                    
                    <!-- Stats Panel -->
                    <div class="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                        <h2 class="text-lg font-bold text-white mb-4">📊 System Caches</h2>
                        <div class="grid grid-cols-2 gap-4">
                            <div class="bg-slate-950 p-4 rounded-xl border border-slate-850 text-center">
                                <span class="block text-3xl font-extrabold text-purple-400">{episodes_count}</span>
                                <span class="text-xs text-slate-400 mt-1 block">Episodes Cached</span>
                            </div>
                            <div class="bg-slate-950 p-4 rounded-xl border border-slate-850 text-center">
                                <span class="block text-3xl font-extrabold text-pink-400">{reports_count}</span>
                                <span class="text-xs text-slate-400 mt-1 block">Reports Cached</span>
                            </div>
                        </div>
                        <div class="mt-4 border-t border-slate-800/60 pt-4 space-y-2">
                            <div class="flex items-center justify-between text-xs text-slate-400">
                                <span>Core Intelligence:</span>
                                <span class="font-mono text-purple-300">gpt-4o</span>
                            </div>
                            <div class="flex items-center justify-between text-xs text-slate-400">
                                <span>Fast Model:</span>
                                <span class="font-mono text-purple-300">gpt-4o-mini</span>
                            </div>
                            <div class="flex items-center justify-between text-xs text-slate-400">
                                <span>Local Fallbacks:</span>
                                <span class="text-green-400">Ollama-Ready</span>
                            </div>
                        </div>
                    </div>

                    <!-- System Logs -->
                    <div class="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                        <h2 class="text-lg font-bold text-white mb-4">📋 Agent Action Log</h2>
                        <div class="space-y-3 max-h-80 overflow-y-auto">
                            {"".join([f'''
                            <div class="bg-slate-950 p-3 rounded-lg border border-slate-850 text-xs">
                                <div class="flex items-center justify-between mb-1">
                                    <span class="font-semibold text-purple-400 uppercase tracking-widest text-[10px]">{log.get('event')}</span>
                                    <span class="text-[10px] text-slate-500 font-mono">{log.get('created_at')}</span>
                                </div>
                                <p class="text-slate-400 font-light">{log.get('details') or ''}</p>
                            </div>
                            ''' for log in logs]) if logs else '''
                            <div class="text-center py-6 text-slate-500 text-xs italic">
                                No logged events yet. Trigger an action above!
                            </div>
                            '''}
                        </div>
                    </div>

                </div>

            </div>

        </main>

        <!-- Footer -->
        <footer class="bg-slate-950 border-t border-slate-900 py-6 mt-12">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-xs text-slate-500">
                <p>{config_obj.PODCAST_NAME} Podcast Studio. Autonomous Agent Running on Vercel Serverless.</p>
                <p class="mt-1">"I'll see you in the future."</p>
            </div>
        </footer>

        <!-- Javascript Operations -->
        <script>
            function toggleScript() {{
                const content = document.getElementById("scriptContent");
                const arrow = document.getElementById("scriptArrow");
                if (content.classList.contains("hidden")) {{
                    content.classList.remove("hidden");
                    arrow.innerText = "▲";
                }} else {{
                    content.classList.add("hidden");
                    arrow.innerText = "▼";
                }}
            }}

            async function triggerEpisode() {{
                showNotification("🤖 Instructing agent to draft new episode...", "bg-purple-600/20 text-purple-300 border border-purple-500/30");
                try {{
                    const res = await fetch("/episode", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{ topic: null }})
                    }});
                    const data = await res.json();
                    showNotification("✅ Generation pipeline started successfully! It will save to Notion & your local database shortly. Refresh in a moment.", "bg-green-500/10 text-green-400 border border-green-500/20");
                }} catch (e) {{
                    showNotification("❌ Error triggering agent: " + e, "bg-red-500/10 text-red-400 border border-red-500/20");
                }}
            }}

            async function triggerWeekly() {{
                showNotification("📅 Starting weekly planning and newsletter workflow...", "bg-slate-800/30 text-slate-300 border border-slate-700/30");
                try {{
                    const res = await fetch("/weekly-workflow", {{ method: "POST" }});
                    const data = await res.json();
                    showNotification("✅ Weekly workflow completed & saved to Notion/Local cache!", "bg-green-500/10 text-green-400 border border-green-500/20");
                }} catch (e) {{
                    showNotification("❌ Error: " + e, "bg-red-500/10 text-red-400 border border-red-500/20");
                }}
            }}

            function showNotification(msg, styleClass) {{
                const alert = document.getElementById("statusAlert");
                alert.className = "mt-4 p-3 rounded-lg text-xs font-semibold " + styleClass;
                alert.innerText = msg;
                alert.classList.remove("hidden");
            }}
        </script>

    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/firasai_agent_3d.png")
def get_agent_image():
    """Endpoint to serve the generated 3D AI Agent artwork dynamically on your webpage."""
    return FileResponse("firasai_agent_3d.png")

@app.get("/episodes")
def get_episodes(limit: int = 10):
    """Retrieve locally cached generated episodes."""
    return db.get_cached_episodes(limit=limit)

@app.get("/reports")
def get_reports(limit: int = 5):
    """Retrieve locally cached weekly analytics reports."""
    return db.get_cached_reports(limit=limit)

@app.get("/logs")
def get_logs(limit: int = 20):
    """Retrieve agent action logs."""
    return db.get_logs(limit=limit)

@app.post("/episode")
def create_episode_endpoint(request: EpisodeRequest, background_tasks: BackgroundTasks):
    """Trigger the full episode creation pipeline in the background on-demand."""
    background_tasks.add_task(agent.create_episode, request.topic)
    return {"message": "Episode generation pipeline started in background", "topic": request.topic or "Auto-Suggest"}

@app.post("/weekly-workflow")
def trigger_weekly_workflow(background_tasks: BackgroundTasks):
    """Trigger the weekly planning and metrics workflow in the background."""
    background_tasks.add_task(agent.run_weekly_workflow)
    return {"message": "Weekly planning workflow started in background"}

@app.post("/check-responses")
def trigger_check_responses(background_tasks: BackgroundTasks):
    """Trigger Notion guest response updates in the background."""
    background_tasks.add_task(agent.check_responses)
    return {"message": "Guest response pipeline started in background"}


# Startup background scheduler thread when running as API server
@app.on_event("startup")
def start_scheduler_on_startup():
    # Only start background thread if NOT on Vercel serverless environment
    if not os.environ.get("VERCEL") and not os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        print("⏰ Starting background scheduler thread...")
        daemon_thread = threading.Thread(target=agent.start_scheduler_loop, daemon=True)
        daemon_thread.start()
    else:
        print("☁️ Vercel Serverless environment detected. Disabling persistent background scheduler thread (use Vercel Cron/Webhooks instead).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🎙️ FirasAi - Autonomous AI Podcast Agent")
    parser.add_argument(
        "--server",
        action="store_true",
        help="Run as a live FastAPI Web Server and Background Scheduler (recommended for production)"
    )
    parser.add_argument(
        "--create-episode",
        type=str,
        nargs="?",
        const="",
        help="Trigger the full episode creation pipeline on-demand. Optionally pass a specific topic."
    )
    parser.add_argument(
        "--weekly-workflow",
        action="store_true",
        help="Run the weekly workflow on-demand (generate ideas, weekly report, newsletter)"
    )
    parser.add_argument(
        "--check-responses",
        action="store_true",
        help="Check Notion for guest outreach responses on-demand"
    )

    args = parser.parse_args()

    # If no arguments or --server explicitly specified, run the FastAPI server + scheduler
    if len(sys.argv) == 1 or args.server:
        import uvicorn
        port = int(os.environ.get("PORT", 8080))
        print(f"🚀 Starting FirasAi Live Server on port {port}...")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # CLI direct trigger mode
        if args.create_episode is not None:
            topic = args.create_episode if args.create_episode != "" else None
            try:
                agent.create_episode(topic=topic)
            except Exception as e:
                print(f"❌ Error during manual episode creation: {e}")
        
        if args.weekly_workflow:
            try:
                agent.run_weekly_workflow()
            except Exception as e:
                print(f"❌ Error during manual weekly workflow: {e}")
                
        if args.check_responses:
            try:
                agent.check_responses()
            except Exception as e:
                print(f"❌ Error during manual guest response check: {e}")
