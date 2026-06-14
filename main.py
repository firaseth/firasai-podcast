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
from pydantic import BaseModel
from typing import Optional

# Initialize DB and Config
db = DbTool()
config_obj = Config()

# Define FastAPI Web Server
app = FastAPI(
    title="🎙️ FirasAi Podcast Agent API",
    description="The live backend API, management dashboard data source, and web webhook triggers for your autonomous podcast.",
    version="1.1.0"
)

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


# ── FastAPI Web Endpoints ───────────────────────────────────────────────────

@app.get("/")
def read_root():
    """Main health status dashboard endpoint."""
    return {
        "status": "healthy",
        "agent": "FirasAi",
        "podcast_name": config_obj.PODCAST_NAME,
        "niche": config_obj.NICHE,
        "sqlite_cached_episodes": len(db.get_cached_episodes(100)),
        "sqlite_cached_reports": len(db.get_cached_reports(100)),
        "current_time": time.strftime("%Y-%m-%d %H:%M:%S")
    }

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
    daemon_thread = threading.Thread(target=agent.start_scheduler_loop, daemon=True)
    daemon_thread.start()


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
